# Adapter Elimination Plan (Phase 27)

## Selection rules

- **Prioritize:** Low-risk skills first (no file deletion, no external calls).
- **Exclude:** Known edge cases until handled (document in batch report).
- **Batch size:** Configurable (default 50). Same repo state → same batch list (deterministic).

## Batch workflow

1. `scripts/adapter_batch_plan.py` — output list of skill ids to convert in this batch.
2. `scripts/adapter_batch_run.py` — snapshot → convert → validate (tests + qa gates) → on failure: rollback.
3. Reports under `.clockwork_runtime/adapter_batch/` (conversion report, validation report, rollback map).

## Current state

Phase 17 completed full conversion; 0 adapter skills remain. Batch tooling supports future bulk operations and rollback safety.
