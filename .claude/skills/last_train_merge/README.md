# last_train_merge

**Pack:** `core`

## Purpose
Deterministic zip evolution analyzer + merger:
- scans multiple zips, ignores cache artifacts
- generates evolution vs loss timeline
- emits combined zip containing the union (latest wins)

## Implementation
- Tool: `.claude/tools/skills/last_train_merge.py`
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
