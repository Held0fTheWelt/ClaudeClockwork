# MVP Phase 14 — Native Skill Promotion

**Goal:** Promote 8 high-value legacy-bridged skills to native `SkillBase` implementations in `claudeclockwork/`. Native skills have typed Python implementations, proper error handling, and no dependency on legacy `run(req)` dict dispatch. This reduces the coupling between the manifest system and the legacy `.claude/tools/skills/` layer for the most-used skills.

**Source finding:** NEW_MVPS.md — "Make implementation MVPs for still unimplemented skills." These skills exist as legacy implementations; this phase gives them proper native implementations.

---

## Definition of Done

- [x] `capability_map_build` has a native implementation (`.claude/skills/meta/capability_map_build/skill.py` — `CapabilityMapBuildSkill`)
- [x] `skill_registry_search` has a native implementation (`.claude/skills/meta/skill_registry_search/skill.py` — `SkillRegistrySearchSkill`)
- [x] `qa_gate` has a native implementation (`.claude/skills/qa/qa_gate/skill.py` — `QaGateSkill`)
- [x] `eval_run` has a native implementation (`.claude/skills/ops/eval_run/skill.py` — `EvalRunSkill`, D6.7 format)
- [x] `budget_router` has a native implementation (`.claude/skills/routing/budget_router/skill.py` — `BudgetRouterSkill`)
- [x] `plan_lint` has a native implementation (`.claude/skills/planning/plan_lint/skill.py` — `PlanLintSkill`)
- [x] Each native skill: manifest entrypoint updated to point to native class; `LegacySkillAdapter` no longer used for these 6 skills
- [x] Legacy `.py` files retained (`skill_runner.py` still works)
- [x] All existing tests pass; 24 new native skill tests added in `tests/test_native_skills_phase14.py`

---

## N14.1 — `capability_map_build` (native)

**Current:** `LegacySkillAdapter` → `.claude/tools/skills/capability_map_build.py`
**Native location:** `claudeclockwork/core/ops/capability_map_build.py`
**Class:** `CapabilityMapBuildSkill(SkillBase)`

**Logic:** Walk `.claude/skills/*/manifest.json` files via the registry; return a structured map with manifest skill count, legacy skill count, skill IDs, and categories.

**Inputs:** none required; `root` (str, optional — defaults to working directory)
**Outputs:** `manifest_skill_count` (int), `legacy_skill_count` (int), `skills` (list of `{id, category, status}`), `categories` (dict of category → count)

**Manifest update:** `.claude/skills/ops/capability_map_build/manifest.json`
- Set `"legacy_bridge": false`
- Update `entrypoint` → `claudeclockwork.core.ops.capability_map_build:CapabilityMapBuildSkill`

**Why native:** Already a CI gate dependency and called by MCP server; latency reduction and direct registry access are high value.

---

## N14.2 — `skill_registry_search` (native)

**Current:** `LegacySkillAdapter` → `.claude/tools/skills/skill_registry_search.py`
**Native location:** `claudeclockwork/core/ops/skill_registry_search.py`
**Class:** `SkillRegistrySearchSkill(SkillBase)`

**Logic:** Call `build_registry(root).search(query)` from `claudeclockwork.core.registry`; return structured results list with name, category, and status per match.

**Inputs:** `query` (str), `root` (str, optional)
**Outputs:** `results` (list of `{id, category, status, description}`), `count` (int)

**Manifest update:** `.claude/skills/ops/skill_registry_search/manifest.json`
- Set `"legacy_bridge": false`
- Update `entrypoint` → `claudeclockwork.core.ops.skill_registry_search:SkillRegistrySearchSkill`

**Why native:** MCP server calls this skill on every lookup; direct registry access eliminates the subprocess round-trip.

---

## N14.3 — `qa_gate` (native)

**Current:** `LegacySkillAdapter` → `.claude/tools/skills/qa_gate.py`  (or equivalent gate runner)
**Native location:** `claudeclockwork/core/ops/qa_gate.py`
**Class:** `QaGateSkill(SkillBase)`

**Logic:** Run the 7 quality checks in sequence using existing gate logic:
1. Manifest lint — validate all `manifest.json` files parse and have required keys
2. Import lint — check each manifest entrypoint is importable
3. Permission lint — check no skill declares unknown permissions
4. Smoke check — call `capability_map_build` and verify count is non-zero
5. Registry diff — compare legacy skill count vs manifest skill count
6. Plugin diff — check declared plugins exist on disk
7. Eval snapshot — compare current eval results against baseline if present

Return per-gate pass/fail with detail strings. Aggregate pass = all 7 pass.

