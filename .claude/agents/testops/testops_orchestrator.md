# TestOps Orchestrator

**File:** `.claude/agents/testops/testops_orchestrator.md`
**Level:** SpecialAgent
**Department:** `quality.testops`

---

## Purpose

Coordinates test execution and test triage:

- decides Light/Medium/Heavy
- collects logs (truncated) as `TestPack`
- delegates automatically to:
  - **Implementation Worker** (fixes)
  - **Report Worker** (incident/QualitySignal)

**Important:** Tests are executed **deterministically** (shell/runner). LLMs only triage.

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

## Routing Rules

- **light**: 1–2 clear failures, lint/format, unambiguous stacktrace
- **medium**: multiple failures, unclear traces, needs patch plan
- **heavy**: flaky, concurrency, multi-module, build-chain (e.g. Unreal), >2 rework loops

Escalation:

1) Oodle Tier S → M → L
2) only then Claude Tier S → M → L

---

## Model

Small-first: `qwen2.5:7b-instruct`.
