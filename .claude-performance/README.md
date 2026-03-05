# .claude-performance/ — Raw Telemetry

Raw, machine-readable telemetry from Clockwork runs.

## Structure
```
.claude-performance/
├── README.md
├── events/          ← JSONL token event logs
├── reports/         ← generated budget/perf reports
├── reviews/         ← LLM panel outputs (worker/teamlead/judge) + consolidated reviews
└── charts/          ← PNG charts from budget_analyze
```

## Naming
```
events/<run_id>_<YYYYMMDD>.jsonl
reports/budget_<run_id>_report.json
```

## Event Format
Each line in `events/*.jsonl` is a `budget_event`:
```json
{"ts": "<ISO8601>", "run_id": "...", "role": "...", "model": "...", "task": "...", "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
```

## Written by
- `.claude/tools/telemetry_writer.py`
- `.claude/tools/token_event_autologger.py`
- `.claude/tools/skills/budget_analyze.py`

## Schemas
- `.claude/contracts/schemas/budget_event.schema.json`
- `.claude/contracts/schemas/budget_report.schema.json`
- `.claude/contracts/schemas/efficiency_review.schema.json`

## Notes
- All event files are **append-only**. Never delete or truncate mid-run.
- Human-readable summaries derived from this data go into `.report/performance/`.
