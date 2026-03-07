# Plugin Security Policy (Phase 29)

- **Capability allowlist:** Plugins may only declare capabilities that are in the allowlist (Phase 24 capability policy).
- **Schema validation:** Every plugin manifest must validate against `plugin_manifest.schema.json`.
- **External runner restrictions:** Declared `external_runners` are checked against the allowlist; non-allowlisted runners cause rejection.
- **Resource limits:** Plugin execution is subject to resource limits (timeouts, concurrency) as defined in Phase 24.
- **Unsafe plugin:** Rejected with a typed error (e.g. `plugin_rejected`, code `unsafe_capability` or `incompatible_version`).
