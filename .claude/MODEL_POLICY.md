# MODEL_POLICY.md (Pointer)

This file is a **clockwork pointer** for Claude Code.

Canonical location (this project):
- `.project/MODEL_POLICY.md`

When deploying Clockwork on another project, create `MODEL_POLICY.md` at that project's root.

## Conventions

- **Product code origin:** all application/plugin source files MUST live under `src/` (see `policies/SRC_ORIGIN_RULE.md`).

## Performance Budgeting
- Token budgeting is **enabled by default** (see `.claude/config/performance_budgeting.yaml`).
- Toggle: `performance_toggle` (TeamLead may disable if too expensive).
- Export at end: `performance_finalize`.
