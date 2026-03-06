# shadow_prompt_minify

**Pack:** `core`

## Purpose
Shadow prompt generator:
- builds `.claude_shadow/` with condensed prompt instructions
- deterministic minify + optional LLM refinement playbook
- produces a quality gap report

## Implementation
- Tool: `.claude/tools/skills/shadow_prompt_minify.py`
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
