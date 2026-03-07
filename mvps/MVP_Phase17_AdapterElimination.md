# MVP Phase 17 — Adapter Elimination

**Goal:** Promote all 84 remaining `LegacySkillAdapter` skills to native `SkillBase` implementations. Remove the `LegacySkillAdapter` class entirely from `claudeclockwork/legacy/adapter.py`. After this phase, every manifest skill subclasses `SkillBase` directly, `legacy_bridge` is `false` in every manifest, and there is no runtime path that imports `LegacySkillAdapter`.

**Baseline:** v18.3 — 104 manifest skills: 20 native, 84 adapters.
**Target:** v19.0 — 104 manifest skills: 104 native, 0 adapters.
**Sources:** User directive — "remove the skill adapter and make all skills be known as native skills."

**Principle:** Do not rewrite what the legacy module already does correctly. The migration pattern inlines the legacy delegation logic directly in each `skill.py` rather than inheriting it, then removes the base class. True rewrites are reserved for skills where the legacy logic is unreliable or the output contract is wrong.

---

## Definition of Done

- [ ] All 84 adapter skills have `skill.py` subclassing `SkillBase` directly (not `LegacySkillAdapter`)
- [ ] All 84 manifests updated: `"legacy_bridge": false`
- [ ] `claudeclockwork/legacy/adapter.py` deleted (or reduced to a `# REMOVED` tombstone stub)
- [ ] No `from claudeclockwork.legacy.adapter import LegacySkillAdapter` anywhere in `.claude/skills/`
- [ ] `tests/test_adapter_elimination.py` — 3 tests verifying the adapter is gone and all skills are native
- [ ] All pre-existing tests continue to pass (≥ 352 tests)
- [ ] `skill_health` returns `unhealthy == 0` (no broken entrypoints or missing bridges)
- [ ] Roadmap updated: Phase 17 = this phase

---

## Migration Pattern

Every adapter skill currently looks like:

```python
from claudeclockwork.legacy.adapter import LegacySkillAdapter

class FooSkill(LegacySkillAdapter):
    legacy_skill_id = "foo"
```

The **inline delegation** replacement — the preferred migration for all 84 skills — inlines the adapter logic without inheriting it:

```python
import os
import sys
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult

class FooSkill(SkillBase):
    _LEGACY_ID = "foo"

    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        skills_root = repo_root / ".claude" / "tools" / "skills"
        if str(skills_root) not in sys.path:
            sys.path.insert(0, str(skills_root))
        try:
            module = __import__(self._LEGACY_ID)
        except Exception as exc:
            return SkillResult(False, self._LEGACY_ID, error=f"Legacy import failed: {exc}")
        req = {
            "type": "skill_request_spec",
            "request_id": context.request_id,
            "skill_id": self._LEGACY_ID,
            "inputs": kwargs,
        }
        old_cwd = Path.cwd()
        try:
            os.chdir(repo_root)
            result = module.run(req)
        except Exception as exc:
            return SkillResult(False, self._LEGACY_ID, error=f"Legacy execution failed: {exc}")
        finally:
            os.chdir(old_cwd)
        status = result.get("status") == "ok"
        outputs = result.get("outputs", {})
        errors = result.get("errors", [])
        warnings = result.get("warnings", [])
        metrics = result.get("metrics", {})
        return SkillResult(
            success=status,
            skill_name=self._LEGACY_ID,
            data=outputs,
            error=("; ".join(errors) if errors else None),
            warnings=warnings,
            metadata=metrics,
        )
```

This is **behavior-identical** to the current adapter. No logic changes, no output contract changes, no regressions. The only difference is the class hierarchy and the removal of `legacy_bridge` string from the manifest.

---

## P17.1 — Migration Script

**File:** `scripts/promote_to_native.py`

A one-shot script that reads every `.claude/skills/*/skill.py` with `LegacySkillAdapter` and rewrites it using the inline delegation pattern above. Runs dry-run by default (`--dry-run`). When run for real (`--apply`), also updates the corresponding `manifest.json` to set `"legacy_bridge": false`.

**Usage:**
```bash
python3 scripts/promote_to_native.py --dry-run   # preview changes
python3 scripts/promote_to_native.py --apply      # apply all 84 rewrites
```

**Logic:**
1. Glob `.claude/skills/**/skill.py`
2. Filter to files that contain `LegacySkillAdapter`
3. Extract the class name and `legacy_skill_id` value via regex
4. Render the inline delegation template
5. Write the updated `skill.py` and `manifest.json`

This script makes the 84-skill migration a single idempotent command rather than 84 manual edits.

---

## P17.2 — Adapter Elimination

Run `promote_to_native.py --apply`. The 84 affected skills are:

**Routing (7):** `bandit_router_select`, `escalation_router`, `model_routing_record_outcome`, `model_routing_select`, `route_autotune_suggest`, `route_profile_patch_pack`, `route_profile_update`

