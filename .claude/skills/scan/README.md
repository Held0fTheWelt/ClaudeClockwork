# scan

**Pack:** `unclassified`

## Purpose
Deterministic directory glob scanner (MVP02).
- Input: `{"path": "string", "pattern": "string (glob)"}`
- Output: `{"files": ["string"], "count": integer, "status": "ok"}`
- Standalone: `python tools/skills/scan.py '{"path": ".", "pattern": "**/*.py"}'`

## Implementation
- Tool: `.claude/tools/skills/scan.py`
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
