# doc_write

Deterministic doc persistence (single/multi-file) + unified diffs.

## Implementation
- Tool: `.claude/tools/skills/doc_write.py`
- Contracts (schemas/examples): `.claude/contracts/`

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in <request.json> --out <result.json>
```

## Constraints / Non-Goals
- This skill is deterministic and performs no semantic "truth verification" of content.
- For content quality: use the appropriate playbooks (Explore/Write/Critic/DecideGap).
