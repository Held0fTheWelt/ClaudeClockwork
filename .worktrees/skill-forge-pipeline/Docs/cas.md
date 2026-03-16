# Content-Addressed Store (Phase 36)

- CAS lives under runtime root (or configurable). Layout: `.clockwork_runtime/cas/objects/<hash_prefix>/<hash>`.
- Artifacts stored and referenced by content hash. Metadata: size, mime, created_at, producer (tool/node id).
- Same content always yields same object id. Node cache can store outputs as CAS refs; reuse when inputs + params + tool versions match.
- Eviction: quota-based, deterministic (oldest-first).
