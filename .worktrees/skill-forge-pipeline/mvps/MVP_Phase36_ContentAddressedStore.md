# MVP Phase 36 — Deterministic Caching & Content-Addressed Store (CAS)

**Goal:** Introduce a content-addressed store for artifacts and tool outputs so Work Graph runs and Distributed Workers can reuse results across runs and hosts deterministically.

**Why now:** Remote workers (Phase 35) need a shared artifact identity. Work Graph caching (Phase 30) is node-local; CAS makes it global and scalable.

---

## Definition of Done

- [x] CAS exists under runtime root (or configurable location)
- [x] Artifacts are stored and referenced by content hash
- [x] Node outputs can be reused across runs when inputs + params + tool versions match
- [x] CAS includes integrity verification (hash checks)
- [x] Eviction policy exists (quota-based) and is deterministic
- [x] Tests cover: put/get, hash integrity, reuse, eviction
- [x] All existing tests pass

---

## C36.1 — CAS Data Model + Layout

**Files:**
- `Docs/cas.md` (new)
- `claudeclockwork/cas/store.py` (new)
- `tests/test_cas_store.py`

**Change:**
- Layout example:
  - `.clockwork_runtime/cas/objects/<hash_prefix>/<hash>`
  - `.clockwork_runtime/cas/index.jsonl` (optional)
- Store metadata: size, mime, created_at, producer (tool/node id).

**Acceptance:**
- Same file always yields same object id.

---

## C36.2 — Node Cache Key Integration

**Files:**
- Work graph cache (Phase 30)
- Router/tool version stamping (Phase 22/26)
- `tests/test_node_cache_key_cas.py`

**Change:**
- Node cache key includes:
  - input artifact hashes
  - params hash
  - tool/version id
- Cache stores outputs as CAS object references.

**Acceptance:**
- Re-running the same node reuses CAS outputs.

---

## C36.3 — Transport Integration

**Files:**
- Worker artifact transport (Phase 35)
- `claudeclockwork/cas/pack.py` (new)

**Change:**
- Bundle inputs as CAS refs + missing objects.
- Worker can request missing objects and verify integrity.

**Acceptance:**
- Worker run succeeds with only CAS refs + transported objects.

---

## C36.4 — Eviction + Quota

**Files:**
- `claudeclockwork/cas/evict.py` (new)
- `Docs/cas_eviction.md` (new)
- `tests/test_cas_eviction.py`

**Change:**
- Quota config (max bytes, max objects).
- Deterministic eviction (oldest-first, stable ordering).
- Never evict objects referenced by “pinned” bundles (optional flag).

**Acceptance:**
- Eviction behavior is reproducible and does not corrupt referenced bundles.

---
