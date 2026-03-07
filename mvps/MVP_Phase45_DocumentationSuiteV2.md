# MVP Phase 45 — Documentation Suite v2 (Runbooks, Tutorials, Troubleshooting)

**Goal:** Produce a complete, task-oriented documentation suite that matches the platform’s current capabilities and failure taxonomy, with stable cross-links and a troubleshooting-first structure.

---

## Definition of Done

- [x] Docs index links to all major guides
- [x] Runbooks exist (install/upgrade, workers+CAS, work graphs, plugins, incidents/exports)
- [x] Troubleshooting organized by error codes
- [x] Link-lint reports zero broken internal links
- [x] Docs are deterministic (no “handwave” steps)
- [x] All existing tests pass

---

## D45.1 — Docs Index + Navigation
Create/update `Docs/INDEX.md` with a clear navigation structure.

## D45.2 — Troubleshooting by Error Codes
Create `Docs/troubleshooting.md` aligned to the failure taxonomy.

## D45.3 — Runbooks
Create `Docs/runbooks/` and include validation + rollback steps per runbook.

## D45.4 — Doc QA Gate
Add/extend a docs gate to enforce link integrity and required docs presence.

---
