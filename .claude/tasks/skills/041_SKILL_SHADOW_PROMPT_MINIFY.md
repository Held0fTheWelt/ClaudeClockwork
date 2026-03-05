# Skill Task: shadow_prompt_minify (Shadow Prompt Skill)

## Intent
Create a `.claude_shadow/` folder containing minimal, correct prompt instructions derived from existing docs.

## Modes
- deterministic_minify (required)
- llm_refine_playbook (optional: uses configured LLM roles)

## Inputs
- source_docs: list of existing docs to compress
- shadow_root: output folder
- max_chars_per_file: cap per shadow file
- mode: deterministic_minify | llm_refine_playbook

## Outputs
- `.claude_shadow/INDEX.md`
- shadow prompt files mirroring the key docs
- shadow_prompt_report.json

## Acceptance criteria
- Preserves critical constraints (policy, file layout, "never do" rules)
- Adds explicit "Limitations / Non-goals" section in the shadow docs
