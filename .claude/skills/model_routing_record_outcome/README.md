# model_routing_record_outcome

**Pack:** `addon:model_routing_personaler`

## Purpose
Update routing hit list stats after a run (success/quality/tokens per task_type).

## Implementation
- Tool: `.claude/tools/skills/model_routing_record_outcome.py`
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
