# efficiency_review

Deterministic consolidation of a multi-panel efficiency review:
- Worker (Oodle) + Worker (DeepSeek)
- TeamLead self-benchmark
- Judge (strong Oodle) quality estimate

This skill **does not call LLMs**. It ingests panel outputs you produce as JSON and merges them with the budget report.

## Inputs
- `budget_report_path`
- `panels_path` (JSON file with worker/teamlead/judge scores + notes)

## Output
- review JSON/MD under `.claude-performance/reports/`
- optional chart export
