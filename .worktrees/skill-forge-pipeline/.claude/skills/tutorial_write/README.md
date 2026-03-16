# tutorial_write

Spec-first tutorial renderer + section validation + diffs.

## Implementation
- Tool: `.claude/tools/skills/tutorial_write.py`
- Contracts (schemas/examples): `.claude/contracts/`

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in <request.json> --out <result.json>
```

## Constraints / Non-goals
- This skill is deterministic and does not perform semantic "truth verification" over content.
- For content perfection: use the appropriate playbooks (Explore/Write/Critic/DecideGap).
