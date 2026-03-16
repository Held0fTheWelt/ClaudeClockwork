# budget_analyze

Deterministic budget analysis of token spend.

## Goal
Make token costs explainable:
- **where** tokens were spent (task/phase)
- **by whom** (role/agent) and **which model**
- output in CLI-friendly ASCII bars + exported charts (matplotlib)

## Inputs
- `events_sources`: JSONL/JSON files containing `budget_event`
- `run_id`: filter
- `output_dir` + `export_prefix`

## Output
- `.claude-performance/reports/<export_prefix>_report.json/.md`
- charts under `.claude-performance/reports/charts/`

## Tip
If you want precise attribution, log events at the end of each agent step.

## Cost estimation
This skill can estimate USD cost when model identifiers match Anthropic models.
Pricing snapshot: `.claude/config/anthropic_pricing_snapshot.json`.
