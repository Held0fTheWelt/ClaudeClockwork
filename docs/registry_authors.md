# Registry: Authors and Operators (Phase 47)

## For plugin authors

1. **Bundle layout:** One directory per plugin with `plugin.json` (see [plugin_template.md](plugin_template.md)). No `.git`, `__pycache__`, `.env`, or `node_modules` inside the bundle.
2. **Validate before publish:** Run the bundle validator (e.g. via `validate_bundle` or CLI) so that CI and publish succeed.
3. **Publish workflow:** Test (validate) → sign/hash → index update. Hash is written to the allowlist; index is rebuilt. See [plugin_signing.md](plugin_signing.md) and [registry_index_format.md](registry_index_format.md).

## For operators

1. **Allowlist:** In strict mode, only plugins whose content hash is in `.clockwork_plugins_allowlist.json` are allowed. Publish workflow updates this file when you opt in.
2. **Index:** Local index is under `.clockwork_runtime/registry_index.json` after publish. Same format can be mirrored for remote discovery.
3. **CI:** Use the bundle validator on submission bundles so that only valid bundles are accepted.
