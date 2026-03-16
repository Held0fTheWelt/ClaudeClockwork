# escalation_router

**Pack:** `unclassified`

## Purpose
Cheapest-first model routing with automatic escalation (wraps `.claude/tools/skills/escalation_router.py`; claudeclockwork native: planned Phase 3).
- Input: `{"ladder": "haiku"|"sonnet", "messages": [...], "max_tokens": int, "dry_run": bool}`
- Output: `{"model_used": str, "rung": int, "content": str, "escalated": bool, "escalation_reason": str|null}`
- Escalates on HTTP 429/529/503/500, timeout, or empty response
- `dry_run=true` returns ladder config without any API call
- Schema: `contracts/schemas/escalation_router.schema.json`
- Exampl…

## Implementation
- Tool: `.claude/tools/skills/escalation_router.py`
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
