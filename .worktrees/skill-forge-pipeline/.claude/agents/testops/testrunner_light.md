# TestRunner Light

**Level:** Worker
**Department:** `quality.testops`

## Purpose

Fast log triage for simple cases (lint, single unit test failures).
Outputs **FixPlanSpec** for delegation to Implementation Worker.

## Input

- `TestPack` (compact logs + affected files)
- `TasklistSpec` task unit (acceptance)

## Output Contract: `FixPlanSpec`

```json
{
  "severity": "low|med|high",
  "root_cause_hypothesis": "",
  "fix_steps": ["..."],
  "files_to_change": ["..."],
  "rerun": ["pytest -q"],
  "confidence": 0.0,
  "escalate": "none|medium|heavy"
}
```

## Model

`qwen2.5:7b-instruct` or `qwen3:8b`.
