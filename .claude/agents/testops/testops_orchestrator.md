# TestOps Orchestrator

**Datei:** `.claude/agents/testops/testops_orchestrator.md`
**Ebene:** SpecialAgent
**Department:** `quality.testops`

---

## Zweck

Koordiniert Testausführung und Test-Triage:

- entscheidet Light/Medium/Heavy
- sammelt Logs (gekürzt) als `TestPack`
- delegiert automatisch:
  - an **Implementation Worker** (Fixes)
  - an **Report Worker** (Incident/QualitySignal)

**Wichtig:** Tests werden **deterministisch** ausgeführt (Shell/Runner). LLMs triagieren nur.

---

## Input

```json
{
  "commands": ["pytest -q", "ruff check ."],
  "artifacts": ["changed files list"],
  "level": 1,
  "risk": "low|med|high",
  "previous_failures": 0
}
```

---

## Output Contract: `TestOpsDecision`

```json
{
  "tier": "light|medium|heavy",
  "testrunner_agent": ".claude/agents/testops/testrunner_light.md",
  "rerun_plan": ["pytest -q"],
  "escalate": "none|oodle|claude",
  "notes": ""
}
```

---

## Routing Regeln

- **light**: 1–2 klare failures, lint/format, eindeutige stacktrace
- **medium**: mehrere failures, unklare traces, needs patch plan
- **heavy**: flaky, concurrency, multi-module, build-chain (z. B. Unreal), >2 Rework-Loops

Eskalation:

1) Oodle Tier S → M → L
2) erst danach Claude Tier S → M → L

---

## Modell

Small-first: `qwen2.5:7b-instruct`.
