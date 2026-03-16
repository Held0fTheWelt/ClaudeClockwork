# Parity Matrix — Post-M1
**Date:** 2026-03-05
**Milestone:** M1 (Parity Follow-up)

## P0 Invariants

| ID | Item | Status | Notes |
|----|------|--------|-------|
| B-001 | Move `-Writes/` to `.llama_runtime/writes/` | ✓ FULL | Moved; gitignore updated |
| B-002 | Move `outcome_ledger.jsonl` to `.llama_runtime/outcome_ledger/` | ✓ FULL | Moved; doc refs fixed |
| B-003 | Move `route_profiles.json` to `.llama_runtime/routing/` | ✓ FULL | Dir created; stale refs fixed |
| B-004 | Move `.claude/brain/` to `.llama_runtime/brain/` | ✓ FULL | Moved |
| B-005 | Create `.github/workflows/gate.yml` | ✓ FULL | CI gate active |

## P1 Items

| ID | Item | Status | Notes |
|----|------|--------|-------|
| B-006 | `status: stub` on unimplemented skill READMEs | ✓ FULL | `playbooks` skill tagged |
| B-007 | Move `oodle/` to `quellen/legacy/oodle/` | ✓ FULL | Moved; test updated |
| B-008 | Move `src/` to `quellen/legacy/src/` | ✓ FULL | Moved; gate checks updated |
| B-009 | QA gate: 6 → 10+ checks | ✓ FULL | 15 checks active |
| B-010 | Design: drift critic + regression critic | ✓ FULL | Design docs in `llamacode/core/critics/` |
| B-011 | `tests/test_integration_pipeline.py` passes | ✓ FULL | 14 tests passing |
| B-013 | Design: adaptive router v1 (bandit spec) | ✓ FULL | Design doc in `llamacode/core/routing/` |

## Deferred (M2)

| ID | Item | Target |
|----|------|--------|
| B-010-impl | Implement drift + regression critics | M2 |
| B-013-impl | Implement adaptive router v1 | M2 |
| B-012 | Eval harness | M2 |
| B-021 | Knowledge graph | P2 |
| B-022 | Agent genome / evolution | P2 |
| B-018 | Plugin runtime | M3+ |
