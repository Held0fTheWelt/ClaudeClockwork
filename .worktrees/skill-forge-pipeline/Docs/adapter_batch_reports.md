# Adapter Batch Reports (Phase 27)

Reports are written under `.clockwork_runtime/adapter_batch/`:

- **conversion_report.json** — converted count, failures, validation_pass, rollback flag.
- **rollback_map.json** — written when rollback runs; contains `restored_from` snapshot path.
- **pre_run_snapshot/** — directory snapshot before conversion (used for rollback).

## Report fields

- `converted`: list of skill ids converted.
- `failures`: list of failure reasons.
- `validation_pass`: true if tests/gates passed after conversion.
- `rollback`: true if snapshot was restored due to failure.
- `planned`: (dry-run) list of skill ids that would be converted.

## Next actions

After a run: if rollback occurred, fix failures and re-run. If success, run next batch or confirm full elimination.
