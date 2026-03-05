# Task: Translate Triad (Local Oodle)

## Goal
Fill in:
- `translation.text` (faithful EN)
- `work_brief` (EN, compact, structured)

## Inputs
- MessageTriadSpec (with source)

## Rules
- Keep `work_brief` under `budget.max_words`
- Preserve code blocks (do not translate code)

## Output
- Updated MessageTriadSpec with translation + work_brief
