# MVP Phase 22 — Release Discipline & Upgrade Pipeline

**Goal:** Make releases boring and deterministic: one canonical version source, automated release notes, and an upgrade pipeline that prevents version/changelog drift.

**Why now:** After Phase 18 (drift guard), we need a consistent “version + release” story to avoid silent divergence across `VERSION`, `.claude/VERSION`, roadmaps, and docs.

---

## Definition of Done

- [ ] A single canonical version source is chosen and documented
- [ ] All secondary version markers are derived from the canonical source (or removed)
- [ ] Release notes generation exists (deterministic, repo-local)
- [ ] `release_check` gate fails on:
  - missing changelog entry for a version bump
  - mismatched version markers
  - missing migration notes when required
- [ ] A short “Upgrade Playbook” exists
- [ ] All existing tests pass

---

## R22.1 — Canonical Version Source

**Files:**
- `.claude/VERSION` (recommended) or `VERSION` (if preferred)
- `Docs/versioning.md` (new)

**Change:**
- Define canonical version file and its semantic meaning (product version vs build number).
- Define propagation rules for any derived copies.

**Acceptance:**
- One command prints the canonical version and verifies consistency.

---

## R22.2 — Changelog Fragments + Deterministic Merge

**Files:**
- `.claude/changelog_fragments/` (new)
- `.claude/CHANGELOG.md` (existing)

**Change:**
- Add a fragment convention (`added/`, `changed/`, `fixed/`, `security/`).
- Add a deterministic “compile fragments → changelog section” tool.

**Acceptance:**
- Running the compiler twice produces identical output.

---

## R22.3 — Release Check Gate

**Files:**
- `claudeclockwork/core/gates/release_check.py` (or existing gate module)
- `tests/test_release_check.py`

**Change:**
- Implement `release_check` gate:
  - ensures version bump has changelog entry
  - ensures no version marker drift
  - ensures optional migration note when breaking changes are detected

**Acceptance:**
- A deliberate mismatch fails the gate with a precise error.

---

## R22.4 — Upgrade Playbook

**Files:**
- `Docs/upgrade_playbook.md`

**Change:**
- Write a step-by-step procedure for upgrading Clockwork versions, including:
  - runtime migration steps
  - how to run validation/eval
  - how to create a redacted export bundle

**Acceptance:**
- Playbook is short, executable, and repo-local.

---
