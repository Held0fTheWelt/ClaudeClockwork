# Runbook: Workers and CAS

Content-addressed store (CAS) and worker lifecycle.

## Verify workers and CAS

1. **Runtime root:** Ensure `.clockwork_runtime/` exists (`clockwork first-run` if not).
2. **CAS path:** CAS uses `.clockwork_runtime/cas/` (or configured path). Directory must be writable.
3. **Validation:** Run a skill that writes to CAS (e.g. capability map build); check that artifacts appear under `.clockwork_runtime/` and no permission errors in output.
4. **Workers:** For local worker, no extra process. For remote workers, see [worker_protocol.md](../worker_protocol.md).

**Rollback:** Remove only generated artifacts under `.clockwork_runtime/cas/` if needed; do not remove runtime root config.

---

## Eviction and quota

1. **Policy:** Eviction policy is configured per project (see [cas_eviction.md](../cas_eviction.md)).
2. **Manual eviction:** Use documented CLI or delete specific CAS keys if supported.
3. **Validation:** Re-run a pipeline; cache miss is acceptable; no crash.

**Rollback:** Restore from backup if CAS was cleared and rebuild is expensive; otherwise accept cache rebuild.
