# MVP Phase 70 — Doc Redaction Sweep (Remove Absolute Host Paths Outside Runtime)

**Goal:** Ensure curated documentation is share-safe by removing absolute host paths from all non-runtime locations (outside `.clockwork_runtime/`), and enforce this with a gate.

**Observed (repo scan 2026-03-08):**
- Absolute host paths appear in curated docs (examples and leaks), including:
  - `Docs/green_criteria.md`
  - `mvps/MVP_Phase64_ReportRedactionGate.md`
  - `.project/Docs/Phase64_Acceptance_Checklist.md`
  - `.project/Docs/redaction_rules.md`
  - `.claude/agents/tester.md`
  - `.claude/governance/ollama_integration.md`

---

## Definition of Done

- [x] ✅ All absolute host path strings removed/replaced outside runtime roots
- [x] ✅ Replacements use placeholders (`<PROJECT_ROOT>`, `<DRIVE>`, `<username>`, `<ABS_PATH>`)
- [x] ✅ `doc_path_leak_gate` scans curated dirs and fails on absolute path leaks
- [x] ✅ Gate excludes runtime roots (scopes: Docs/, .project/Docs/, mvps/, .claude/governance/, .claude/agents/)
- [x] ✅ All existing tests pass (12/12 new gate tests)

---

## R70.1 — Replace Absolute Paths with Placeholders

**Files:**
- The documents listed above (and any additional findings)

**Change:**
- Replace:
  - `<DRIVE>:\...` → `<ABS_PATH>`
  - `/Users/...` → `<ABS_PATH>`
  - `/home/...` → `<ABS_PATH>`
- If examples are needed, format them as code blocks with placeholders.

**Acceptance:**
- 0 absolute host path matches in curated areas.

---

## R70.2 — Add Gate: Curated Doc Path Leak Scan

**Files:**
- `claudeclockwork/core/gates/doc_path_leak_gate.py` (new)
- `tests/test_doc_path_leak_gate.py`

**Change:**
- Scan curated directories:
  - `Docs/`
  - `.project/Docs/` (if curated)
  - `.claude/governance/`
  - `.claude/agents/`
  - `mvps/`
- Exclude:
  - `.clockwork_runtime/`
  - `.llama_runtime/` (legacy stub)
  - other explicit runtime locations

**Acceptance:**
- Synthetic leak triggers deterministic failure with file+pattern.

---

## Drift Prevention Instruction
This MVP must explicitly state (in a short policy note) whether absolute paths were:
- accidental leaks (should never happen), or
- examples (then placeholders must be used).
The gate must reflect that decision.

---
