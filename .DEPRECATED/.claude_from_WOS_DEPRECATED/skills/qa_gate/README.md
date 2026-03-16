# qa_gate

**Pack:** `unclassified`

## Purpose
Runs the **hard QA gate** (PR-blocking fast checks):
- repo_validate + contract drift + topology + SSoT path resolution + semantic drift

## Implementation
- Tool: `.claude/tools/skills/qa_gate.py`
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
