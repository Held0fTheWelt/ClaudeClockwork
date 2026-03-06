# refactor_bridge_scan

**Pack:** `unclassified`

## Purpose
Scans a repo for legacy markers (`src/`, `.claude/`, `claude-documents/`, etc.) and suggests refactor bridge steps.

## Implementation
- Tool: `.claude/tools/skills/refactor_bridge_scan.py`
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
