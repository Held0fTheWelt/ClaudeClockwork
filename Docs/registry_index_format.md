# Registry Index Format (Phase 47)

Canonical format for the plugin registry index. Used for local discovery and for mirroring.

## Index file

- **Location:** Repo-local (e.g. `.clockwork_runtime/registry_index.json` or build on demand).
- **Structure:** JSON array of plugin entries, stable sort by `id`.

## Entry schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Plugin identifier (from manifest) |
| `allowed` | boolean | Whether plugin is allowlisted (hash/signing) |
| `compatible` | boolean | Compatibility with current Clockwork version |
| `last_test` | object \| null | Last test result (optional: status, timestamp) |
| `hash` | string | (Optional) Content hash after publish |

## Mirroring

The same format can be exported or mirrored to a remote registry. Publish workflow writes hash into allowlist and index is rebuilt from local plugins + allowlist.
