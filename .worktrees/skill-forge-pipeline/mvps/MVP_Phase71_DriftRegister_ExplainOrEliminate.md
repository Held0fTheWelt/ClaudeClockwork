# MVP Phase 71 — Drift Explanation or Elimination (Document the Why, Then Enforce)

**Goal:** Stop recurring drift from “always being carried along” by requiring every recurring drift type to be either:
- eliminated, or
- explicitly justified with a stable rule and a gate.

This phase is about **institutionalizing** the fix so the same issues do not recur (version drift, report/runtime confusion, perf artifact pollution, host-path leaks).

---

## Definition of Done

- [x] ✅ A single “Drift Register” exists documenting recurring drifts:
  - what drift is
  - why it happened
  - whether it is allowed (and why) or forbidden
  - what gate prevents it
  - what to do when it triggers
- [x] ✅ The following drifts are addressed:
  - VERSION vs `.claude/VERSION` mismatches
  - `.report/` pollution
  - `.claude-performance/` pollution
  - absolute host path leaks in curated docs
- [x] ✅ Gates exist and are wired into `qa_gate` / CI (PERF_001, DOC_PATH_001 added to CHECKS)
- [x] ✅ Green Run certificate (Phase 66) updated to 9 gates; drift register gates block recurrence
- [x] ✅ All existing tests pass

---

## D71.1 — Create Drift Register

**Files:**
- `Docs/drift_register.md` (new)

**Change:**
For each drift type, record:
- **Symptom** (how it appears)
- **Root cause** (why it happened historically)
- **Decision** (forbidden vs allowed-with-constraints)
- **Prevention** (gate name + scope)
- **Remediation** (what steps to take)

**Acceptance:**
- Register is concise, actionable, and referenced by policies.

---

## D71.2 — Ensure All Relevant Gates Are Linked

**Files:**
- `Docs/green_criteria.md` (or gate suite doc)
- `claudeclockwork/core/gates/*`
- `.claude/tools/skills/qa_gate.py` (or gate runner)

**Change:**
- Add the new gates from Phases 69–70 plus existing drift/report/version gates.
- Ensure stable ordering and clear output.

**Acceptance:**
- Running qa_gate lists the drift-related gates and their results.

---

## D71.3 — Explain or Eliminate Requirement

**Policy Change:**
- If a drift keeps recurring, future PRs must include either:
  - removal of the drift source, or
  - an explicit documented rationale in the drift register plus a gate.

**Acceptance:**
- Drift register contains explicit “why it exists” for any allowed drift.
- Forbidden drifts have gates that block them.

---
