# review_panel

**Pack:** `unclassified`

## Purpose
Consolidates multi-reviewer verdicts (worker/team_lead/judge) into a final panel decision (CCW-MVP12).
- Input: `{"reviews": [{reviewer, role, verdict, score, notes}], "task_ref": str, "consolidation": "majority"|"unanimous"|"weighted"}`
  - `consolidation` defaults to `"majority"`
  - majority: most common verdict wins; ties resolved by severity (fail > warn > pass)
  - unanimous: pass only if all reviewers vote pass; any warn → warn; any fail → fail
  - weighted: worker=0.3, team_lead=0.5, jud…

## Implementation
- Tool: `.claude/tools/skills/review_panel.py`
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
