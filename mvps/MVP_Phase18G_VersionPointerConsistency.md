# MVP Phase 18G — Version & Pointer Consistency (DRIFT_001 + POINTER_001)

**Goal:** Eliminate planning/version drift and missing `.claude/` pointer docs that cause gates to fail.

---

## Definition of Done

- [ ] `VERSION` and `.claude/VERSION` are consistent per policy (or root VERSION removed with documented policy change)
- [ ] Pointer docs exist under `.claude/`:
  - `.claude/ARCHITECTURE.md`
  - `.claude/ROADMAP.md`
  - `.claude/MODEL_POLICY.md`
- [ ] `planning_drift_scan` passes
- [ ] Pointer/link gate passes
- [ ] All existing tests pass

---

## 18G.1 — Version Canonicalization

**Files:**
- `VERSION`
- `.claude/VERSION`
- `Docs/versioning.md` (if present)

**Change:**
- Choose canonical version source and make all other markers derive from it.

**Acceptance:**
- Drift scan reports zero version mismatches.

---

## 18G.2 — `.claude/` Pointer Docs

**Files:**
- `.claude/ARCHITECTURE.md`
- `.claude/ROADMAP.md`
- `.claude/MODEL_POLICY.md`

**Change:**
- Create pointer docs (short) that redirect to root equivalents.

**Acceptance:**
- Pointer gate reports zero missing required pointers.

---
