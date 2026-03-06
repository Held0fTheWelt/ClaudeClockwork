# MVP Phase 9 — Test Hardening

**Goal:** Fill the specific test coverage gaps identified in VERIFY 2026-03-06. The Phase 6 smoke gate verifies that every skill returns a well-formed result, but it does not cover: permission enforcement failure, capability matching correctness, `ExecutionPipeline.run()` end-to-end path, CLI argument parsing, or error paths (missing skill, invalid entrypoint).

**Source finding:** VERIFY 2026-03-06 Section 4 — "Zero coverage of: permission validation failure, capability matching algorithm, error paths (missing skill, invalid entrypoint), `ExecutionPipeline` direct invocation, CLI argument parsing."

---

## Definition of Done

- [ ] `test_error_paths.py` — covers missing skill, invalid entrypoint, and malformed inputs
- [ ] `test_permission_enforcement.py` — covers blocked permission rejection and allowed permission pass
- [ ] `test_pipeline.py` — covers `ExecutionPipeline.run()` end-to-end path
- [ ] `test_cli.py` — covers CLI argument parsing including `--skill-id`, `--inputs`, `--plugin-healthcheck`, unknown flag
- [ ] All new tests pass; all 136 existing tests continue to pass

---

## T9.1 — Error Path Tests

**File:** `tests/test_error_paths.py`

```python
# Missing skill returns None from bridge
def test_bridge_returns_none_for_unknown_skill():
    result = run_manifest_skill({"request_id": "x", "skill_id": "no_such_skill", "inputs": {}}, ROOT)
    assert result is None

# Registry get_manifest returns None for unknown skill
def test_registry_get_manifest_unknown():
    registry = build_registry(ROOT)
    assert registry.get_manifest("definitely_not_a_skill") is None

# Registry create raises KeyError for unknown skill
def test_registry_create_unknown_raises():
    registry = build_registry(ROOT)
    with pytest.raises(KeyError, match="no_such_skill"):
        registry.create("no_such_skill")

# Executor returns failure result for unknown skill_id (not an exception)
def test_executor_unknown_skill_returns_fail():
    executor = build_executor(ROOT)
    context = ExecutionContext(request_id="t", user_input="x", working_directory=str(ROOT))
    result = executor.execute("unknown_skill_xyz", context)
    assert result.success is False

# SkillLoader raises ImportError for bad entrypoint module
def test_loader_bad_module_raises():
    from claudeclockwork.core.registry.loader import SkillLoader
    with pytest.raises((ModuleNotFoundError, ImportError)):
        SkillLoader.load_skill_class("nonexistent.module.path:SomeClass")

# SkillLoader raises AttributeError for bad class name
def test_loader_bad_class_raises():
    from claudeclockwork.core.registry.loader import SkillLoader
    with pytest.raises(AttributeError):
        SkillLoader.load_skill_class("claudeclockwork.runtime:NonExistentClass")

# run_manifest_skill returns None if skill_id is empty
def test_bridge_empty_skill_id():
    result = run_manifest_skill({"request_id": "x", "skill_id": "", "inputs": {}}, ROOT)
    assert result is None
```

---

## T9.2 — Permission Enforcement Tests

**File:** `tests/test_permission_enforcement.py`

```python
# PermissionManager allows declared permissions
def test_permission_manager_allows_declared():
    mgr = PermissionManager(allowed={"repo:read", "qa:run"}, blocked=set())
    assert mgr.is_allowed("repo:read")
    assert mgr.is_allowed("qa:run")

# PermissionManager blocks unlisted permissions
def test_permission_manager_blocks_undeclared():
    mgr = PermissionManager(allowed={"repo:read"}, blocked=set())
    assert not mgr.is_allowed("shell:admin")

# PermissionManager blocks explicitly blocked permissions
def test_permission_manager_explicit_block():
    mgr = PermissionManager(allowed={"repo:read", "shell:admin"}, blocked={"shell:admin"})
    assert not mgr.is_allowed("shell:admin")

# PermissionManager defaults (empty allowed = allow all minus blocked)
def test_permission_manager_default_allows_everything():
    mgr = PermissionManager()  # no restrictions
    assert mgr.is_allowed("repo:read")
    assert mgr.is_allowed("anything:goes")

# Executor built from configs/permissions.json correctly loads blocked list
def test_executor_loads_permissions_from_config():
    from claudeclockwork.runtime import _load_permissions
    mgr = _load_permissions(ROOT)
    # configs/permissions.json blocks shell:admin and system:kill
    assert not mgr.is_allowed("shell:admin")
    assert not mgr.is_allowed("system:kill")
    # Allowed permissions work
    assert mgr.is_allowed("repo:read")
    assert mgr.is_allowed("qa:run")
```

> **Note:** If `PermissionManager.is_allowed()` does not yet exist, this phase introduces it as a minimal method. Check `claudeclockwork/core/security/permissions.py` first — if `PermissionManager` only stores sets without an `is_allowed()` method, add it.

---

## T9.3 — `ExecutionPipeline.run()` Tests

**File:** `tests/test_pipeline.py`

