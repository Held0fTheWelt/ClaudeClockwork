# MVP Phase 2 — Wrapper Wave 3

**Goal:** Bring 11 high-priority legacy skills into the manifest system, expanding CLI coverage from 34 to 45 skills.

---

## Definition of Done

- [ ] All 11 skills callable via `python3 -m claudeclockwork.cli --skill-id <skill>`
- [ ] All 11 manifests pass `manifest_validate` (schema + entrypoint)
- [ ] `capability_map_build` reports 45 manifest skills
- [ ] Each new skill has at least one test asserting real output (not just `status == "ok"`)
- [ ] All existing tests pass

---

## Skills to Wrap

| Skill | Category | Migration priority | Notes |
|-------|----------|--------------------|-------|
| `determinism_proof` | qa | P1 | SHA256 digest chain — high value for audit trails |
| `hardening_scan_fix` | qa | P1 | Security pattern scanner — needs permission `fs:read` |
| `drift_semantic_check` | qa | P1 | Cross-file semantic drift detection |
| `team_topology_verify` | qa | P1 | Agent hierarchy validation |
| `reference_fix` | docs | P1 | Fixes backtick path references in docs |
| `outcome_event_generate` | evidence | P1 | Generates structured outcome events |
| `outcome_ledger_append` | evidence | P1 | Appends to outcome ledger — needs `fs:write` |
| `clockwork_version_bump` | misc | P2 | Version bump with changelog update |
| `telemetry_summarize` | performance | P2 | Token/cost summarizer from event logs |
| `performance_toggle` | performance | P2 | Enable/disable token budgeting |
| `performance_finalize` | performance | P2 | Export and persist performance report |

---

## Deliverables per Skill

For each skill, create:

1. **`manifest.json`** at `.claude/skills/<category>/<skill_name>/manifest.json`
   ```json
   {
     "id": "<skill_name>",
     "name": "<Human Readable Name>",
     "description": "<one sentence>",
     "version": "1.0.0",
     "category": "<category>",
     "entrypoint": "bundle.<category>.<skill_name>.skill:<ClassName>",
     "permissions": ["<required permissions>"],
     "legacy_bridge": true,
     "tags": ["<relevant tags>"]
   }
   ```

2. **`skill.py`** at `.claude/skills/<category>/<skill_name>/skill.py`
   ```python
   from claudeclockwork.legacy.adapter import LegacySkillAdapter

   class <ClassName>(LegacySkillAdapter):
       SKILL_ID = "<skill_name>"
   ```

3. **One test assertion** (see test section below)

---

## Directory Structure After Phase 2

```
.claude/skills/
  qa/
    determinism_proof/        ← NEW
    hardening_scan_fix/       ← NEW
    drift_semantic_check/     ← NEW
    team_topology_verify/     ← NEW
  docs/
    reference_fix/            ← NEW
  evidence/
    outcome_event_generate/   ← NEW
    outcome_ledger_append/    ← NEW
  misc/
    clockwork_version_bump/   ← NEW
  performance/
    telemetry_summarize/      ← NEW
    performance_toggle/       ← NEW
    performance_finalize/     ← NEW
```

---

## Tests

Add to `tests/test_wrapper_wave3.py`:

```python
import pytest
from pathlib import Path
from claudeclockwork.bridge import run_manifest_skill

PROJECT_ROOT = Path(__file__).resolve().parents[1]

WAVE3_SKILLS = [
    "determinism_proof",
    "hardening_scan_fix",
    "drift_semantic_check",
    "team_topology_verify",
    "reference_fix",
    "outcome_event_generate",
    "outcome_ledger_append",
    "clockwork_version_bump",
    "telemetry_summarize",
    "performance_toggle",
    "performance_finalize",
]

@pytest.mark.parametrize("skill_id", WAVE3_SKILLS)
def test_wave3_skill_executes(skill_id):
    result = run_manifest_skill(
        {"request_id": "test", "skill_id": skill_id, "inputs": {}},
        PROJECT_ROOT
    )
    assert result is not None
    assert result["status"] == "ok"

def test_capability_map_reports_45_skills():
    result = run_manifest_skill(
        {"request_id": "test", "skill_id": "capability_map_build", "inputs": {}},
        PROJECT_ROOT
    )
    manifest_count = result["outputs"]["manifest_skill_count"]
    assert manifest_count >= 45
```

---

## Implementation Order

1. Start with `qa` group (determinism_proof, hardening_scan_fix, drift_semantic_check, team_topology_verify) — highest value
2. Then `evidence` group (outcome_event_generate, outcome_ledger_append) — artifact pipeline
3. Then `docs/reference_fix`
4. Finally `performance` group and `misc` — lower urgency

## Dependencies

- Phase 1 complete (manifest_validate must pass before wrapping)
- `configs/permissions.json` may need entries for `fs:write` (outcome_ledger_append)

## Notes

- Do not modify the legacy `.py` files — wrap only
- `skill_runner.py` must keep working for all 97 legacy skills throughout this phase
- If a skill requires inputs that have no sensible default for smoke tests, add `"inputs": {"dry_run": true}` convention
