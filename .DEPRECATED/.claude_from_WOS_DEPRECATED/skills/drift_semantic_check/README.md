# drift_semantic_check

**Pack:** `unclassified`

## Purpose
Semantic drift sentinel:
- Skills Registry <-> Skill Runner mismatch
- Contract drift sentinel
- SSoT path references

## Implementation
- Tool: `.claude/tools/skills/drift_semantic_check.py`
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
