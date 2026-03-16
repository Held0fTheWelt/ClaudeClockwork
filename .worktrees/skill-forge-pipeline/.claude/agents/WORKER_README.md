# Implementation Worker — Reference (CCW-MVP03)

_File: `.claude/agents/workers/implementation_worker.md` | Department: `engineering.implementation`_

---

## Purpose

The Implementation Worker writes and modifies code. It does **not** route, architect,
or perform large-scale refactors without a gate. It receives a compact `Pack + TasklistSpec`
and returns a structured JSON result.

---

## Input Format

```json
{
  "task": {
    "id": "T1",
    "acceptance": ["criterion 1", "criterion 2"]
  },
  "pack": {
    "files": ["src/foo.py", "src/bar.py"]
  },
  "trust": "inherit | verify | rebuild",
  "risk": "low | med | high"
}
```

**Trust modes:**
- `inherit` — worker trusts TasklistSpec + Pack as-is (default, cheapest).
- `verify` — worker receives an additional 10–20 line Goal/Constraints extract.
- `rebuild` — worker ignores spec and re-plans; only at `risk=high` or `confidence < 0.5`.

---

## Output Format

```json
{
  "status": "done | blocked | needs_review",
  "changed_files": ["src/foo.py"],
  "notes": "free-text rationale or blockers",
  "rerun_tests": ["pytest -q", "ruff check ."]
}
```

---

## Write Permissions

- Source code directories per project (`src/`, `oodle/`, etc.).
- No governance documents without an explicit gate.

---

## Model Assignment

| Situation | Model |
|---|---|
| Default implementation | `qwen2.5-coder:32b` or `deepseek-coder:33b-instruct-q4_K_M` |
| Small / isolated fix | `deepseek-coder:6.7b` |
| Hard reasoning needed | Escalate via TestOps/Critic — do not call directly |

---

## Activation

- Called by TeamLead after Personaler produces a RoutingSpec.
- Never called directly from user triggers.
- Tester runs immediately after Worker completes (at L1+).
