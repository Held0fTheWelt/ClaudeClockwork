# Legacy Adapter Layer Deprecation (Phase 27)

## Retirement criteria

- **Native coverage threshold:** 100% of manifest skills use native SkillBase (no LegacySkillAdapter). Phase 17 achieved this.
- **Critical skills:** No remaining critical skills on legacy bridge. All are native or removed.

## Enforcement

- **CI:** If any code imports `LegacySkillAdapter` (except the tombstone in `claudeclockwork/legacy/adapter.py`), treat as error. Phase 17 removed the adapter; the stub raises ImportError.
- **Gradual policy:** New skills must use SkillBase only. Batch conversion tooling (Phase 27) supports any future cleanup; no new adapter usage is allowed.

## Status

Legacy adapter layer is **deprecated and removed**. The module `claudeclockwork.legacy.adapter` exists only as a tombstone (ImportError on use). All 104+ manifest skills are native.
