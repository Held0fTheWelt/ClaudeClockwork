# telemetry_summarize

**Pack:** `unclassified`

## Purpose
Aggregates JSONL telemetry events into grouped token/cost/quality summaries (CCW-MVP12).
- Input: `{"events_dir": str, "run_id_filter": str|null, "group_by": [str], "top_n": int}`
  - `events_dir` defaults to `.claude-performance/events/`
  - `group_by` defaults to `["role", "model"]`; supports any TelemetryEvent fields
  - `top_n` defaults to 10
- Output: `{type: telemetry_summary, groups: [{key, total_tokens, avg_tokens, run_count, total_cost_cents, avg_quality_score}], totals: {events, total_…

## Implementation
- Tool: `.claude/tools/skills/telemetry_summarize.py`
- Skill runner: `.claude/tools/skills/skill_runner.py`
- Contracts: `.claude/contracts/`

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in <request.json> --out <result.json>
```

## Outputs
Describe output files and write locations here.

## Grenzen / Nicht-Ziele
- Deterministisch: keine semantische "Wahrheitsprüfung" über Inhalte.
- Kann Kandidatenlisten liefern, aber nicht beweisen, dass etwas obsolet ist.
- Wenn LLM-Verfeinerung nötig ist: nutze das passende Playbook (Explore/Write/Critic/DecideGap).
