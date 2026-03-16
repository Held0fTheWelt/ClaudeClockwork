# MVP Phase 46 — One-Command Demo Pipelines (Killer Examples)

**Goal:** Provide a small set of “one-command” demo pipelines that prove platform value end-to-end: work graph execution, gates, incident handling, and export bundles.

---

## Definition of Done

- [x] 3 demo pipelines exist and run end-to-end locally
- [x] Each demo has a work graph + README + expected outputs
- [x] Demos are deterministic (seeded, stubbed)
- [x] CI runs at least one demo in smoke mode
- [x] All existing tests pass

---

## E46.1 — Demo Graph Specs
Create demo graphs under `demos/<demo>/graph.*`.

## E46.2 — Deterministic Stubs
Provide stubs for heavy steps so demos run on CPU-only machines.

## E46.3 — Demo Smoke on CI
Add CI smoke runner for at least one demo.

---
