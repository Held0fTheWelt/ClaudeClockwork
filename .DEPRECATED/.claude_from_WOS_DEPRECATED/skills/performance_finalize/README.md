# performance_finalize

End-of-run performance export:
- reads `.claude/config/performance_budgeting.yaml`
- runs `budget_analyze` (and optionally `efficiency_review`)
- exports charts under `.claude-performance/reports/charts/`
- can auto-disable budgeting if a token threshold is exceeded

## Skill ID
- `performance_finalize`
