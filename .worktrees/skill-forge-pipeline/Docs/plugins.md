# Plugins (Phase 29)

Extensions (skills, agents, critics, tools) without modifying core. Repo-local plugin directory with a clear contract.

## Manifest contract

- **Schema:** `.claude/contracts/schemas/plugin_manifest.schema.json`
- **Fields:** id, name, version (required); clockwork_compat (version range); capabilities; permissions; file_access; external_runners; lifecycle.

## Discovery

- Plugins are discovered under `plugins/` (or `.clockwork_plugins/`). Each plugin is a directory with a manifest (`plugin.json` or `manifest.json`).
- Loader is deterministic (stable ordering by plugin id).
- Compatibility: `clockwork_compat` is checked against the current Clockwork version; incompatible plugins are skipped or rejected with a typed error.

## Safety

See `Docs/plugin_security_policy.md`: capability allowlist, schema validation, external runner restrictions, resource limits. Unsafe plugins are rejected with a typed error.
