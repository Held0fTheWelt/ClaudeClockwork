# MVP Phase 45 — Documentation Suite v2 (Runbooks, Tutorials, Troubleshooting)

**Goal:** Produce a complete, task-oriented documentation suite that matches the platform’s current capabilities and failure taxonomy, with stable cross-links and a troubleshooting-first structure.

---

## Definition of Done

- <span style="color:#2563eb">**[x]**</span> Docs index links to all major guides
- <span style="color:#2563eb">**[x]**</span> Runbooks exist (install/upgrade, workers+CAS, work graphs, plugins, incidents/exports)
- <span style="color:#2563eb">**[x]**</span> Troubleshooting organized by error codes
- <span style="color:#2563eb">**[x]**</span> Link-lint reports zero broken internal links
- <span style="color:#2563eb">**[x]**</span> Docs are deterministic (no “handwave” steps)
- <span style="color:#2563eb">**[x]**</span> All existing tests pass

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
