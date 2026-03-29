# Runtime Discovery Note

In the inspected ClaudeClockwork archive, native manifest skills are stored under `.claude/skills/`, but the current `build_registry()` implementation points to `skills/` as its discovery root.

That means there are two possible integration modes:

## Preferred native placement

Place this pack into:

- `.claude/skills/analysis/...`

This matches the existing repository structure.

## Runtime discovery caveat

If your runtime path still scans only `skills/`, the new manifests may not be discovered automatically until you do one of the following:

- update the runtime registry discovery root to `.claude/skills`
- or mirror the same package into a top-level `skills/` directory

This pack itself does not change that behavior, because it is intentionally delivered as a drop-in skill package rather than a runtime refactor.
