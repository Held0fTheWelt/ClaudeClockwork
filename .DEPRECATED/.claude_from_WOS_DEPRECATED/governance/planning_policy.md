# Planning Policy (Plan Compaction v2)

Goal: minimize token spend by making plans small, deterministic, and verifiable.

## Max plan tasks
- Allowed range: 8–12
- Default: 12
- Active value: read from `.claude/settings.local.json`:
  - `planning.max_plan_tasks` (active)
  - `planning.max_plan_tasks_default` (default)

## Rules
1) Plans must conform to PlanSpec and contain:
   - goal (1 sentence)
   - constraints (<= 5 bullets)
   - tasks (<= max_plan_tasks)
   - acceptance criteria (explicit & testable)
   - risk + trust_mode
   - evidence_required (if applicable)

2) No essays
Anything that doesn't fit the schema is not a plan.

3) Plan Lock
Once approved, execution must follow the plan unless a trigger fires:
- context_missing=true
- repeat_failures>=2
- risk_changed=true

4) Two-phase planning (cost-first)
- Draft: cheap tier (C0 or O0/O1)
- Verify: tool-first (plan_lint), then local O3 only if needed
