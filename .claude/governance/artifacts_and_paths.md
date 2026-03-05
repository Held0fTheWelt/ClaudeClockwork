# Artifacts & Paths Standard (Canonical)

Use these standard paths under an evidence run folder (e.g. `validation_runs/YYYY-MM-DD/`):

## Reports
- `reports/decision_feedback.json`
- `reports/policy_gate_decision.json`
- `reports/autotune_suggestion.json`
- `reports/drift_sentinel.json`
- `reports/deliberation_pack.json`

## Knowledge (repo-level)
- `knowledge/outcome_ledger.jsonl`
- `knowledge/route_profiles.json`

## Notes
- Prefer relative paths.
- Avoid host-specific paths like `/mnt/d/...`.
