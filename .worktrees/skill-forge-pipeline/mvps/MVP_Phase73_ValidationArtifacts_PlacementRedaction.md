# MVP Phase 73 — Validation Artifacts: Placement + Redaction Fix

**Goal:** Make validation artifacts share-safe and correctly placed. `validation_runs/` and `validation_runs_redacted/` must not leak absolute host paths and must follow runtime/curated boundaries.

**Observed (repo scan 2026-03-08):**
- Evidence manifests under `validation_runs*` still include absolute Windows paths (e.g., `<DRIVE>:\ClaudeClockwork\...`).

---

## Definition of Done

- [ ] A clear policy exists for validation artifacts:
  - runtime-only under `.clockwork_runtime/`, OR
  - curated redacted outputs under a curated root with strict rules
- [ ] No absolute host paths appear in any “redacted” validation manifest
- [ ] A gate enforces this (fails on path leaks)
- [ ] Any repo-committed validation artifacts are either:
  - minimal curated summaries, or
  - pointers to runtime artifacts (preferred)
- [ ] All existing tests pass

---

## V73.1 — Decide Placement Policy

**Files:**
- `Docs/report_vs_runtime_policy.md`
- `Docs/drift_register.md`

**Change:**
- Declare where validation runs live and what may be committed.

**Acceptance:**
- Policy is explicit and referenced by gates.

---

## V73.2 — Redact Manifests Properly

**Files:**
- Redaction engine/gates (existing)
- `validation_runs_redacted/**`

**Change:**
- Replace host paths with placeholders:
  - `<PROJECT_ROOT>` / `<ABS_PATH>`
- Ensure manifests remain valid JSON.

**Acceptance:**
- Zero matches for `^[A-Z]:\`, `/Users/`, `/home/` outside runtime.

---

## V73.3 — Add Gate: Validation Artifact Leak Scan

**Files:**
- `claudeclockwork/core/gates/validation_artifact_gate.py` (new)
- `tests/test_validation_artifact_gate.py`

**Change:**
- Gate scans:
  - `validation_runs_redacted/**` (and any curated validation outputs)
- Fails on:
  - absolute path leaks
  - runtime-only files committed unintentionally

**Acceptance:**
- Synthetic leak triggers deterministic failure.

---

## Drift Prevention Instruction
If you keep any validation artifacts in the repo, you must document:
- why they exist,
- what is allowed,
- and how gates prevent reintroducing leaks.

---
