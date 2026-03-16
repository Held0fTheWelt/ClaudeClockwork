# clockwork_changelog_entry

**Pack:** `unclassified`

## Purpose
Lightweight companion to clockwork_version_bump — adds a changelog line without bumping version (CCW-MVP21).
- Input: `{"version": str, "entry_text": str, "category": "added"|"changed"|"fixed"|"removed"}`
- Output: `{"written_to": str, "status": "ok"|"error"}`
- Appends a single categorized entry to the active changelog file
- Schema: `contracts/schemas/clockwork_version_bump.schema.json` (shared)
- Example: `contracts/examples/clockwork_version_bump_example.json` (shared)

## Implementation
- Tool: `.claude/tools/skills/clockwork_changelog_entry.py`
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
