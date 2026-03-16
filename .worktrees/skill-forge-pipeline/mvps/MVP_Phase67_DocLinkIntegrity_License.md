# MVP Phase 67 — Doc Link Integrity + License

**Goal:** Eliminate broken internal links in top-level docs and add a clear repository license/status file. This improves trust, automation, and onboarding.

**Observed (repo scan 2026-03-08):**
- `README.md` links to `QUALITY_TRACKING.md` but file lives at `.project/QUALITY_TRACKING.md`.
- `README.md` links to `LICENSE` which is missing.

---

## Definition of Done

- [x] ✅ Link-lint reports zero broken links (excluding runtime root)
- [x] ✅ `README.md` references the correct quality tracking doc path (or a root pointer exists)
- [x] ✅ A `LICENSE` file exists (or an explicit `UNLICENSED`/proprietary notice is provided)
- [x] ✅ All existing tests pass

---

## L67.1 — Quality Tracking Link Fix

**Options (choose one, prefer pointer):**
A) Create root `QUALITY_TRACKING.md` as a pointer to `.project/QUALITY_TRACKING.md`
B) Update `README.md` to point to `.project/QUALITY_TRACKING.md`

**Acceptance:**
- The link resolves and is stable.

---

## L67.2 — Add `LICENSE` (or Explicit Unlicensed Notice)

**Change:**
- Add a `LICENSE` file appropriate for your project:
  - MIT/Apache-2.0/GPL-3.0/etc., OR
  - `UNLICENSED` / proprietary notice

**Acceptance:**
- `README.md` license link resolves.
- License status is unambiguous.

---

## Rules to Complete (if incomplete)
- If you choose “UNLICENSED/proprietary”, ensure docs explicitly state redistribution rules.
- Add a short section in `Docs/INDEX.md` or `README.md` clarifying license + contribution policy.

---
