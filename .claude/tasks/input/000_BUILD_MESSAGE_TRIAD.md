# Task: Build Message Triad (tool-first)

## Goal
Wrap a narrative user message into a MessageTriadSpec with explicit fallbacks.

## How
Run skill `triad_build` with:
- source_text (original)
- source_lang (de)
- primary_agent (e.g., personaler)
- optional: translation/work_brief if already available

## Output
- MessageTriadSpec JSON (skill output)

## Next steps
- Translator (Local Oodle) fills `translation` and draft `work_brief`.
- Content Compactor produces `context_pack.compactor_shortlist`.
