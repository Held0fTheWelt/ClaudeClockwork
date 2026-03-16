# MVP Phase 66 — Re-Audit “Green Run Certificate” (MVP18+ → Current)

**Goal:** Produce a deterministic certificate proving the repo is “green”: required gates pass, evidence bundle is exportable (redacted), and the report is stable and reproducible.

**Prerequisite:** Phase 62 + 63 + 67 + 68 must be green.

---

## Definition of Done

- [x] ✅ Gate suite for scope MVP18+ runs and passes:
  - `qa_gate`
  - `planning_drift_scan`
  - `release_check`
  - docs link-lint
  - report policy gate
  - report redaction gate
  - runtime root gate
- [x] ✅ A redacted evidence bundle is exported successfully
- [x] ✅ `Docs/green_run_certificate.md` generated in stable format
- [x] ✅ Certificate includes canonical version and evidence bundle id/hash
- [x] ✅ All existing tests pass

---

## G66.1 — Define Green Criteria

**Files:**
- `Docs/green_criteria.md` (new) OR embed in certificate generator

**Change:**
- Explicitly list required gates and scope, stable ordering.

**Acceptance:**
- Green criteria doc is referenced by QA tooling.

---

## G66.2 — Certificate Generator

**Files:**
- `claudeclockwork/qa/reports/green_run.py` (new)
- `Docs/green_run_certificate.md` (generated)
- `tests/test_green_run_certificate.py`

**Change:**
- Generate stable markdown certificate referencing canonical version and gate results.

**Acceptance:**
- Re-running without changes yields identical output (except optional timestamp).

---

## G66.3 — Evidence Export Integration

**Files:**
- Evidence export pipeline (existing)

**Change:**
- Ensure export runs in strict redacted mode and certificate references bundle manifest.

**Acceptance:**
- Export produces a bundle with manifest and redaction markers.

---

## Rules to Complete (if incomplete)
- Ensure there is a single canonical list of “required gates” and where it lives.
- Ensure `qa_gate` documents its stable ordering and scoping rules.

---
