# Plugin Signing (Phase 40)

- Hash allowlist: repo-local allowlist file (e.g. `.clockwork_plugins_allowlist.json`) lists plugin id → content hash.
- Plugin manifest can declare a `content_hash` (of plugin dir or manifest).
- In strict mode, modified plugin content changes hash and is rejected if not on allowlist.
