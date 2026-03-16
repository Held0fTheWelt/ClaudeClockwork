# Implementation Worker

**File:** `.claude/agents/workers/implementation_worker.md`
**Level:** Worker
**Department:** `engineering.implementation`

---

## Purpose

Writes and modifies code based on:

- `TasklistSpec` (single task unit)
- `Pack` (relevant files/excerpts)
- `Acceptance` (checklist)

The Worker should **not** route, architect, or perform large-scale refactors without a gate.

---

## Input

```json
{
  "task": {"id":"T1","acceptance":["..."]},
  "pack": {"files": ["..."]},
  "trust": "inherit|verify|rebuild",
  "risk": "low|med|high"
}
```

---

## Output

```json
{
  "status": "done|blocked|needs_review",
  "changed_files": ["path1", "path2"],
  "notes": "",
  "rerun_tests": ["pytest -q", "ruff check ."]
}
```

---

## Write Rights

- Code (depending on project): `src/`, `oodle/`, etc.
- No governance documents without a gate

---

## Model

- Default: `qwen2.5-coder:32b` or `deepseek-coder:33b-instruct-q4_K_M`
- Small fixes: `deepseek-coder:6.7b`
- Hard reasoning: escalate via TestOps/Critic first, do not call directly