**Inputs:** `gate_level` (int: 1 = fast/checks 1–4 only, 2 = full/all 7; default 2)
**Outputs:** `pass` (bool), `gate_results` (dict of gate_name → `{pass, detail}`), `gates_run` (int)

**Manifest update:** `.claude/skills/ops/qa_gate/manifest.json`
- Set `"legacy_bridge": false`
- Update `entrypoint` → `claudeclockwork.core.ops.qa_gate:QaGateSkill`

---

## N14.4 — `eval_run` (native)

**Current:** `LegacySkillAdapter` → `.claude/tools/skills/eval_run.py`
**Native location:** `claudeclockwork/core/ops/eval_run.py`
**Class:** `EvalRunSkill(SkillBase)`

**Logic:** Load a test suite YAML from `.claude/eval/`; run each test case; write a D6.7 snapshot to `.clockwork_runtime/eval/results/<run_id>.json`. Return structured result.

**Inputs:** `suite` (str, optional — run all suites if omitted), `dry_run` (bool, default false)
**Outputs:** `run_id` (str), `pass_count` (int), `fail_count` (int), `duration_ms` (float), `results_path` (str), `tests` (list of `{name, status, detail}`)

**D6.7 snapshot format:** `{run_id, suite, timestamp, pass_count, fail_count, tests[]}` — written atomically to results path.

**Manifest update:** `.claude/skills/ops/eval_run/manifest.json`
- Set `"legacy_bridge": false`
- Update `entrypoint` → `claudeclockwork.core.ops.eval_run:EvalRunSkill`

---

## N14.5 — `budget_router` (native)

**Current:** `LegacySkillAdapter` → `.claude/tools/skills/budget_router.py`
**Native location:** `claudeclockwork/core/routing/budget_router_native.py`
**Class:** `BudgetRouterSkill(SkillBase)`

**Logic:** Port the existing deterministic `_decide()` logic from the legacy `.py`. Pure function — no I/O, no external dependencies, no subprocess. Accepts complexity/risk/urgency scores and a mode string; returns a routing decision with tier, model, and rationale.

**Inputs:** `complexity` (int 1–5), `risk` (int 1–5), `urgency` (int 1–5), `mode` (str: `"balanced"` | `"fast"` | `"quality"`; default `"balanced"`)
**Outputs:** `tier` (str), `model` (str), `rationale` (str), `escalation_level` (int)

**Manifest update:** `.claude/skills/routing/budget_router/manifest.json`
- Set `"legacy_bridge": false`
- Update `entrypoint` → `claudeclockwork.core.routing.budget_router_native:BudgetRouterSkill`

**Why native:** Deterministic logic with no side effects is the clearest candidate for native promotion; enables unit-level testing of routing decisions.

---

## N14.6 — `plan_lint` (native)

**Current:** `LegacySkillAdapter` → `.claude/tools/skills/plan_lint.py`
**Native location:** `claudeclockwork/core/planning/plan_lint.py`
**Class:** `PlanLintSkill(SkillBase)`

**Logic:** Receive a plan document path or inline text. Check for required sections (Goal, Tasks, Acceptance Criteria, Files Changed). Return a lint errors list with line references where sections are absent or malformed.

**Required sections checked:**
- `## Definition of Done` or `## DoD` — must contain at least one `- [ ]` checkbox
- At least one numbered task section (`## N` or `## P` or `## S` prefix)
- `## Files Changed` — must contain a markdown table
- `## Acceptance Criteria` — must be non-empty

**Inputs:** `path` (str, optional — path to plan file), `text` (str, optional — inline plan text; one of `path` or `text` required)
**Outputs:** `errors` (list of `{section, message}`), `warnings` (list of `{section, message}`), `pass` (bool — true if zero errors)

**Manifest update:** `.claude/skills/planning/plan_lint/manifest.json`
- Set `"legacy_bridge": false`
- Update `entrypoint` → `claudeclockwork.core.planning.plan_lint:PlanLintSkill`

---

## N14.7 — Tests (`tests/test_native_skills_phase14.py`)

4 tests per skill × 6 skills = 24 tests. Pattern per skill:

1. **Registry entrypoint check** — skill is in registry with an entrypoint that does NOT contain `LegacySkillAdapter`
2. **Smoke run** — `run_manifest_skill({"skill_id": "<id>", "inputs": <minimal>}, ROOT)` returns `status: ok`
3. **Output keys** — output dict contains all declared output keys
4. **Graceful empty inputs** — missing optional inputs use defaults; no unhandled exception