**Planning (11):** `create_mvp`, `creativity_burst`, `decision_feedback`, `deliberation_pack_build`, `economics_regression`, `edge_case_selector`, `hypothesis_builder`, `idea_dedupe`, `idea_scoring`, `plan_diff_apply`, `plan_mutate`

**Analysis (6):** `code_assimilate`, `limitation_harvest_scan`, `mechanic_explain`, `mutation_detect`, `pattern_detect`, `system_map`

**Docs (11):** `autodocs_generate`, `copyright_standardize`, `doc_review`, `doc_ssot_resolver`, `doc_write`, `log_standardize`, `pdf_export`, `pdf_render`, `reference_fix`, `screencast_script`, `tutorial_write`

**Performance (7):** `budget_analyze`, `efficiency_review`, `performance_finalize`, `performance_toggle`, `prompt_debt_capture`, `telemetry_summarize`, `token_event_log`

**Archive (4):** `last_train`, `last_train_merge`, `shadow_prompt`, `shadow_prompt_minify`

**QA (6):** `determinism_harness`, `determinism_proof`, `drift_semantic_check`, `hardening_scan_fix`, `schema_batch_validate`, `team_topology_verify`

**Evidence (4):** `evidence_init`, `evidence_router`, `outcome_event_generate`, `outcome_ledger_append`

**Code/Repo (9):** `cleanup_apply`, `cleanup_plan_apply`, `code_clean`, `code_clean_scan`, `contract_drift_sentinel`, `refactor_bridge_scan`, `repo_clean`, `repo_clean_scan`, `repo_compare`

**Meta/Registry (6):** `legacy_skill_inventory`, `manifest_registry_export`, `manifest_validate`, `reference_skill_catalog`, `skill_gap_detect`, `refactor_bridge_scan`

**Misc (8):** `clockwork_version_bump`, `critics_board_review`, `exec_dryrun`, `policy_gatekeeper`, `review_panel`, `triad_build`, `triad_ref_lint`, `work_scope_assess`

**Plugins (2):** `plugin_registry_export`, `plugin_scaffold`

**Demo (3):** `hello`, `report`, `scan`

---

## P17.3 — Remove LegacySkillAdapter

Once all 84 skills are migrated and tests pass:

1. **Delete** `claudeclockwork/legacy/adapter.py`
2. **Delete** `claudeclockwork/legacy/` directory if no other files remain; otherwise keep with a `__init__.py` note
3. **Grep verify:** `grep -r "LegacySkillAdapter" .claude/ claudeclockwork/` must return zero results
4. **Remove import** from any `__init__.py` or module that re-exports `LegacySkillAdapter`
5. **Update** `tests/test_native_skills_phase14.py` — remove the `LegacySkillAdapter` import and the `_is_native()` helper (no longer needed; all skills are native by definition)

---

## P17.4 — Tests (`tests/test_adapter_elimination.py`)

3 tests that gate the complete removal:

1. **`test_no_legacy_adapter_class_in_registry`** — build the registry with `strict=True` and assert that no loaded skill class is a subclass of `LegacySkillAdapter`; since `LegacySkillAdapter` is deleted, this test asserts the import itself fails:
   ```python
   with pytest.raises(ImportError):
       from claudeclockwork.legacy.adapter import LegacySkillAdapter
   ```

2. **`test_all_manifests_have_legacy_bridge_false`** — glob all `.claude/skills/**/manifest.json`, parse each, assert `metadata.legacy_bridge == false` (not a string, not absent — exactly `false`)

3. **`test_all_skills_are_native_skillbase`** — build registry, load every skill class, assert each is a subclass of `SkillBase` and its MRO contains no class named `LegacySkillAdapter`

---

## Files Changed

| File | Change |
|------|--------|
| `scripts/promote_to_native.py` | New — one-shot migration script |
| `.claude/skills/**/skill.py` (84 files) | Rewritten — inline delegation, no LegacySkillAdapter |
| `.claude/skills/**/manifest.json` (84 files) | Updated — `legacy_bridge: false` |
| `claudeclockwork/legacy/adapter.py` | Deleted |
| `tests/test_adapter_elimination.py` | New — 3 tests |
| `tests/test_native_skills_phase14.py` | Updated — remove LegacySkillAdapter import |

---

## Dependencies

- Phase 16 complete — all 104 skills are in the manifest registry
- `scripts/` directory must exist (create if absent)
- No new external dependencies

## Acceptance Criteria

- `grep -r "LegacySkillAdapter" .claude/skills/` returns zero results
- `python3 -c "from claudeclockwork.legacy.adapter import LegacySkillAdapter"` raises `ImportError`
- `skill_health` returns `total == 104` and `unhealthy == 0`
- All pre-existing tests pass (≥ 352 passing, 0 failing)
- 3 new tests in `tests/test_adapter_elimination.py` pass
