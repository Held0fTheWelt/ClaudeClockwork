# Model Policy (Root)

**Canonical policy.** Extended content: `.claude/MODEL_POLICY.md`.

## Conventions

- **Product code origin:** Application/plugin source files MUST live under `src/` (see `.claude/policies/SRC_ORIGIN_RULE.md`). Current codebase still has primary logic in `llamacode/` and `oodle/`; migration is roadmap item.

## Performance Budgeting

- Token budgeting is **enabled by default** (`.claude/config/performance_budgeting.yaml`).
- Toggle: `performance_toggle` (TeamLead may disable if too expensive).
- Export at end: `performance_finalize`.

## Tiers and Triggers

See `.claude/config/model_escalation_ladder.yaml` and `.claude/governance/model_escalation_policy.md` for model tiers and escalation rules.
