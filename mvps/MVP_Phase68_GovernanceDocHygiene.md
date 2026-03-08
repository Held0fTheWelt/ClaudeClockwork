# MVP Phase 68 — Governance Doc Hygiene (Placeholder Link Removal)

**Goal:** Remove placeholder links from governance documents and ensure governance docs are link-lint clean and actionable.

**Observed (repo scan 2026-03-08):**
- `.claude/governance/file_lifecycle.md` contains a placeholder link like `../path/to/canonical.md`.

---

## Definition of Done

- [x] ✅ Governance docs contain no placeholder/dead links
- [x] ✅ link-lint passes for `.claude/governance/**`
- [x] ✅ Any examples that resemble links are formatted as code blocks so they do not break link-lint
- [x] ✅ All existing tests pass

---

## G68.1 — Replace Placeholder Link with Real Reference

**Options:**
A) Replace with the actual canonical doc path if it exists (preferred)
B) If it is only an example, format as a code block and label “example only”

**Acceptance:**
- link-lint reports zero broken links in governance docs.

---

## Rules to Complete (if incomplete)
- Ensure governance docs follow a consistent template:
  - Purpose
  - Scope
  - Rules (normative)
  - Examples (non-normative, in code blocks)
  - References (real paths only)

---
