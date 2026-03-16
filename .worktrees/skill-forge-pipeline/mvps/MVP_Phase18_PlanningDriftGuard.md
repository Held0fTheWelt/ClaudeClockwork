# MVP Phase 18 — Planning Drift Guard & Single Source of Truth

**Goal:** Eliminate planning/status/version drift across Clockwork. Ensure that roadmaps, MVP trackers, milestone indexes, and version markers cannot disagree without failing a deterministic gate.

**Source findings (repo scan 2026-03-07):**
- Root `ROADMAP.md` often lags behind `mvps/` reality.
- `.claude-development/milestones/index.md` may link to missing plan files.
- Version markers can disagree: `VERSION` vs `.claude/VERSION` vs roadmap header versions.
- `Docs/skill_system_audit_and_roadmap.md` can become stale vs current phase set and inventory.

---

## Definition of Done

- [x] Root `ROADMAP.md` updated to reflect the current phase reality (Phase0..latest) and correct inventory numbers
- [x] `Docs/skill_system_audit_and_roadmap.md` updated (header points to canonical roadmap + mvps)
- [x] `.claude/development/MVP_STATUS.md` updated (date + cross-links + Phase roadmap mapping)
- [x] `.claude-development/milestones/index.md` has no dead links (frozen as legacy; M1/M2 plan file links removed)
- [x] New deterministic drift checker added: `planning_drift_scan` in `claudeclockwork.core.gates`
- [x] `qa_gate` extended with DRIFT_001 to fail when drift is detected
- [x] All existing tests pass

---

## P18.1 — Canonical Planning Map

**Finding:** Roadmaps and trackers drift out of sync with actual MVP Phase files.

**Files:**
- `ROADMAP.md`
- `roadmaps/Roadmap_ClockworkV18.md`
- `.claude/development/MVP_STATUS.md`
- `mvps/MVP_Phase*.md`

**Change:**
- Declare the canonical planning source of truth (recommendation: `roadmaps/Roadmap_ClockworkV18.md` + `mvps/`).
- Update `ROADMAP.md` to point to the canonical roadmap and summarize Phase0..latest status.
- Update `.claude/development/MVP_STATUS.md` with a short “Phase roadmap mapping” section.

**Acceptance:**
- No doc claims a phase is planned if its Phase MVP is complete (and vice versa).
- All internal links resolve.

---

## P18.2 — Version Marker Convergence

**Finding:** Multiple version files disagree.

**Files:**
- `VERSION`
- `.claude/VERSION`
- `.claude/CHANGELOG.md`
- `roadmaps/Roadmap_ClockworkV18.md`

**Change:**
- Choose a single canonical version location and define propagation rules.
- Add a deterministic check: if versions disagree, fail the drift gate with a clear diff.
- Align “current version” in roadmap headers to the canonical version.

**Acceptance:**
- A single canonical version is surfaced by a check command or script.
- Any mismatch fails the gate with an actionable message.

---

## P18.3 — Milestone Index Integrity

**Finding:** Milestone index links to non-existent plan files.

**Files:**
- `.claude-development/milestones/index.md`
- `.claude-development/milestones/*.md`

**Change (choose one approach, but make it explicit):**
A) Restore the missing plan files (rehydrate M1/M2 plans into the repo), OR  
B) Freeze the `.claude-development` milestone system as legacy and remove dead links, pointing to the Phase MVP system instead.

**Acceptance:**
- Link-lint reports zero broken internal links.

---

## P18.4 — Planning Drift Scan Gate

**Finding:** Drift reappears because nothing enforces it.

**Files:**
- `claudeclockwork/core/gates/` (or existing gate module)
- `tests/test_gates.py` (or existing gate tests)

**Change:**
Implement `planning_drift_scan` that checks:
- broken links in key docs
- version mismatches
- milestone index link existence
- roadmap phase list matches `mvps/MVP_Phase*.md`

Integrate into `qa_gate` / CI gates.

**Acceptance:**
- A deliberate broken link causes gate failure.
- A deliberate version mismatch causes gate failure.
- Clean repo passes.

---
