# Message Triad Protocol (DE → EN + Work Brief)

Goal: reduce token spend and rereads by standardizing every incoming user message into a **Triad**:

1) **source**: original message (e.g., German, narrative)
2) **translation**: faithful English translation
3) **work_brief**: compact English work request for the target agent

## Default processing order
- Use `work_brief` first.
- If blocked/ambiguous, fallback to `translation`.
- Only if still blocked, read `source`.

## Integration with existing components
- **Translator (local Oodle)** produces `translation` + draft `work_brief`.
- **Content Compactor** produces `context_pack.compactor_shortlist` (small, structured).
- **Content Packer** produces per-agent packs from `work_brief + shortlist`.
- **Personaler** routes/staffs using `work_brief + shortlist` (fallback only if needed).

## Hard limits (cost control)
- Work brief is capped by `budget.max_words` (recommended 250–400).
- Tasks in work brief must respect `planning.max_plan_tasks` (8–12).

## Blocked definition (deterministic)
A consumer agent must request fallback if any of these is true:
- required fields missing (goal/tasks/acceptance)
- contradictory constraints
- tasks > max_plan_tasks
- scope mismatch (wrong agent)


## Small tasks
If a task is tiny, set a tighter budget:
- `budget.max_chars` (e.g., 300–900)
- and/or smaller `budget.max_words`.
