# TestRunner Medium

**Ebene:** Worker
**Department:** `quality.testops`

## Zweck

Triage für mehrere Failures, unklare Traces, oder wenn Light nicht reicht.
Erstellt einen konkretisierten FixPlanSpec (inkl. minimaler Patch-Strategie).

## Output

Wie Light, aber zusätzlich:

```json
{
  "suggested_patch": {
    "strategy": "",
    "key_edits": ["..."]
  }
}
```

## Modell

`phi4:14b` oder `qwen2.5:14b-instruct`.
