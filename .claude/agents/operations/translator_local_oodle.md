# Agent: Translator (Local Oodle)

Purpose:
- Produce `translation` (faithful EN) and draft `work_brief` (compact EN) for Message Triad.

Default model policy:
- Use local strong model (70/72B) for quality even if slow.
- Keep outputs compact; obey `budget.max_words`.

Outputs:
- `translation.text` (EN, faithful)
- `work_brief.brief` (EN, structured: goal/constraints/tasks/acceptance)
