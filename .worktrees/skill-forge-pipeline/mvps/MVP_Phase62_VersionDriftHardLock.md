# MVP Phase 62 — Version & Drift Hard Lock

**Goal:** Eliminate version drift and make it impossible to reintroduce: define a single canonical version source and enforce it via gates.

**Observed drift (repo scan 2026-03-08):**
- Root `VERSION` and `.claude/VERSION` disagree.

---

## Definition of Done

- [ ] A single canonical version file is chosen and documented
- [ ] All secondary version markers either derive from canonical source, or are removed with updated policy docs
- [ ] `planning_drift_scan` fails on mismatches and passes when aligned
- [ ] `release_check` uses canonical version source
- [ ] All existing tests pass

---

## V62.1 — Canonical Version Source

**Files:**
- `.claude/VERSION` (recommended) OR `VERSION`
- `Docs/versioning.md`

**Change:**
- Declare canonical version source.
- Define rules for any other version files.

**Acceptance:**
- A single CLI or script returns the canonical version and verifies consistency.

---

## V62.2 — Drift Gate Enforcement

**Files:**
- `claudeclockwork/core/gates/planning_drift_scan.py` (or existing)
- `tests/test_planning_drift_scan.py`

**Change:**
- Ensure the gate explicitly checks:
  - canonical version source matches all required mirrors
  - no extra version files exist untracked by policy

**Acceptance:**
- Synthetic mismatch fails with a precise diff.

---

## V62.3 — Release Integration

**Files:**
- `claudeclockwork/core/gates/release_check.py` (or existing)

**Change:**
- Ensure release uses canonical version value, not a stale copy.

**Acceptance:**
- Release check output includes canonical version and passes when aligned.

---

## Rules to Complete (if incomplete)
- Ensure `Docs/versioning.md` explicitly states:
  - canonical version file
  - whether root `VERSION` is required or forbidden
  - how build numbers (if any) are handled
- Ensure `release_check` policy references this doc.

---
