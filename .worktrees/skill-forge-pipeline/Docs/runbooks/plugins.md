# Runbook: Plugins

Plugin lifecycle and operations.

## Install / enable a plugin

1. **Source:** Plugin must be in `plugins/` or `.clockwork_plugins/` (or configured path).
2. **Manifest:** Each plugin has a manifest validated by [plugin manifest schema](../plugins.md).
3. **Validation:** Run `clockwork plugin list` or healthcheck: `python -m claudeclockwork.cli --plugin-healthcheck <plugin_id> --project-root .`. Exit 0 and `"status": "ok"`.

**Rollback:** Remove plugin directory or disable in config; re-run env-check.

---

## Plugin healthcheck failure

1. **Run:** `python -m claudeclockwork.cli --plugin-healthcheck <plugin_id> --project-root .`
2. **Inspect:** JSON `errors` and `detail` for cause.
3. **Fix:** Resolve dependency, path, or manifest error per [plugin_compatibility.md](../plugin_compatibility.md).
4. **Validation:** Healthcheck exits 0.

**Rollback:** Disable plugin until fix is available.
