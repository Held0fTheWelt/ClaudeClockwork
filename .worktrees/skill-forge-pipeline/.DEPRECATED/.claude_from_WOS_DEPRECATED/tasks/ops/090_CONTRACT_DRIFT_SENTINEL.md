# Task: Contract Drift Sentinel (No-LLM friendly)

## Goal
Detect drift between schemas, examples, and task references.

## How
Run skill `contract_drift_sentinel` with root `.claude`.

## Output
- list of invalid examples (if any)
- list of missing schema references in tasks (if any)

## Notes
This is safe to run in No-LLM mode.
