# CAS Eviction (Phase 36)

- Quota: max bytes and/or max objects.
- Deterministic eviction: oldest-first (mtime), then stable sort by hash.
- Pinned refs (e.g. bundle references) are never evicted. Eviction does not corrupt referenced bundles.
