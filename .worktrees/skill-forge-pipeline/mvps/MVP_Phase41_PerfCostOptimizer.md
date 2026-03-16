# MVP Phase 41 — Performance & Cost Optimizer (Cache-Aware Routing + Scheduling)

**Goal:** Optimize performance and cost by jointly considering:
- router choices (model/tool)
- worker placement (local vs remote)
- CAS availability (cache hits)
- budget profiles (fast/balanced/strong)

**Why now:** Router v3 (26), Workers (35), CAS (36), and Scoreboards (25) enable real cost/perf optimization with measurable constraints.

---

## Definition of Done

- [x] Cost model exists (time, GPU minutes, memory hints)
- [x] Cache-aware planning exists (prefer nodes with existing CAS inputs/outputs)
- [x] Worker-aware scheduling exists (choose worker based on capability + load + locality)
- [x] Budget profiles enforce constraints deterministically
- [x] Regression gates exist for cost/perf (latency and cost budgets)
- [x] All existing tests pass

---

## O41.1 — Cost Model Contract

**Files:**
- `Docs/cost_model.md` (new)
- `claudeclockwork/optimizer/cost_model.py`
- `tests/test_cost_model.py`

**Change:**
- Define cost fields:
  - expected_latency_ms
  - expected_gpu_minutes
  - expected_memory_mb
  - expected_failure_risk
- Provide defaults and deterministic estimation functions.

**Acceptance:**
- Given the same inputs, cost estimates are identical.

---

## O41.2 — Cache-Aware Planner

**Files:**
- Work graph runner (Phase 30)
- CAS store (Phase 36)
- `claudeclockwork/optimizer/cache_aware.py`
- `tests/test_cache_aware_planner.py`

**Change:**
- Plan node execution order / worker placement to maximize cache hits.
- Prefer reusing CAS outputs when node cache key matches.

**Acceptance:**
- On repeated runs, planner increases cache hit rate deterministically.

---

## O41.3 — Worker Placement Policy

**Files:**
- Worker dispatcher (Phase 35)
- `claudeclockwork/optimizer/worker_placement.py`
- `tests/test_worker_placement.py`

**Change:**
- Choose worker based on:
  - required resources (GPU)
  - capability allowlists
  - current worker load (stubbed metrics)
  - data locality (CAS object presence)

**Acceptance:**
- Placement decision is explainable and contract-compliant.

---

## O41.4 — Budget Profiles + Gates

**Files:**
- Router budget config (Phase 26)
- `claudeclockwork/core/gates/cost_perf_gate.py` (new)
- `tests/test_cost_perf_gate.py`

**Change:**
- Enforce:
  - max expected cost per run
  - latency budgets
  - fallback policies

**Acceptance:**
- A simulated budget violation fails the gate with actionable diagnostics.

---
