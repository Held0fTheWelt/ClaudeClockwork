# MVP Phase 19 — Runtime Root Normalization (Decouple Naming)

**Goal:** Remove the repo-coupled runtime naming (`.llama_runtime/`) and standardize Clockwork runtime artifacts under a dedicated Clockwork runtime root (e.g. `.clockwork_runtime/`). Ensure deterministic paths for reports, evidence, telemetry, and redactions.

**Source findings (repo scan 2026-03-07):**
- `.llama_runtime/` exists and is referenced across docs/tests/scripts.
- `.report/` sometimes contains runtime outputs, while other systems expect curated reports.

---

## Definition of Done

- [x] New runtime root created: `.clockwork_runtime/` with a documented sub-structure (README + subdirs)
- [x] Automated migration script added: `scripts/migrate_runtime_root.py` (copies `.llama_runtime/` → `.clockwork_runtime/`)
- [x] `.gitignore` updated to ignore `.clockwork_runtime/` and `.llama_runtime/`
- [x] All references to `.llama_runtime/` removed from repo docs/code/tests (except migration script comment)
- [x] Report vs runtime policy documented: `Docs/report_vs_runtime_policy.md` (curated `.report/` vs runtime `.clockwork_runtime/`)
- [x] All existing tests pass

---

## R19.1 — Define Canonical Runtime Layout

**Files:**
- `.clockwork_runtime/README.md`
- `.gitignore`

**Change:**
Create a stable structure, for example:
- `.clockwork_runtime/telemetry/` (raw JSONL)
- `.clockwork_runtime/reports/` (derived machine reports)
- `.clockwork_runtime/evidence/` (artifacts)
- `.clockwork_runtime/redacted_exports/` (sanitized bundles)

**Acceptance:**
- A clean run writes artifacts only under `.clockwork_runtime/`.

---

## R19.2 — Migration Script + Reference Update

**Files:**
- `scripts/migrate_runtime_root.py` (or `.sh`)
- All docs/tests referencing `.llama_runtime/`

**Change:**
- Move folder contents.
- Update hardcoded references in docs, tests, and scripts.
- Add a compatibility note for users with old directories (optional).

**Acceptance:**
- `grep -R ".llama_runtime" -n .` returns 0 (or only the migration note).

---

## R19.3 — Report vs Runtime Policy

**Files:**
- Policy doc (e.g. `Docs/report_vs_runtime_policy.md`)
- `.report/README.md` (if present)

**Change:**
- Decide: `.report/` is curated human-facing summaries; runtime outputs go to `.clockwork_runtime/`.
- Add a deterministic exporter that copies/redacts runtime outputs into `.report/` only when requested.

**Acceptance:**
- CI gate prevents writing new runtime outputs directly into `.report/`.

---
