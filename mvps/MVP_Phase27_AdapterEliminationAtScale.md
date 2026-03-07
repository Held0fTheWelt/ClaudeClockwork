# MVP Phase 27 — Adapter Elimination at Scale (Batch Engine + Rollback)

**Goal:** Convert adapter-bridged skills to native implementations at scale, safely and deterministically, using a batch engine with tests, rollback, and reporting.

**Why now:** Phase 21 provides tooling. This phase operationalizes it for large batches without breaking the system.

---

## Definition of Done

- [ ] Batch engine exists to convert skills in batches (e.g. 50 at a time)
- [ ] Each batch run produces:
  - conversion report (what changed)
  - validation report (tests/qa gates)
  - rollback map for failed conversions
- [ ] Rollback is automatic when gates fail
- [ ] A deprecation plan exists for the legacy adapter layer
- [ ] All existing tests pass

---

## B27.1 — Batch Planner + Selection Rules

**Files:**
- `scripts/adapter_migrate.py` (Phase 21)
- `scripts/adapter_batch_plan.py` (new)
- `Docs/adapter_elimination_plan.md` (new)

**Change:**
- Selection rules:
  - prioritize low-risk skills first
  - exclude known edge cases until handled
- Batch sizes configurable.

**Acceptance:**
- Planner produces the same batch list for the same repo state.

---

## B27.2 — Batch Conversion + Reporting

**Files:**
- `scripts/adapter_batch_run.py` (new)
- `Docs/adapter_batch_reports.md` (new)

**Change:**
- Run conversion, then:
  - unit tests
  - qa gates
  - manifest validation
- Emit reports under runtime root.

**Acceptance:**
- Report includes: converted count, failures, reasons, next actions.

---

## B27.3 — Automatic Rollback

**Files:**
- `claudeclockwork/core/snapshot/` (or existing snapshot system)
- `scripts/adapter_batch_run.py`

**Change:**
- Create snapshot before conversion.
- If gates fail, restore snapshot and emit rollback evidence.

**Acceptance:**
- A forced failure triggers rollback and returns repo to pre-run state.

---

## B27.4 — Deprecation of Legacy Adapter Layer

**Files:**
- `Docs/legacy_adapter_deprecation.md` (new)
- `claudeclockwork/legacy/adapter.py` (existing)

**Change:**
- Define criteria to retire the adapter:
  - % native coverage threshold
  - no remaining critical skills on legacy bridge
- Add CI warning when legacy adapter is used.

**Acceptance:**
- Deprecation policy is clear and enforced gradually.

---
