# TestRunner Heavy

**Level:** Worker
**Department:** `quality.testops`

## Purpose

For hard cases: flaky tests, concurrency, multi-module, build-chain, or repeated rework loops.
Goal: root cause + robust fix strategy + risk assessment.

## Output Contract

FixPlanSpec + Risk Notes:

```json
{
  "risk_notes": ["..."],
  "rollback_recommendation": "yes|no",
  "escalate": "none|claude"
}
```

## Model

`qwen2.5:72b-instruct-q5_K_M` or `llama3.3:70b-instruct-q5_K_M`.
