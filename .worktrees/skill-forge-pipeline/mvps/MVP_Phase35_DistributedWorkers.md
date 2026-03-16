# MVP Phase 35 — Distributed Workers (Remote Execution / Agent Runners)

**Goal:** Enable executing Work Graph nodes on remote workers (e.g., GPU machine, CI runner, separate host) with deterministic job envelopes, artifact shipping, retries, and idempotency.

**Why now:** Work Graph Engine (Phase 30) defines node-level work; sandboxing (Phase 34) defines security boundaries. Remote workers unlock scale.

---

## Definition of Done

- [x] Worker protocol exists (job envelope schema + signed/hashed payload)
- [x] A local “worker runner” exists (same host) to validate protocol end-to-end
- [x] Artifact shipping exists via bundles (redacted where required)
- [x] Idempotency keys prevent duplicate execution
- [x] Retry/timeout semantics are deterministic
- [x] Tests cover: envelope validation, idempotency, retry, artifact upload/download
- [x] All existing tests pass

---

## W35.1 — Job Envelope Contract

**Files:**
- `.claude/contracts/schemas/worker_job_envelope.schema.json` (new)
- `Docs/worker_protocol.md` (new)

**Change:**
- Envelope includes:
  - job_id, idempotency_key
  - node spec (skill/tool/agent)
  - input artifact references (hashes)
  - resource hints (cpu/gpu, timeout)
  - security context (allowed roots, capabilities)
  - expected output schema

**Acceptance:**
- Schema validates sample envelopes.

---

## W35.2 — Local Worker (Same Machine) Reference Implementation

**Files:**
- `claudeclockwork/workers/local_worker.py` (new)
- `claudeclockwork/workers/dispatcher.py` (new)
- `tests/test_local_worker.py`

**Change:**
- Implement a worker that processes envelopes using existing runtime.
- Record telemetry and output artifacts under runtime root.

**Acceptance:**
- A graph node can be executed via dispatcher → local worker → result.

---

## W35.3 — Artifact Shipping (Bundle-based)

**Files:**
- Evidence/export bundle system (Phase 23)
- `claudeclockwork/workers/artifact_transport.py` (new)
- `tests/test_artifact_transport.py`

**Change:**
- Use content-addressed artifacts (Phase 36 will extend).
- Transport as zipped bundles with manifest + hashes.
- Redact where required.

**Acceptance:**
- Worker receives inputs and returns outputs with hash verification.

---

## W35.4 — Retry & Idempotency

**Files:**
- `claudeclockwork/workers/retry.py` (new)
- `tests/test_worker_retry_idempotency.py`

**Change:**
- Define retry policy:
  - retryable errors (timeouts, transient)
  - non-retryable errors (policy denied, validation)
- Idempotency ensures repeated dispatch doesn’t duplicate work.

**Acceptance:**
- Duplicate dispatch returns cached result for same idempotency_key.

---

## W35.5 — Remote Worker Stub (Protocol-only)

**Files:**
- `Docs/remote_worker_stub.md` (new)
- Optional: `claudeclockwork/workers/http_worker_client.py` (stub)

**Change:**
- Define how a remote worker would be contacted (HTTP/WebSocket/CLI).
- Keep actual networking minimal for MVP; focus on protocol correctness.

**Acceptance:**
- Protocol is stable and ready for real networking in a later phase.

---
