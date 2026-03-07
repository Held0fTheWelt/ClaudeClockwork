# Clockwork Versioning

**Canonical version source:** `.claude/VERSION` (single source of truth).

- **Product version:** Semantic-style `MAJOR.MINOR.PATCH` (e.g. `17.7.83`). Stored only in `.claude/VERSION`.
- **Propagation:** Root `VERSION` (if present) must match `.claude/VERSION`. The planning drift gate (DRIFT_001) fails if they differ.
- **Changelog:** `.claude/CHANGELOG.md` must reference the current version (e.g. header or `<!-- current-version: X.Y.Z -->`). The release check gate (RELEASE_001) fails if the changelog does not mention the canonical version.

## Propagation rules

1. Edit only `.claude/VERSION` when bumping.
2. Run `scripts/sync_version.py` or copy manually to root `VERSION` if your workflow uses root `VERSION`.
3. Add an entry or update the version pointer in `.claude/CHANGELOG.md` for every version bump.
4. CI runs `planning_drift_scan` and `release_check`; both must pass.
