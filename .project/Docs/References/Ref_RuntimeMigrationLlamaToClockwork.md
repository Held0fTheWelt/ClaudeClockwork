# Runtime Migration: .llama_runtime → .clockwork_runtime

**Date:** 2026-03-08
**Phase:** MVP Phase 65
**Status:** Completed

## Executive Summary

The `.llama_runtime/` directory was used in early versions of Clockwork (pre-Phase 19) as the runtime state root. As of Phase 19, `.clockwork_runtime/` became the canonical runtime root. This document records the migration decision and cleanup.

## Inventory of .llama_runtime/ (as of 2026-03-08)

| Directory | Size | Content | Status |
|-----------|------|---------|--------|
| `.llama_runtime/artifacts/` | ~0 KB | Legacy test bundles | Migrated to `.clockwork_runtime/artifacts/` |
| `.llama_runtime/brain/` | ~0 KB | Model routing stats | Newer version in `.clockwork_runtime/brain/` |
| `.llama_runtime/eval/` | ~4 MB | Historical eval results (45+ runs from 2026-03-06) | Discarded (stale test data) |
| `.llama_runtime/knowledge/` | ~28 MB | 159 files (outcome_ledger.jsonl, autodocs reports) | Discarded (superseded by `.clockwork_runtime/knowledge/`) |
| `.llama_runtime/writes/` | ~6 MB | 49 hardening/quality reports from 2026-03-06 | Discarded (stale reports, newer versions in `.clockwork_runtime/writes/`) |
| `.llama_runtime/.gitkeep` | 0 bytes | Marker file | Removed |

**Total size:** ~38 MB (all ephemeral/transient, nothing hand-curated)

## Migration Decisions

### Artifacts
- **Decision:** MIGRATE
- **Reason:** Contains `test_phase3_bundle.zip` and manifest (Phase 3 test data)
- **Action:** Files already exist in `.clockwork_runtime/artifacts/`; no action needed

### Brain
- **Decision:** DISCARD (REPLACE)
- **Reason:** `.clockwork_runtime/brain/model_routing_stats.json` is newer (231 attempts vs 45 in `.llama_runtime/`)
- **Action:** None — `.clockwork_runtime/` version is authoritative

### Eval
- **Decision:** DISCARD
- **Reason:** All 45 eval results are from 2026-03-06, stale test data with no permanent value
- **Action:** Delete from `.llama_runtime/eval/`

### Knowledge
- **Decision:** DISCARD
- **Reason:** 159 files of telemetry/autodocs reports; superseded by `.clockwork_runtime/knowledge/` which has current ledgers
- **Action:** Delete from `.llama_runtime/knowledge/`

### Writes
- **Decision:** DISCARD
- **Reason:** 49 hardening reports from 2026-03-06; newer versions exist in `.clockwork_runtime/writes/`
- **Action:** Delete from `.llama_runtime/writes/`

## Final Action

- **Delete** `.llama_runtime/` content entirely (all subdirectories)
- **Replace** with **stub directory** containing:
  - `.gitkeep` (marker for git)
  - `README.md` (deprecation notice)
- **Keep in `.gitignore`** (already present)

## Code Impact

- `scripts/migrate_runtime_root.py`: No longer needed; kept as historical reference but not executed
- `.clockwork_runtime/README.md`: Updated to remove migration instructions (users should never encounter `.llama_runtime/`)
- No active code references `.llama_runtime/` (confirmed via grep)

## Files Modified by This Phase

- `.llama_runtime/` (stubbed)
- `.clockwork_runtime/README.md` (updated)
- `claudeclockwork/core/gates/runtime_root_gate.py` (new, Phase 65.3)
- `tests/test_runtime_root_gate.py` (new, Phase 65.3)
