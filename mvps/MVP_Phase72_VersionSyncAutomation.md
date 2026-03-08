# MVP Phase 72 — Version Sync Automation (Kill DR-001 Permanently)

**Goal:** Make version drift impossible. No commit/release/green run may leave `VERSION` and `.claude/VERSION` inconsistent (or eliminate one of them cleanly).

**Observed (repo scan 2026-03-08):**
- Root `VERSION` and `.claude/VERSION` still drift.

---

## Definition of Done

- [ ] A single SSOT is chosen and documented (recommended: `.claude/VERSION`)
- [ ] Drift is prevented automatically, not manually:
  - either an auto-sync step exists, or
  - the non-SSOT file is removed and policies updated
- [ ] Gates enforce SSOT:
  - `planning_drift_scan` blocks mismatches
  - `release_check` uses SSOT only
- [ ] A remediation command exists (`clockwork version sync` or similar)
- [ ] All existing tests pass

---

## V72.1 — SSOT Decision + Policy Update

**Files:**
- `Docs/versioning.md`
- `Docs/drift_register.md`

**Change:**
- Explicitly declare:
  - SSOT file
  - whether mirrors exist (and why)
  - how build metadata is handled

**Acceptance:**
- Docs contain a single unambiguous rule.

---

## V72.2 — Auto-Sync Mechanism

**Option A (preferred): keep both, auto-sync mirrors**
**Files:**
- `claudeclockwork/cli/version.py` (new/extend)
- `claudeclockwork/core/gates/planning_drift_scan.py`

**Change:**
- Implement `clockwork version sync`:
  - reads SSOT
  - rewrites mirror file(s)
  - emits a short report
- Integrate into:
  - `qa_gate` (pre-step) OR
  - `release_check` (pre-step) OR
  - a developer workflow script

**Acceptance:**
- Running sync twice is idempotent.
- Sync is deterministic.

**Option B: eliminate the mirror file**
- Remove root `VERSION` (or `.claude/VERSION`) and update gates/docs accordingly.

**Acceptance:**
- No drift is possible because only one file remains.

---

## V72.3 — Gate Tightening

**Files:**
- Drift gate tests

**Change:**
- Ensure `planning_drift_scan`:
  - fails on mismatch
  - prints precise diff
  - is always included in green criteria

**Acceptance:**
- A mismatch cannot pass any “green run”.

---

## Drift Prevention Instruction
This phase must ensure DR-001 never returns:
- If it recurs, treat it as a release-blocking regression.
- Update the drift register to include the new prevention mechanism.

---
