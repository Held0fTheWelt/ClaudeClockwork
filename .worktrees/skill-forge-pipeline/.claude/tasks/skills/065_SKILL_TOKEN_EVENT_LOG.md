# Skill Task: token_event_log

## Intent
Write a single `budget_event` JSONL line for token attribution by role/model/task.

## Acceptance
- deterministic append-only logging
- creates events file if missing
- used by wrappers at the end of each agent action
