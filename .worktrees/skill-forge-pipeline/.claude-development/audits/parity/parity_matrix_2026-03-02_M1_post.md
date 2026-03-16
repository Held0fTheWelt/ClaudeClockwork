# Parity Matrix — Post-M1 (2026-03-02)

_Snapshot after M1 parity follow-up. P0 invariant items B-001–B-004 resolved._

## M1 Resolutions

| Former P0 Item | Status | Evidence |
|----------------|--------|----------|
| B-001 `.claude/knowledge/-Writes/` | **FULL** | Content moved to `.llama_runtime/knowledge/writes/`; all refs updated; source dir removed. |
| B-002 `outcome_ledger.jsonl` in clockwork | **FULL** | `.claude/knowledge/outcome_ledger.jsonl` deleted; canonical `.llama_runtime/knowledge/outcome_ledger.jsonl`. |
| B-003 `route_profiles.json` in clockwork | **FULL** | `.claude/knowledge/route_profiles.json` deleted; canonical `.llama_runtime/knowledge/route_profiles.json`. |
| B-004 `.claude/brain/` in clockwork | **FULL** | `.claude/brain/` removed; canonical `.llama_runtime/brain/`. |

## CCW-MVP17 (Clockwork Invariants + CI Gate + Integration Tests)

| Criterion | Status |
|-----------|--------|
| Invariant: no runtime state in `.claude/knowledge/` | **FULL** (post B-001–B-004) |
| `.github/workflows/gate.yml` runs `scripts/gate.sh` | **FULL** |
| `scripts/gate.sh` runs pytest qa_tests + tests | **FULL** |
| qa_gate.py has 10+ checks | **FULL** (12 checks) |
| `tests/test_integration_pipeline.py` exists | **FULL** |
| outcome_ledger_append / route_* skills use .llama_runtime paths | **FULL** |

## Deferred / Out of Scope for M1

- B-006: Stub skill tagging — no unimplemented skill READMEs found.
- B-007 / B-008: `oodle/` and `src/` confirmed active; not moved to legacy.
- B-010 / B-013: Design-only in M1; implementation in M2.

End.
