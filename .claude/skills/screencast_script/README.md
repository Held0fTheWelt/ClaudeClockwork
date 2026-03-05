# screencast_script

Spec-first screencast script writer (chapters + shot list) + diffs.

## Implementation
- Tool: `.claude/tools/skills/screencast_script.py`
- Contracts (schemas/examples): `.claude/contracts/`

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in <request.json> --out <result.json>
```

## Grenzen / Nicht-Ziele
- Dieser Skill ist deterministisch und macht keine semantische "Wahrheitsprüfung" über Inhalte.
- Für inhaltliche Perfektion: nutze die jeweiligen Playbooks (Explore/Write/Critic/DecideGap).
