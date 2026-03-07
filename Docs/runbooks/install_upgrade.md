# Runbook: Install and Upgrade

Deterministic steps. No handwave.

## Install (fresh)

1. **Prerequisites:** Python 3.10+, pip.
2. **Install:** From repo root: `pip install -e .`
3. **Validation:** Run `python -m claudeclockwork.cli env-check --project-root .`. Exit 0 and `"ok": true` in JSON.
4. **First-run:** Run `python -m claudeclockwork.cli first-run --project-root .`. Expect `.clockwork_runtime/` created and JSON `"ok": true` or actionable `errors`.

**Rollback:** `pip uninstall claudeclockwork`. Remove `.clockwork_runtime/` if created.

---

## Upgrade (existing install)

1. **Pull:** `git pull` (or obtain new package).
2. **Reinstall:** `pip install -e .` (or `pip install claudeclockwork==<version>`).
3. **Validation:** `python -m claudeclockwork.cli env-check --project-root .`. Exit 0.
4. **Config:** If release notes mention config migration, run `clockwork migrate --dry-run` then `clockwork migrate --apply` per [versioning.md](../versioning.md).

**Rollback:** Reinstall previous version: `pip install claudeclockwork==<prev>`. Restore config backup if migrated.
