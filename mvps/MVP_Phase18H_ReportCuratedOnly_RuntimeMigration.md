# MVP Phase 18H — `.report/` Curated-Only + Runtime Migration (REPORT_001)

**Goal:** Restore `.report/` as curated human-facing summaries only, and move runtime outputs to `.clockwork_runtime/` per policy. Remove host-specific path leaks from curated reports.

---

## Definition of Done

- [ ] `.report/README.md` exists and states curated-only policy
- [ ] Runtime outputs removed from `.report/` and migrated into `.clockwork_runtime/reports/` (or appropriate runtime subdir)
- [ ] Curated exporter (optional) can produce redacted summaries into `.report/`
- [ ] Report gate passes
- [ ] No absolute host paths are present in `.report/` (redaction check)
- [ ] All existing tests pass

---

## 18H.1 — Add `.report/README.md`

**Files:**
- `.report/README.md`

**Change:**
- Add short policy + link to `Docs/report_vs_runtime_policy.md` (if exists).

**Acceptance:**
- Gate `REPORT_001` passes.

---

## 18H.2 — Migrate Runtime Noise

**Files:**
- `.report/**`
- `.clockwork_runtime/**`

**Change:**
- Move machine-generated outputs from `.report/` into runtime root.
- Keep `.report/` only for curated markdown summaries.

**Acceptance:**
- A “report vs runtime” policy checker reports compliant placement.

---

## 18H.3 — Redaction / Path Leak Check

**Files:**
- Redaction engine (Phase 23) or add minimal checker
- `tests/test_report_redaction.py`

**Change:**
- Detect absolute Windows/macOS/Linux paths in curated reports and fail.

**Acceptance:**
- Reports contain no absolute host paths.

---
