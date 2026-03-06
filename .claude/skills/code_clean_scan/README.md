# code_clean_scan

**Pack:** `core`

## Purpose
Deterministic code cleaning scanner:
- builds a lightweight import graph (Python)
- finds orphan modules and unregistered skill modules
- flags markers (deprecated/todo/legacy/path drift)
- outputs a conservative report with limitations

## Implementation
- Tool: `.claude/tools/skills/code_clean_scan.py`
- Skill runner: `.claude/tools/skills/skill_runner.py`
- Contracts: `.claude/contracts/`

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in <request.json> --out <result.json>
```

## Outputs
Describe output files and write locations here.

## Constraints / Non-Goals
- Deterministic: no semantic "truth verification" of content.
- Can produce candidate lists, but cannot prove that something is obsolete.
- If LLM refinement is needed: use the appropriate playbook (Explore/Write/Critic/DecideGap).
