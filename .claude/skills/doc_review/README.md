# doc_review

Deterministic doc lint review (TODOs, missing sections, broken local links, headings).

## Implementation
- Tool: `.claude/tools/skills/doc_review.py`
- Contracts (schemas/examples): `.claude/contracts/`

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in <request.json> --out <result.json>
```

## Constraints / Non-Goals
- This skill is deterministic and performs no semantic "truth verification" of content.
- For content quality: use the appropriate playbooks (Explore/Write/Critic/DecideGap).
