# MVP Phase 43 — Multi-Repo Orchestrator v2 (Workspace Federation)

**Goal:** Orchestrate multiple repos/projects safely: federated workspaces, cross-project linking via bundles (never hard paths), global policy enforcement, and a high-level orchestrator mode.

**Why now:** You already have workspace boundaries (33) and bundle exports (23/36). This phase formalizes multi-repo operation without coupling.

---

## Definition of Done

- [x] Federated workspace config exists (multiple workspaces/projects)
- [x] Orchestrator can:
  - select project/workspace
  - run a work graph
  - export incident bundle
  - import bundle into another project (as an artifact, not as paths)
- [x] Global boundary enforcement prevents cross-repo writes
- [x] Cross-project linking uses bundle ids + versions only
- [x] Tests cover federation switching + boundary enforcement + bundle import
- [x] All existing tests pass

---

## F43.1 — Federation Config

**Files:**
- `Docs/workspace_federation.md` (new)
- `claudeclockwork/workspace/federation.py`
- `tests/test_workspace_federation.py`

**Change:**
- Support multiple workspace roots.
- Allow selecting active workspace + project deterministically.

**Acceptance:**
- Selection is stable and persists in config.

---

## F43.2 — Bundle Link/Import Workflow

**Files:**
- Bundle importer (Phase 33)
- `claudeclockwork/workspace/bundle_link.py` (new)
- `tests/test_bundle_link.py`

**Change:**
- Allow linking evidence bundles across projects:
  - store bundle under project runtime
  - index bundle metadata
  - allow queries without accessing other repo

**Acceptance:**
- No file paths outside project boundary are accessed.

---

## F43.3 — Orchestrator Mode (High-Level Commands)

**Files:**
- `Docs/orchestrator_mode.md` (Phase 33) or extend
- `claudeclockwork/cli/orchestrate.py` (new)
- `tests/test_orchestrator_cli.py`

**Change:**
- Commands:
  - `orchestrate run --workspace W --project P --graph G`
  - `orchestrate incident --last`
  - `orchestrate export-incident`
  - `orchestrate import-bundle`

**Acceptance:**
- Commands respect boundaries and produce deterministic output.

---

## F43.4 — Global Policy Enforcement

**Files:**
- Capability policy system (existing)
- `claudeclockwork/workspace/global_policy.py`
- `tests/test_global_policy.py`

**Change:**
- Enforce:
  - never write outside active project + runtime root
  - never read sibling repos unless via imported bundles

**Acceptance:**
- Violations fail deterministically with `policy_denied`.

---
