# route_profile_update

**Pack:** `unclassified`

## Purpose
Updates a local route profiles knowledge file (best routes).

## Implementation
- Tool: `.claude/tools/skills/route_profile_update.py`
- Skill runner: `.claude/tools/skills/skill_runner.py`
- Contracts: `.claude/contracts/`

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in <request.json> --out <result.json>
```

## Outputs
Describe output files and write locations here.

## Constraints / Non-goals
- Deterministic: no semantic "truth verification" over content.
- Can provide candidate lists, but cannot prove that something is obsolete.
- If LLM refinement is needed: use the appropriate playbook (Explore/Write/Critic/DecideGap).
