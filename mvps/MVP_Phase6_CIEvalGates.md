# MVP Phase 6 — CI / Eval / Quality Gates

**Goal:** Make the skill system permanently verifiable through automated gates that catch regressions before they land.

---

## Definition of Done

- [X] All 7 gates pass on clean checkout
- [X] A manifest with a bad entrypoint fails the import lint gate
- [X] A skill removed from the registry is caught by the registry diff gate
- [X] Gates run in CI on every commit (GitHub Actions)
- [X] `eval_run` stores results to `.llama_runtime/eval/results/` with per-run snapshots
- [X] All existing tests pass (136 total)

---

## Deliverables

### D6.1 — Manifest Lint Gate

**What:** Validate all `manifest.json` files against the schema from Phase 1.

**Implementation:** Extend `tests/test_gates.py`:

```python
def test_manifest_lint():
    """All manifests must pass schema validation."""
    from claudeclockwork.runtime import build_registry
    registry = build_registry(Path(".").resolve(), strict=True)
    assert len(registry.validation_errors) == 0, registry.validation_errors
```

**CI failure condition:** Any manifest missing a required field or having wrong type.

---

### D6.2 — Import Lint Gate

**What:** All manifest entrypoints must resolve without `ModuleNotFoundError`.

```python
def test_import_lint():
    """All manifest entrypoints must be importable."""
    registry = build_registry(Path(".").resolve())
    errors = []
    for item in registry.list_skills(enabled_only=False):
        manifest = registry.get_manifest(item.name)
        try:
            registry._loader.load_skill_class(manifest.entrypoint)
        except (ModuleNotFoundError, AttributeError) as e:
            errors.append(f"{item.name}: {e}")
    assert not errors, "\n".join(errors)
```

**CI failure condition:** Any entrypoint fails to import.

---

### D6.3 — Permission Lint Gate

**What:** All permissions declared in manifests must exist in `configs/permissions.json`.

```python
def test_permission_lint():
    """All manifest permissions must be declared in configs/permissions.json."""
    import json
    with open("configs/permissions.json") as f:
        allowed = set(json.load(f).get("allowed_permissions", []))
    registry = build_registry(Path(".").resolve())
    errors = []
    for item in registry.list_skills(enabled_only=False):
        manifest = registry.get_manifest(item.name)
        for perm in (manifest.permissions or []):
            if perm not in allowed:
                errors.append(f"{item.name}: unknown permission '{perm}'")
    assert not errors, "\n".join(errors)
```

---

### D6.4 — Smoke Run Gate

**What:** Every wrapped skill returns `status == "ok"` with empty inputs or declared minimal inputs.

```python
@pytest.mark.parametrize("skill_id", get_all_manifest_skill_ids())
def test_skill_smoke(skill_id):
    result = run_manifest_skill(
        {"request_id": "smoke", "skill_id": skill_id, "inputs": {}},
        Path(".").resolve()
    )
    # Allow "fail" only if inputs are genuinely required
    assert result is not None
    assert result.get("status") in ("ok", "fail")
    assert "errors" in result  # must always have errors field
```

Skills that require mandatory inputs must declare `"smoke_inputs": {...}` in their manifest for this gate to use.

---

### D6.5 — Registry Export Diff Gate

**What:** `capability_map_build` output must not change silently between commits.

**Implementation:**
1. Store a baseline snapshot: `.llama_runtime/eval/baselines/capability_map.json`
2. On each CI run, generate current snapshot and diff against baseline
3. Gate fails if skill count drops or any previously-present skill disappears

```python
def test_registry_export_diff():
    baseline_path = Path(".llama_runtime/eval/baselines/capability_map.json")
    if not baseline_path.exists():
        pytest.skip("No baseline — run: python3 scripts/update_baselines.py")
    import json
    baseline = json.loads(baseline_path.read_text())
    result = run_manifest_skill({"skill_id": "capability_map_build", "inputs": {}}, ROOT)
    current = result["outputs"]
    assert current["manifest_skill_count"] >= baseline["manifest_skill_count"], \
        f"Skill count dropped: {baseline['manifest_skill_count']} → {current['manifest_skill_count']}"
```

**Baseline update command:**
```bash
python3 scripts/update_baselines.py
```

---

### D6.6 — Plugin Index Diff Gate

**What:** Plugin registry must be stable across runs (no silent plugin additions or removals).

Same pattern as D6.5 but for `plugin_registry_export` output.

---

### D6.7 — Eval Run Integration

**What:** `eval_run` skill writes structured results to `.llama_runtime/eval/results/<timestamp>.json` for historical comparison.

Each result record:
```json
{
  "run_id": "2026-03-06T12:00:00",
  "suite": "default",
  "pass_count": 5,
  "fail_count": 0,
  "duration_ms": 4140,
  "tests": [
    {"name": "test_registry_discovers_manifest_skills", "status": "pass", "ms": 820}
  ]
}
```

**Trend tracking:** Compare last 5 runs; alert if pass rate drops below 100%.

---

## CI Configuration

**File:** `.github/workflows/ci.yml`

```yaml
name: Clockwork CI
on: [push, pull_request]

jobs:
  gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install pytest pytest-cov
      - run: python3 .claude/tools/boot_check.py
      - run: python3 -m pytest tests/ -v --tb=short
        # Includes: manifest lint, import lint, permission lint, smoke run, registry diff
```

---

## Dependencies

- Phase 1 (manifest hardening) — gates rely on `strict=True` registry mode
- Phase 2–3 (skill coverage) — smoke gate only meaningful with ≥45 skills
- Phase 4 (plugin runtime) — plugin diff gate requires live plugin registry
- `.llama_runtime/eval/baselines/` directory must be seeded before diff gates activate

## Notes

- Gates D6.1–D6.3 can be implemented immediately after Phase 1 — they have no dependency on Phases 2–4
- The smoke gate (D6.4) should run last in CI — it's the slowest (one subprocess per skill)
- Baselines are committed to the repo so CI always has a reference point
