# MVP Phase 64 — Curated Report Redaction Gate (No Host Paths / Secrets)

**Goal:** Ensure curated content is share-safe: no absolute host paths and no secret-like strings in `.report/` markdown.

**Observed (repo scan 2026-03-08):**
- Many `.report/*.md` files contain absolute Windows paths (e.g., `C:\`, `D:\`).

---

## Definition of Done

- [x] ✅ Redaction gate exists and runs in CI
- [x] ✅ `.report/**/*.md` contains zero absolute host paths
- [x] ✅ `.report/**/*.md` contains zero detected secret patterns (if defined)
- [x] ✅ Any runtime-generated `.md` moved out of `.report/` (Phase 63)
- [x] ✅ All existing tests pass

---

## X64.1 — Define Redaction Rules

**Files:**
- `Docs/redaction_rules.md` (new or extend)

**Change:**
- Block patterns:
  - Windows drive paths: `^[A-Z]:\`
  - Unix home paths: `/Users/`, `/home/`
  - API key patterns (if policy defines patterns)

**Acceptance:**
- Rules are deterministic and documented.

---

## X64.2 — Implement Redaction Gate

**Files:**
- `claudeclockwork/core/gates/report_redaction_gate.py` (new)
- `tests/test_report_redaction_gate.py`

**Change:**
- Scan `.report/**/*.md` and fail with file path + matched pattern (line number best effort).

**Acceptance:**
- Synthetic path leak triggers deterministic failure.

---

## X64.3 — Fix Violations

**Change:**
- Migrate runtime-generated md out of `.report/`.
- Redact remaining curated docs.

**Acceptance:**
- Gate passes with 0 findings.

---
