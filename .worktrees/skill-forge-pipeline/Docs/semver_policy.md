# SemVer Policy

> Clockwork follows Semantic Versioning (MAJOR.MINOR.PATCH). This document defines what constitutes a breaking change and how we enforce it.

## Rules

| Change type | Version bump | Allowed without deprecation |
|-------------|--------------|-----------------------------|
| Breaking: stable CLI output/exit codes, public API removal/rename | MAJOR | No — must be in `Docs/deprecations.md` first |
| New stable command or flag | MINOR | Yes |
| New public API symbol (export in `claudeclockwork.__init__`) | MINOR | Yes, if additive |
| Internal-only changes, bug fixes, docs | PATCH | Yes |
| Deprecation (warn, then block, then remove) | MINOR for deprecation, MAJOR for removal | No — must follow deprecation framework |

## Breaking change definition

- **CLI:** Changing stable command names, output JSON keys (for stable commands), or exit code semantics.
- **Public API:** Removing or renaming any symbol in `Docs/public_api.md` or in `claudeclockwork.__all__`.
- **Config schema:** Removing or renaming required config keys; changing semantics of existing keys (see migration system for schema versioning).

## Gates

- `public_surface_gate`: Fails if the public surface (exports, CLI contract) changes without a version bump or without a deprecation entry.
- Run before release: `python -m claudeclockwork.core.gates.public_surface_gate`

## Deprecation framework

See `Docs/deprecations.md`. Lifecycle: **warn** (MINOR) → **block** (next MINOR or PATCH with feature flag) → **remove** (MAJOR).
