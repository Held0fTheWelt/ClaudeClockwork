# clockwork_version_bump

**Pack:** `unclassified`

## Purpose
Bumps the Clockwork semver, writes a changelog entry, and optionally creates a git tag (CCW-MVP21).
- Input: `{"bump_type": "major"|"minor"|"patch", "summary": str, "affected_mvps": [str], "tag_git": bool, "dry_run": bool}`
- Output: `{"previous_version": str, "new_version": str, "changelog_entry": str, "tag_created": bool, "status": "ok"|"dry_run"|"error"}`
- Reads version from `.claude/VERSION`; writes date-stamped entry to `.claude/changelog/`; updates `.claude/CHANGELOG.md` header
- Schema:…

## Implementation
- Tool: `.claude/tools/skills/clockwork_version_bump.py`
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
