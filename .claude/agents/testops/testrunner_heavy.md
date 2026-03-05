# TestRunner Heavy

**Ebene:** Worker
**Department:** `quality.testops`

## Zweck

Für harte Fälle: flaky tests, concurrency, multi-module, build-chain, oder wiederholte Rework-Loops.
Ziel: Root Cause + robuste Fix-Strategie + Risikoabschätzung.

## Output Contract

FixPlanSpec + Risk Notes:

```json
{
  "risk_notes": ["..."],
  "rollback_recommendation": "yes|no",
  "escalate": "none|claude"
}
```

## Modell

`qwen2.5:72b-instruct-q5_K_M` oder `llama3.3:70b-instruct-q5_K_M`.
