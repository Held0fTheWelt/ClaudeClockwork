# TestRunner Light

**Ebene:** Worker
**Department:** `quality.testops`

## Zweck

Schnelle Log-Triage für einfache Fälle (Lint, einzelne Unit-Test-Fails).
Gibt **FixPlanSpec** zur Delegation an Implementation Worker aus.

## Input

- `TestPack` (kompakte Logs + betroffene Dateien)
- `TasklistSpec` Task Unit (acceptance)

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

## Modell

`qwen2.5:7b-instruct` oder `qwen3:8b`.
