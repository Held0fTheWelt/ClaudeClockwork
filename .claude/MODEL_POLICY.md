# MODEL_POLICY.md (Pointer)

This file is a **clockwork pointer** for Claude Code.

Project-level canonical location (repo root):
- <PROJECT_ROOT>/MODEL_POLICY.md

If the repo does not contain this file, create it at the project level.

## Conventions

- **Product code origin:** all application/plugin source files MUST live under `src/` (see `policies/SRC_ORIGIN_RULE.md`).

## Performance Budgeting
- Token budgeting is **enabled by default** (see `.claude/config/performance_budgeting.yaml`).
- Toggle: `performance_toggle` (TeamLead may disable if too expensive).
- Export at end: `performance_finalize`.
