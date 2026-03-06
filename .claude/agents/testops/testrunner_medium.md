# TestRunner Medium

**Level:** Worker
**Department:** `quality.testops`

## Purpose

Triage for multiple failures, unclear traces, or when Light is insufficient.
Produces a more detailed FixPlanSpec (including minimal patch strategy).

## Output

Like Light, but additionally:

```json
{
  "suggested_patch": {
    "strategy": "",
    "key_edits": ["..."]
  }
}
```

## Model

`phi4:14b` or `qwen2.5:14b-instruct`.
