# MVP Phase 18F — Re-Audit from MVP 18 (Quality Gates Baseline)

**Goal:** Re-run and formalize *all* quality gates from MVP 18 onward, producing a deterministic, stable-ordered audit report that maps each failing gate to a dedicated fix MVP (18G–18J).

**Why now:** The project evolved; “implemented MVPs” must be validated by gates. We need a single, repeatable entry point that makes drift and missing artifacts visible.

---

## Definition of Done

- [ ] `qa_gate` is runnable deterministically (imports and repo-root sys.path fixed)
- [ ] Gates are executed for scope “from MVP 18 onward”
- [ ] Output report generated: `Docs/quality_reaudit_from_mvp18.md`
- [ ] Report is stable-ordered and includes:
  - gate id
  - severity (blocker/non-blocker)
  - file paths involved
  - recommended fix MVP id (18G/18H/18I/18J)
- [ ] Report includes a “Green Criteria” section describing required gates for release candidate
- [ ] All existing tests pass

---

## 18F.1 — Make qa_gate Import-Safe

**Files:**
- `.claude/tools/skills/qa_gate.py`
- `.claude/tools/skills/skill_runner.py` (if needed)

**Change:**
- Ensure repo root is inserted into `sys.path` before importing `claudeclockwork.*`.

**Acceptance:**
- Running `qa_gate` does not fail due to import errors.

---

## 18F.2 — Gate Execution Scope (MVP18+)

**Files:**
- `claudeclockwork/core/gates/*` (or existing gates)
- `.claude/tools/skills/qa_gate.py`

**Change:**
- Define gate list and scoping rule:
  - gates that were introduced/required from MVP 18 onward
- Allow `--scope mvp18_plus`.

**Acceptance:**
- Gate output includes a scope header and deterministic gate ordering.

---

## 18F.3 — Report Generator

**Files:**
- `Docs/quality_reaudit_from_mvp18.md` (generated)
- `claudeclockwork/qa/reports/re_audit.py` (new) or integrated into gate runner

**Change:**
- Write a stable markdown report.

**Acceptance:**
- Re-running produces identical report (except timestamps if included).

---
