# MVP Phase 39 — Reliability Engineering (Chaos, Recovery, Rollbacks)

**Goal:** Make reliability a first-class property: deterministic chaos tests, recovery playbooks, end-to-end rollback for work graphs, and enforceable SLO thresholds.

**Why now:** After Sandboxing (34), Distributed Workers (35), CAS (36), Workspaces UX (37), and Knowledge Base (38), the system must prove it can fail safely and recover predictably.

---

## Definition of Done

- [x] Reliability test suite exists and runs deterministically in CI
- [x] Chaos scenarios exist (timeouts, worker kill, CAS corruption, network stub failures)
- [x] Recovery strategies exist (retry policies, fallback to local worker, cache bypass)
- [x] End-to-end rollback works for a failed work graph run (snapshot + restore)
- [x] SLO thresholds are defined and enforced (failure rate, p95 latency budgets)
- [x] Incident bundles capture enough info to reproduce (redacted)
- [x] All existing tests pass

---

## R39.1 — Failure Taxonomy + Retry Policy Consolidation

**Files:**
- `Docs/failure_taxonomy.md` (Phase 32) or extend if already present
- `claudeclockwork/workers/retry.py` (Phase 35)
- `tests/test_retry_policy.py`

**Change:**
- Define retryable vs non-retryable errors.
- Ensure consistent error codes across router, workers, workgraph, LocalAI.

**Acceptance:**
- Retry policy produces deterministic decisions for given error codes.

---

## R39.2 — Chaos Scenarios (Deterministic)

**Files:**
- `tests/chaos/` (new)
- `Docs/chaos_suite.md` (new)

**Change:**
Create chaos tests that simulate:
- worker termination mid-node
- timeout during external runner
- CAS object corruption (hash mismatch)
- transient transport failure (stubbed)

**Acceptance:**
- Chaos suite runs without flakiness using deterministic seeds/stubs.

---

## R39.3 — Recovery Playbooks + Auto-Fallbacks

**Files:**
- `Docs/recovery_playbooks.md` (new)
- `claudeclockwork/workgraph/recovery.py` (new)

**Change:**
- Implement fallback strategies:
  - retry with backoff
  - reroute node to local worker
  - bypass cache and recompute
- Capture recovery actions in telemetry.

**Acceptance:**
- A simulated failure results in a documented fallback path.

---

## R39.4 — Work Graph Rollback (Snapshot + Restore)

**Files:**
- Snapshot system (existing or new)
- `claudeclockwork/workgraph/snapshot.py`
- `tests/test_workgraph_rollback.py`

**Change:**
- Snapshot before executing a graph.
- On failure, restore repo state (if applicable) and runtime state pointers.
- Write rollback evidence to runtime root.

**Acceptance:**
- Forced failure triggers rollback and returns state to pre-run deterministically.

---

## R39.5 — SLO Gate (Reliability Budgets)

**Files:**
- `Docs/slo.md` (new)
- `claudeclockwork/core/gates/slo_gate.py` (new)
- `tests/test_slo_gate.py`

**Change:**
- Enforce thresholds:
  - max failure rate
  - p95 latency budget
  - regression thresholds (tie into Phase 25)

**Acceptance:**
- Synthetic SLO violation fails the gate with clear diagnostics.

---
