# Agent Step Wrapper

File: `.claude/tools/run_agent_step.py`

## Purpose
Run one agent/action command and append exactly one token event line to:
- `.claude-performance/events/<run_id>.jsonl`

This is the glue for accurate attribution:
- **where** costs happened (task/phase)
- **by whom** (role)
- **which model**
- **how many tokens**

## Recommended usage (env-driven)
Set environment variables in your agent runner:
- `CLOCKWORK_RUN_ID`
- `CLOCKWORK_ROLE` (Explore/Write/Critic/DecideGap/TeamLead/Judge)
- `CLOCKWORK_MODEL`
- `CLOCKWORK_TASK`
- `CLOCKWORK_PHASE` (optional)
- `CLOCKWORK_NOTES` (optional)
- `CLOCKWORK_PROMPT_TOKENS`, `CLOCKWORK_COMPLETION_TOKENS`, `CLOCKWORK_TOTAL_TOKENS` (if available)

Then run:
```bash
python .claude/tools/run_agent_step.py -- -- your-command --args
```

## Token parsing
If you don't provide tokens explicitly, the wrapper will try to parse them from stdout/stderr (heuristic).
For maximum reliability, pass tokens explicitly or write a JSON usage file and pass `--tokens-file`.

## Performance budgeting toggle
- Controlled by `.claude/config/performance_budgeting.yaml`
- If disabled, the wrapper will skip logging unless `--force-log` is used.
