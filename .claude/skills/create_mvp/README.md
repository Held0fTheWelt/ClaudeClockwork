# create_mvp

**Pack:** `unclassified`

## Purpose
Autonomously creates new MVP entries in the Clockwork MVP chain (CCW-MVP20).
- Input: `{"trigger": "user_instruction"|"audit_gap"|"defect"|"parity_scan"|"manual", "trigger_ref": str|null, "mvp_name": str|null, "domain": str, "scope": [str], "dry_run": bool}`
- Output: `{"mvp_id": str, "mvp_entry": str, "written_to": str|null, "status": "ok"|"dry_run"|"error"}`
- Reads chain file to determine next MVP number; appends using atomic write (.tmp → rename)
- Logs creation to `.claude-development/audit…

## Implementation
- Tool: `.claude/tools/skills/create_mvp.py`
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
