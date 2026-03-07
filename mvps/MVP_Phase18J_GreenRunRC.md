# MVP Phase 18J — Gate Stabilization & “Green Run” (RC Minimum)

**Goal:** Produce a deterministic “Green Run” where all required gates pass, and generate a signed-off certificate doc that records versions, gate outputs, and evidence bundle references.

---

## Definition of Done

- [ ] `qa_gate` passes on scope MVP18+
- [ ] `planning_drift_scan` passes
- [ ] `release_check` passes
- [ ] docs link-lint passes
- [ ] curated report policy passes
- [ ] a redacted evidence bundle can be exported successfully
- [ ] `Docs/green_run_certificate.md` is generated (stable format)
- [ ] All existing tests pass

---

## 18J.1 — Gate Suite Definition

**Files:**
- `Docs/green_criteria.md` (new) OR embed into certificate
- Gate runner config

**Change:**
- Define the exact gate list that constitutes “green”.

**Acceptance:**
- Gate suite is consistent and stable-ordered.

---

## 18J.2 — Evidence Bundle Export

**Files:**
- Export pipeline (Phase 23)
- `Docs/green_run_certificate.md`

**Change:**
- Ensure export runs in “redacted-only” mode.

**Acceptance:**
- Certificate references bundle id/hash and runtime path.

---

## 18J.3 — Certificate Generator

**Files:**
- `Docs/green_run_certificate.md` (generated)
- `claudeclockwork/qa/reports/green_run.py` (new) or integrated

**Change:**
- Record:
  - timestamp (optional)
  - canonical version
  - gate results summary
  - links/paths to evidence bundle

**Acceptance:**
- Re-running without changes produces identical certificate (except optional timestamp).

---
