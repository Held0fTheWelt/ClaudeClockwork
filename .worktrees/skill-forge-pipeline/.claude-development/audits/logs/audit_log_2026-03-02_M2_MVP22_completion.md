# M2 MVP22 — Clockwork Invariant Cleanup (Completion)

**Date:** 2026-03-02  
**Plan:** `.claude-development/milestones/M2_clockwork_audit_followup_plan_2026-03-02.md`  
**Scope:** MVP22 (Week 1 immediate)

---

## Delivered

| Item | Action |
|------|--------|
| **V-001–V-004** | Already closed in M1 (`.claude/knowledge/` ledger, profiles, `-Writes/`, `.claude/brain/` removed). No remnants. |
| **V-005** | `.claude/eval/__pycache__/` added to `.gitignore`; directory removed. |
| **V-006** | Eval results default → `.llama_runtime/eval/results/`; existing `run_*.json` moved; `eval_runner.py` and `eval_run.py` defaults updated; `.claude/eval/README.md` updated. |
| **Pointer targets** | `ARCHITECTURE.md`, `ROADMAP.md`, `MODEL_POLICY.md` created at repo root with canonical overviews. |
| **INDEX.md** | VERSION reference updated to 17.7.0 (`.claude/VERSION`). |

## Files Touched

- `.gitignore` — added `.claude/eval/__pycache__/`
- `.claude/eval/eval_runner.py` — default `--results-dir` → `.llama_runtime/eval/results`
- `.claude/tools/skills/eval_run.py` — default `output_dir` → `.llama_runtime/eval/results`
- `.claude/eval/README.md` — docs for results location and CLI example
- `.claude/INDEX.md` — VERSION string 6.5.0-MVP9 → 17.7.0
- **New:** `ARCHITECTURE.md`, `ROADMAP.md`, `MODEL_POLICY.md` (repo root)
- **Moved:** `run_20260302_083150.json` (+ 3) from `.claude/eval/results/` to `.llama_runtime/eval/results/`
- **Removed:** `.claude/eval/__pycache__/`

## Verification

- `pytest tests/test_integration_pipeline.py` — 14 passed.

---

**Next (per plan):** Week 2 — MVP22-D (Runtime Critics Architecture), MVP23-D (Capability Policy Design), MVP24-D (Eval Harness Completion Design).
