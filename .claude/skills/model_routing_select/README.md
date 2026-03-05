# model_routing_select

**Pack:** `addon:model_routing_personaler`

## Purpose
Personaler model selector:
- chooses cheapest model likely good enough based on tier + hit list stats
- writes routing report under `.report/routing/<run_id>/`

## Implementation
- Tool: `.claude/tools/skills/model_routing_select.py`
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
