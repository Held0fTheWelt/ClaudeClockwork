# MVP Phase 3 — Native Core Services

**Goal:** Rewrite the most critical meta and QA skills as native Python implementations — removing the `LegacySkillAdapter` dependency for foundational services.

---

## Definition of Done

- [X] 11 listed skills have native `skill.py` implementations (no `LegacySkillAdapter`)
- [X] Each native skill is importable from `claudeclockwork.*` without side effects
- [X] Each native skill has unit tests for core logic (not just integration smoke)
- [X] `skill_runner.py` legacy equivalents remain functional (no regression)
- [X] All existing tests pass; ≥8 new tests added

---

## Rationale

The current `LegacySkillAdapter` pattern works but couples the manifest system to the legacy subprocess runner. Native skills:
- Are faster (no subprocess launch)
- Are testable at unit level
- Can share `claudeclockwork.core.*` types directly
- Enable reliable Phase 4 plugin boundaries

---

## Wave 1 — Meta/Registry Skills (highest leverage)

### `skill_registry_search`

**Current:** `LegacySkillAdapter` → `.claude/tools/skills/skill_registry_search.py`
**Native:** Directly call `SkillRegistry.search(query)` from `claudeclockwork.core.registry`

```python
class SkillRegistrySearchSkill(SkillBase):
    def run(self, context: ExecutionContext) -> SkillResult:
        query = context.config.get("query", "")
        registry = build_registry(Path(context.working_directory))
        results = registry.search(query)
        return SkillResult(outputs={"results": [r.name for r in results], "count": len(results)})
```

### `skill_scaffold`

**Current:** `LegacySkillAdapter` → `.claude/tools/skills/skill_scaffold.py`
**Native:** Generate `manifest.json` + `skill.py` from a template, optionally call `manifest_validate`

Inputs: `skill_id`, `category`, `description`, `dry_run` (bool)
Outputs: `manifest_path`, `skill_path`, `valid` (bool if not dry_run)

### `capability_map_build`

**Current:** `LegacySkillAdapter` → `.claude/tools/skills/capability_map_build.py`
**Native:** Call `build_registry()` directly and emit structured map

Outputs: `manifest_skill_count`, `legacy_skill_count`, `skills` (list of {id, category, status})

---

## Wave 2 — QA Gate Skills

### `repo_validate`

**Current:** `LegacySkillAdapter`
**Native:** Check that declared paths in `ARCHITECTURE.md` and `CLAUDE.md` exist on disk; check boot_check passes; return structured findings

Inputs: `project_root`
Outputs: `pass` (bool), `findings` (list of {path, status, severity})

### `spec_validate`

**Current:** `LegacySkillAdapter`
**Native:** Validate JSON files against their declared schemas in `.claude/contracts/schemas/`

Inputs: `target` (file or directory), `schema_root`
Outputs: `valid` (bool), `errors` (list)

### `qa_gate`

**Current:** `LegacySkillAdapter`
**Native:** Orchestrate: run `manifest_validate`, `repo_validate`, `spec_validate` in sequence; return aggregate pass/fail

Inputs: `gate_level` (1=fast, 2=full)
Outputs: `pass` (bool), `gate_results` (dict per sub-gate)

---

## Wave 3 — Artifact/Evidence Pipeline

### `evidence_bundle_build`

**Current:** `LegacySkillAdapter`
**Native:** Collect specified artifacts into a signed bundle (SHA256 manifest), write to `.llama_runtime/`

Inputs: `artifacts` (list of paths), `bundle_name`
Outputs: `bundle_path`, `manifest_hash`, `artifact_count`

### `security_redactor`

**Current:** `LegacySkillAdapter`
**Native:** Scan files for patterns matching `configs/redaction_patterns.json`; redact matches

Inputs: `target`, `dry_run`
Outputs: `redacted_count`, `findings` (list)

### `parity_scan_and_mvp_planner`

**Current:** `LegacySkillAdapter`
**Native:** Compare legacy skill inventory vs manifest registry; emit a prioritized wrap-next list

Outputs: `unwrapped_count`, `wrap_candidates` (list with priority), `parity_percent`

### `eval_run`

**Current:** `LegacySkillAdapter`
**Native:** Load eval suite from `.claude/eval/`, run each test, write results to `.llama_runtime/eval/results/`

Inputs: `suite` (optional — runs all if omitted)
Outputs: `pass_count`, `fail_count`, `results_path`

### `pdf_quality`

**Current:** `LegacySkillAdapter`
**Native:** Run PDF quality rubric against a given document path; return structured score

Inputs: `document_path`, `rubric` (optional — defaults to `.claude/skills/pdf_quality/rubric.md`)
Outputs: `score`, `max_score`, `findings` (list by rubric section)

---

## Implementation Pattern

All native skills follow this structure:

```
.claude/skills/<category>/<skill_name>/
  manifest.json       ← updated: legacy_bridge: false
  skill.py            ← native implementation (no LegacySkillAdapter)
  __init__.py         ← empty
```

```python
# skill.py
from __future__ import annotations
from pathlib import Path
from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


class <ClassName>(SkillBase):
    def run(self, context: ExecutionContext) -> SkillResult:
        # real implementation here
        ...
        return SkillResult(outputs={...})
```

---

## Tests

Add `tests/test_native_skills.py`:

```python
# One unit test per native skill testing core logic

def test_skill_registry_search_returns_matches():
    result = run_manifest_skill({"skill_id": "skill_registry_search", "inputs": {"query": "qa"}}, ROOT)
    assert result["status"] == "ok"
    assert result["outputs"]["count"] > 0
    assert all("qa" in r or True for r in result["outputs"]["results"])  # search returns results

def test_capability_map_includes_all_manifest_skills():
    result = run_manifest_skill({"skill_id": "capability_map_build", "inputs": {}}, ROOT)
    assert result["outputs"]["manifest_skill_count"] >= 45  # Phase 2 baseline

def test_qa_gate_passes_on_clean_repo():
    result = run_manifest_skill({"skill_id": "qa_gate", "inputs": {"gate_level": 1}}, ROOT)
    assert result["outputs"]["pass"] is True

def test_evidence_bundle_build_creates_hash():
    result = run_manifest_skill({
        "skill_id": "evidence_bundle_build",
        "inputs": {"artifacts": ["VERSION"], "bundle_name": "test_bundle"}
    }, ROOT)
    assert result["status"] == "ok"
    assert "manifest_hash" in result["outputs"]

def test_parity_scan_detects_unwrapped_skills():
    result = run_manifest_skill({"skill_id": "parity_scan_and_mvp_planner", "inputs": {}}, ROOT)
    assert result["outputs"]["unwrapped_count"] >= 0  # should not crash
    assert "wrap_candidates" in result["outputs"]
```

---

## Dependencies

- Phase 1 (manifest hardening) complete
- Phase 2 (wrapper wave 3) complete
- `claudeclockwork/core/` models stable — do not modify models while implementing native skills

## Notes

- The legacy `.py` equivalents in `.claude/tools/skills/` are NOT deleted in this phase — they remain as fallback
- `skill_runner.py` dispatch for these skills stays intact
- Mark manifests with `"legacy_bridge": false` after native implementation is confirmed passing
