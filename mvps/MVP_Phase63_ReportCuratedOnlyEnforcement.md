# MVP Phase 63 — `.report/` Curated-Only Enforcement + Runtime Migration

**Goal:** Restore `.report/` as curated human-facing summaries only. Move runtime outputs into `.clockwork_runtime/` and prevent regressions.

**Observed (repo scan 2026-03-08):**
- `.report/` contains large amounts of runtime artifacts (JSON/JSONL and run-unknown outputs).

---

## Definition of Done

- [x] ✅ `.report/` contains curated markdown only (plus minimal structure files)
- [x] ✅ Runtime outputs are moved to `.clockwork_runtime/` (reports/telemetry/eval as appropriate)
- [x] ✅ A checker gate prevents new runtime writes into `.report/`
- [x] ✅ Optional: curated exporter can intentionally generate redacted summaries into `.report/`
- [x] ✅ All existing tests pass

---

## R63.1 — Classify `.report/` Contents

**Files:**
- `.report/**`
- `Docs/report_vs_runtime_policy.md` (or create if missing)

**Change:**
- Define categories and a mapping table (path → category → destination).

**Acceptance:**
- Mapping is stable and checked into `Docs/report_migration_map.md`.

---

## R63.2 — Migrate Runtime Outputs

**Change:**
- Move runtime outputs from `.report/` to runtime root, preserving structure.
- Update references that pointed into `.report/`.

**Acceptance:**
- After migration, `.report/` contains no JSON/JSONL and no machine-run folders.

---

## R63.3 — Prevent Regression (Gate)

**Files:**
- `claudeclockwork/core/gates/report_policy_gate.py` (new or extend)
- `tests/test_report_policy_gate.py`

**Change:**
- Gate fails when non-curated files or machine-run folders appear in `.report/`.

**Acceptance:**
- Synthetic runtime file in `.report/` triggers deterministic failure.

---
