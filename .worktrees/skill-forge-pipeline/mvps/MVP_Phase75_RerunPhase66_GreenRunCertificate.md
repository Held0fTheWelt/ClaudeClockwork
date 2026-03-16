# MVP Phase 75 — Re-run Phase 66 (Green Run Certificate) After Fixes

**Goal:** After Phase 72–74 are complete and green, repeat Phase 66 to produce a current “Green Run Certificate” proving the repo is clean, gates pass, and evidence export is redacted and share-safe.

**Prerequisites:** Phase 72, 73, 74 must be green.

---

## Definition of Done

- [ ] Phase 66 gate suite passes (MVP18+ scope)
- [ ] A new `Docs/green_run_certificate.md` is generated (stable format)
- [ ] Certificate references canonical version (SSOT) and evidence bundle id/hash
- [ ] Evidence bundle export produces a redacted manifest (no host paths)
- [ ] All existing tests pass

---

## R75.1 — Ensure Green Criteria Includes New Gates

**Files:**
- `Docs/green_criteria.md`
- `qa_gate` runner config

**Change:**
- Ensure the following are included:
  - version drift enforcement (72)
  - validation artifact leak gate (73)
  - doc policy consistency gate (74)

**Acceptance:**
- `qa_gate` lists them and runs them in stable order.

---

## R75.2 — Execute Phase 66 End-to-End

**Change:**
- Run the full green suite.
- Export evidence bundle in strict redacted mode.
- Regenerate certificate.

**Acceptance:**
- Certificate and bundle are share-safe and deterministic.

---

## Drift Prevention Instruction
If Phase 66 fails due to any of these drifts again, treat it as:
- a release-blocking regression,
- and update `Docs/drift_register.md` with a postmortem note.

---
