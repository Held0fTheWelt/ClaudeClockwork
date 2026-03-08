# MVP Phase 69 — `.claude-performance/` Hygiene (Move Runtime Noise + Prevent Reintroduction)

**Goal:** Stop performance/runtime artifacts from polluting curated repo space. `.claude-performance/` must be either:
A) Curated-only (preferred), with runtime outputs moved to `.clockwork_runtime/performance/`, OR
B) Explicitly justified as a curated artifact root (must be documented and gated).

**Observed (repo scan 2026-03-08):**
- `.claude-performance/` contains many `.md` files with absolute host paths (e.g., `D:\ClaudeClockwork\...`) and `run-unknown` style output, consistent with runtime/perf logs.

---

## Definition of Done

- [x] ✅ A clear policy decision is made (A) and documented in `Docs/report_vs_runtime_policy.md`
- [x] ✅ Option A implemented:
  - `.claude-performance/` contains curated docs only (README.md, reviews/, charts/)
  - Runtime/perf outputs removed from git tracking and disk; gitignored going forward
  - `perf_artifact_gate` blocks new runtime/perf outputs under `.claude-performance/`
- [x] ✅ No absolute host paths remain in curated `.claude-performance/` outputs
- [x] ✅ All existing tests pass (10/10 new gate tests)

---

## P69.1 — Decide and Document the Policy (Explain or Eliminate)

**Files:**
- `Docs/report_vs_runtime_policy.md` (extend)
- `Docs/performance_artifacts_policy.md` (new, if needed)

**Change:**
- Decide whether `.claude-performance/` is:
  - curated-only index (preferred), or
  - a curated artifact root with strict rules.

**Acceptance:**
- Policy explicitly answers:
  - Why `.claude-performance/` exists
  - What may live there
  - How artifacts are produced (manual vs automated)
  - Where runtime/perf outputs must live

---

## P69.2 — Migrate Runtime/Perf Outputs (Preferred Path)

**Files:**
- `.claude-performance/**`
- `.clockwork_runtime/performance/**`

**Change:**
- Move any “run-* / run-unknown / generated” files into runtime root.
- Keep only curated summaries (if any) in `.claude-performance/`.

**Acceptance:**
- `.claude-performance/` contains no machine-run output folders.

---

## P69.3 — Add Gate: Performance Artifact Placement

**Files:**
- `claudeclockwork/core/gates/perf_artifact_gate.py` (new)
- `tests/test_perf_artifact_gate.py`

**Change:**
- Gate fails if:
  - `run-*` or machine-generated patterns appear under `.claude-performance/`
  - absolute host paths appear in curated perf docs
  - runtime outputs appear outside `.clockwork_runtime/`

**Acceptance:**
- Synthetic violation fails deterministically.

---

## Drift Prevention Instruction
This MVP must also add a short section to the policy docs stating:
- whether these artifacts are expected,
- and if they are, exactly why they exist and how drift is prevented.
If drift keeps recurring, the gate must be tightened until it cannot.

---
