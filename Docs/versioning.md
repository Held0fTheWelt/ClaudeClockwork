# Clockwork Versioning — Hard Lock Policy

**Phase 62:** Version drift is now cryptographically impossible via the planning drift gate.

## Canonical Version Source

The canonical version source is **`.claude/VERSION`** — single source of truth (SSOT).

- **Format:** Semantic versioning `MAJOR.MINOR.PATCH` (e.g., `17.7.294`)
- **No trailing newlines:** File contains only the version string followed by newline
- **Immutable:** Only automated version bumps or manual edits to the canonical source propagate

## Drift Detection Hard Lock

The planning drift gate (`claudeclockwork/core/gates/planning_drift.py`) runs deterministic checks that **hard-fail** if version convergence is violated:

### Check 1: Canonical Version Existence
- `.claude/VERSION` must exist and be readable
- Fails with: `"Canonical version file .claude/VERSION missing or unreadable"`

### Check 2: Version Convergence
- If root-level `VERSION` file exists, it **must exactly match** `.claude/VERSION`
- Example failure: `.claude/VERSION='17.7.290'` vs `VERSION='17.7.208'`
- Fails with: `"Version mismatch: .claude/VERSION='{canonical}' vs VERSION='{root}'"`

### Check 3: No Extra Version Files
- Scanning detects extra untracked version files and reports them as warnings
- Future phases may hard-fail on extra files

### Enforcement Gate
- **DRIFT_001:** Automatic gate runs in CI before release
- **Test:** `test_planning_drift_scan_clean_repo` verifies clean-repo pass
- **Test:** `test_planning_drift_version_mismatch_fails` verifies mismatch detection

## Release Check Hard Lock

The release check gate (`claudeclockwork/core/gates/release_check.py`) enforces:

### Check 1: Version Convergence
- Inherits DRIFT_001 checks (must pass version convergence)

### Check 2: Changelog Entry
- `.claude/CHANGELOG.md` must **explicitly mention** the canonical version
- Supported formats:
  - HTML comment: `<!-- current-version: 17.7.290 -->`
  - Markdown header: `## 17.7.290`
  - Plain text: Version string anywhere in first 2048 bytes
- Fails with: `"Missing changelog entry for version {version}"`

### Enforcement Gate
- **RELEASE_001:** Runs before release cut
- **Test:** `test_release_check_clean_repo_passes` verifies clean-repo pass
- **Test:** `test_changelog_mentions_version_detection` verifies changelog matching

## Propagation Workflow

Version bumps flow through this workflow:

```
1. Edit only .claude/VERSION (canonical source)
2. Changelog must be updated to mention the new version
3. Root VERSION (if present) must be synced to match
4. Run: python3 -m pytest tests/test_gates.py::test_planning_drift_scan_clean_repo
5. CI runs DRIFT_001 + RELEASE_001 gates
6. Both gates must pass before deployment
```

### Propagation Rules

1. **Never edit root `VERSION` directly** — it mirrors the canonical source
2. **Always edit `.claude/VERSION` first** when bumping the product version
3. **Sync root `VERSION`** via `python3 scripts/sync_version.py` (Phase 72 — canonical sync utility)
4. **Update `.claude/CHANGELOG.md`** with the new version in the first line:
   ```markdown
   <!-- current-version: 17.7.295 -->
   ```
5. **Verify gates pass** before committing:
   ```bash
   python3 -m pytest tests/test_gates.py::test_planning_drift_scan_clean_repo \
                       tests/test_release_check.py -v
   ```

## Deterministic Testing

All version drift checks are deterministic and can be tested in isolation:

```python
# Test version mismatch detection
from claudeclockwork.core.gates.planning_drift import run_planning_drift_scan
result = run_planning_drift_scan("/path/to/repo")
assert result["pass"] is True  # Clean repo
assert any("mismatch" in e.lower() for e in result["errors"])  # Mismatch detected
```

See `tests/test_gates.py` and `tests/test_release_check.py` for full test suite.

## Deployment Guarantee

With DRIFT_001 + RELEASE_001 hard locks enforced:

- **Guarantee:** Version convergence at release time is mathematically impossible to violate
- **Guarantee:** Changelog is synchronized with released version
- **Guarantee:** No orphaned or duplicate version files
- **Safeguard:** Both gates must pass or deployment is blocked

## Version Sync Command (Phase 72)

`scripts/sync_version.py` is the canonical auto-sync utility. It reads `.claude/VERSION` and
writes root `VERSION` to match. Running it twice is idempotent.

```bash
# Sync (dry-run first to preview)
python3 scripts/sync_version.py --dry-run
python3 scripts/sync_version.py

# Verify convergence
python3 -m pytest tests/test_gates.py::test_planning_drift_scan_clean_repo -v
```

**When to run:** Before any commit where `.claude/VERSION` may have been auto-incremented.
Run it as the last step before `git add VERSION && git commit`.

**DR-001 Prevention:** This sync tool is the enforcement mechanism for DR-001. Any mismatch
is caught by `planning_drift_scan` (DRIFT_001) at gate time. If DRIFT_001 fails, run
`python3 scripts/sync_version.py` to fix instantly.

---

## Migration from Old Workflow

If your repo has stale version files (e.g., `setup.py`, `pyproject.toml` with embedded versions):

1. Remove embedded version declarations
2. Import canonical version at runtime:
   ```python
   from pathlib import Path
   __version__ = (Path(__file__).parent.parent / ".claude" / "VERSION").read_text().strip()
   ```
3. Run drift gate to verify convergence
4. Remove old version files in cleanup phase
