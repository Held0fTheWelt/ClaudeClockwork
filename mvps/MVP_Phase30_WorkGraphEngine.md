# MVP Phase 30 — Work Graph Engine (Tasks as DAG)

**Goal:** Replace linear “do everything” runs with a deterministic Work Graph (DAG): plan, execute, validate, fix, export — with caching and clear failure attribution.

**Why now:** After eval harness (Phase 25) and evidence export (Phase 23), DAG-based execution reduces task loss and makes runs resumable.

---

## Definition of Done

- [ ] Work Graph spec exists (node types, edges, artifacts)
- [ ] Minimal DAG runner exists with deterministic scheduling
- [ ] Node outputs are cached (hash-based) under runtime root
- [ ] Failure reporting shows the exact failed node and reason
- [ ] CLI can run a graph and resume from cache
- [ ] Tests cover: ordering, caching, resume, failure reporting
- [ ] All existing tests pass

---

## G30.1 — Graph Spec + Contracts

**Files:**
- `Docs/work_graph_spec.md` (new)
- `.claude/contracts/schemas/work_graph.schema.json` (new)

**Change:**
- Define nodes:
  - `skill_call`
  - `agent_run`
  - `gate_check`
  - `export_bundle`
- Define artifact passing by references (paths/hashes).

**Acceptance:**
- Schema validates a sample graph.

---

## G30.2 — Deterministic DAG Runner

**Files:**
- `claudeclockwork/workgraph/runner.py`
- `claudeclockwork/workgraph/cache.py`
- `tests/test_workgraph_runner.py`

**Change:**
- Topological ordering with stable tie-breaks.
- Cache key = node id + inputs hash + tool versions.

**Acceptance:**
- Running twice without changes reuses cache.

---

## G30.3 — Resume + Failure Attribution

**Files:**
- `claudeclockwork/cli/run_graph.py`
- `Docs/run_graph.md` (new)

**Change:**
- Resume support from cached nodes.
- Emit a failure summary with node context + error codes.

**Acceptance:**
- A deliberately failing node stops the run and prints a clear summary.

---

## G30.4 — Integration with Gates & Export

**Files:**
- Gate modules (existing)
- Exporter (Phase 23)

**Change:**
- Allow graphs to include gate nodes and export nodes.

**Acceptance:**
- A graph can run: “execute → gate → export”.

---