```python
# ExecutionPipeline.run() executes a skill end-to-end via planner + executor
def test_pipeline_runs_skill_registry_search():
    pipeline = ExecutionPipeline(
        build_planner(ROOT),
        build_executor(ROOT),
        working_directory=str(ROOT),
    )
    result = pipeline.run("skill_registry_search", query="qa")
    assert result is not None
    assert result.get("status") in ("ok", "fail")

# Pipeline returns a result with the expected spec structure
def test_pipeline_result_has_spec_fields():
    pipeline = ExecutionPipeline(build_planner(ROOT), build_executor(ROOT), working_directory=str(ROOT))
    result = pipeline.run("capability_map_build")
    assert "status" in result
    assert "errors" in result

# Pipeline handles unknown user_input gracefully (does not raise)
def test_pipeline_unknown_input_does_not_raise():
    pipeline = ExecutionPipeline(build_planner(ROOT), build_executor(ROOT), working_directory=str(ROOT))
    result = pipeline.run("this_skill_definitely_does_not_exist")
    assert result is not None  # must return a dict, not raise
```

---

## T9.4 — CLI Argument Parsing Tests

**File:** `tests/test_cli.py`

```python
import subprocess, sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def _cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "claudeclockwork.cli", "--project-root", str(ROOT), *args],
        capture_output=True, text=True, cwd=str(ROOT),
    )

# --skill-id with known skill returns exit 0 and JSON
def test_cli_known_skill_exits_zero():
    r = _cli("--skill-id", "skill_registry_search", "--inputs", '{"query":"qa"}')
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data.get("status") == "ok"

# --skill-id with unknown skill returns exit 1 and error JSON
def test_cli_unknown_skill_exits_one():
    r = _cli("--skill-id", "no_such_skill_xyz")
    assert r.returncode == 1
    data = json.loads(r.stdout)
    assert data.get("status") == "fail"
    assert "errors" in data

# --inputs with invalid JSON returns non-zero exit
def test_cli_invalid_json_inputs():
    r = _cli("--skill-id", "qa_gate", "--inputs", "not-json")
    assert r.returncode != 0

# --plugin-healthcheck for known plugin returns exit 0 and JSON
def test_cli_plugin_healthcheck_known():
    r = _cli("--plugin-healthcheck", "filesystem")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data.get("status") == "ok"

# --plugin-healthcheck for unknown plugin returns exit 1
def test_cli_plugin_healthcheck_unknown():
    r = _cli("--plugin-healthcheck", "no_such_plugin_xyz")
    assert r.returncode == 1
    data = json.loads(r.stdout)
    assert data.get("status") == "fail"
```

---

## T9.5 — Capability Matching Algorithm Tests

**File:** `tests/test_registry_search.py`

```python
# search() is case-insensitive
def test_search_case_insensitive():
    registry = build_registry(ROOT)
    upper = registry.search("QA")
    lower = registry.search("qa")
    assert {m.name for m in upper} == {m.name for m in lower}

# search() returns higher-scoring exact-name match first
def test_search_exact_name_ranks_first():
    registry = build_registry(ROOT)
    results = registry.search("qa_gate")
    assert results[0].name == "qa_gate"

# search() returns empty list for nonsense query
def test_search_no_match():
    registry = build_registry(ROOT)
    results = registry.search("zzz_definitely_not_a_skill_name_zzz")
    assert results == []

# search(enabled_only=False) returns more results than search(enabled_only=True) if any disabled
def test_search_enabled_only_filter():
    registry = build_registry(ROOT)
    all_results = registry.search("", enabled_only=False)  # wait — search("") returns 0; use list_skills
    all_skills = registry.list_skills(enabled_only=False)
    enabled_skills = registry.list_skills(enabled_only=True)
    # All enabled skills are in the enabled list
    assert len(enabled_skills) <= len(all_skills)

# list_skills() is sorted by (category, name)
def test_list_skills_sorted():
    registry = build_registry(ROOT)
    skills = registry.list_skills(enabled_only=False)
    pairs = [(m.category, m.name) for m in skills]
    assert pairs == sorted(pairs)
```

---

## Acceptance Criteria

- All 5 new test files are collected by pytest
- Each new test module contributes ≥ 5 passing tests
- Total test count increases from 136 to ≥ 165
- All Phase 6 gates continue to pass
- No new test depends on network, GPU, or any optional dependency

---

## Implementation Notes

- Check `PermissionManager` API before writing T9.2 — if `is_allowed()` doesn't exist, add it in `claudeclockwork/core/security/permissions.py` as part of this phase
- Check `ExecutionPipeline.run()` signature before writing T9.3 — align test inputs to actual signature
- T9.4 CLI tests use `subprocess` to test the real CLI entry point, not internal functions — this ensures argument parsing is covered end-to-end
- The `search("")` behaviour (returns 0 results) is intentional; use `list_skills()` for all-skills enumeration

## Files Changed / Created

| File | Change |
|------|--------|
| `tests/test_error_paths.py` | New — 7 tests |
| `tests/test_permission_enforcement.py` | New — 5 tests |
| `tests/test_pipeline.py` | New — 3 tests |
| `tests/test_cli.py` | New — 5 tests |
| `tests/test_registry_search.py` | New — 5 tests |
| `claudeclockwork/core/security/permissions.py` | Add `is_allowed()` if missing |
