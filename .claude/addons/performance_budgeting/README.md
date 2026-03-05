# Performance Budgeting (Pack)

## Included skills
- `token_event_log` — append one token event (JSONL) per agent step
- `token_event_autologger.py` — CLI wrapper to log events via env vars

- `budget_analyze` — token spend attribution (role/model/task)
- `efficiency_review` — merge multi-panel review with budget report

## Outputs
- `.claude-performance/events/` (input)
- `.claude-performance/reports/` (budget + review outputs)

## Boundaries
- This pack is optional. Core should not depend on it to boot.
- See `../BOUNDARIES.md` and `../map.yaml`.


## Recommended wrapper
- `.claude/tools/run_agent_step.py` — run step + log event (single line).


## Pricing snapshot
- `.claude/config/anthropic_pricing_snapshot.json` (update when pricing changes)