```python
# Example test pattern (one skill shown)

def test_budget_router_entrypoint_is_native():
    registry = build_registry(ROOT)
    skill = registry.get("budget_router")
    assert "LegacySkillAdapter" not in skill.entrypoint

def test_budget_router_smoke():
    result = run_manifest_skill(
        {"skill_id": "budget_router", "inputs": {"complexity": 3, "risk": 2, "urgency": 1, "mode": "balanced"}},
        ROOT
    )
    assert result["status"] == "ok"

def test_budget_router_output_keys():
    result = run_manifest_skill(
        {"skill_id": "budget_router", "inputs": {"complexity": 3, "risk": 2, "urgency": 1}},
        ROOT
    )
    for key in ("tier", "model", "rationale", "escalation_level"):
        assert key in result["outputs"]

def test_budget_router_defaults_mode():
    # mode is optional — must not raise
    result = run_manifest_skill(
        {"skill_id": "budget_router", "inputs": {"complexity": 1, "risk": 1, "urgency": 1}},
        ROOT
    )
    assert result["status"] == "ok"
```

---

## Implementation Pattern

All native skills follow this structure:

```
.claude/skills/<category>/<skill_id>/
  manifest.json       ← updated: legacy_bridge: false, entrypoint → native class
  skill.py            ← native implementation (no LegacySkillAdapter)
  __init__.py         ← empty
```

```python
# skill.py (template)
from __future__ import annotations
from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


class <ClassName>(SkillBase):
    def run(self, context: ExecutionContext) -> SkillResult:
        # implementation here
        return SkillResult(outputs={...})
```

The canonical implementation lives in `claudeclockwork/core/<subpackage>/<module>.py`. The `skill.py` in `.claude/skills/` is either a thin re-export or the manifest entrypoint points directly to the `claudeclockwork` module path.

---

## Files Changed

| File | Change |
|------|--------|
| `claudeclockwork/core/ops/capability_map_build.py` | New native skill class |
| `claudeclockwork/core/ops/skill_registry_search.py` | New native skill class |
| `claudeclockwork/core/ops/qa_gate.py` | New native skill class |
| `claudeclockwork/core/ops/eval_run.py` | New native skill class |
| `claudeclockwork/core/routing/budget_router_native.py` | New native skill class |
| `claudeclockwork/core/planning/plan_lint.py` | New native skill class |
| `.claude/skills/ops/capability_map_build/manifest.json` | Update entrypoint; set `legacy_bridge: false` |
| `.claude/skills/ops/skill_registry_search/manifest.json` | Update entrypoint; set `legacy_bridge: false` |
| `.claude/skills/ops/qa_gate/manifest.json` | Update entrypoint; set `legacy_bridge: false` |
| `.claude/skills/ops/eval_run/manifest.json` | Update entrypoint; set `legacy_bridge: false` |
| `.claude/skills/routing/budget_router/manifest.json` | Update entrypoint; set `legacy_bridge: false` |
| `.claude/skills/planning/plan_lint/manifest.json` | Update entrypoint; set `legacy_bridge: false` |
| `tests/test_native_skills_phase14.py` | New — 24 tests (4 per skill × 6 skills) |

---

## Dependencies

- Phase 3 (`NativeCoreServices`) complete — `SkillBase`, `ExecutionContext`, `SkillResult` are stable
- Phase 6 (`CIEvalGates`) complete — D6.7 eval format is defined
- `claudeclockwork/core/` models must not be modified during this phase
- Legacy `.py` files in `.claude/tools/skills/` are NOT deleted — `skill_runner.py` dispatch remains intact

## Notes

- The 6 native skills in this phase bring the total native (non-`LegacySkillAdapter`) manifest skills from 4 to 10.
- `doc_write` and `system_map` are deferred to a later phase; their structured output contracts need further specification before native promotion.
- Manifests that still use `LegacySkillAdapter` retain `"legacy_bridge": true`; the 6 promoted skills switch to `"legacy_bridge": false`.

---

## Acceptance Criteria

- None of the 6 promoted skills use `LegacySkillAdapter` in their manifest entrypoint
- `python3 -m claudeclockwork.cli --skill-id budget_router --inputs '{"complexity":3,"risk":2,"urgency":1,"mode":"balanced"}'` returns a native result with `tier`, `model`, and `rationale` keys
- `python3 -m claudeclockwork.cli --skill-id qa_gate --inputs '{"gate_level":1}'` returns `{"pass": true, ...}` on a clean repository
- 24 new tests in `tests/test_native_skills_phase14.py` pass
- All pre-existing tests continue to pass (no regression)
- `grep -r "LegacySkillAdapter" .claude/skills/ops/capability_map_build/` returns zero results
