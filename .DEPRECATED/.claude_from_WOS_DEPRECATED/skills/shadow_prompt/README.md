# shadow_prompt_minify (Shadow Prompts Skill)

Create a **shadow folder** with **shorter, cheaper, still-correct** prompt instructions derived from your existing `.claude` docs.

## Skill ID
- `shadow_prompt_minify`

## Modes
- `deterministic_minify` (implemented): rule-based extraction + compression
- `llm_refine_playbook` (playbook-defined): optional multi-model refinement (Oodle -> Sonnet -> Opus)

## Outputs
- Writes shadow prompt files under `shadow_root` (default: `.claude_shadow/`)
- Creates an index: `.claude_shadow/INDEX.md`
- Produces a `shadow_prompt_report.json` with a conservative quality-gap estimate

## Deterministic minify approach
- Keep: top-level purpose, must-follow rules, file layout, required commands, acceptance criteria.
- Drop: repetition, long prose, historical notes (unless marked canonical).
- Preserve: critical constraints & "limitations / non-goals" sections.

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in .claude/contracts/examples/shadow_prompt_minify.skill_request.example.json --out out.json
```

## Limitations
- Deterministic compression cannot reach "perfect machine-level prompts" alone.
- Use the playbook for LLM-based refinement and evaluation if needed.
