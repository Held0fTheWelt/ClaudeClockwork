# MVP Phase 33 — Multi-Repo / Multi-Project Orchestration (Without Coupling)

**Goal:** Support multiple repos/projects under a single “workspace” concept, without path coupling: per-project runtime roots, per-project profiles, and cross-repo references via versioned bundles, not direct paths.

**Why now:** After split pain (Clockwork vs LlamaCode), you need a first-class boundary model so tasks do not disappear and artifacts do not mix.

---

## Definition of Done

- [ ] Workspace concept exists (config + discovery)
- [ ] Each project has:
  - its own runtime root
  - its own router profiles
  - its own telemetry streams
- [ ] Cross-project references are via exported bundles (Phase 23), not file paths
- [ ] Boundary enforcement prevents writes outside the active project root
- [ ] Tests cover: workspace switching + boundary enforcement
- [ ] All existing tests pass

---

## W33.1 — Workspace Config + Discovery

**Files:**
- `Docs/workspaces.md` (new)
- `claudeclockwork/workspace/config.py`
- `tests/test_workspace.py`

**Change:**
- Workspace config lists projects:
  - repo root
  - runtime root
  - allowed exports/imports

**Acceptance:**
- Workspace discovery is deterministic.

---

## W33.2 — Boundary Enforcement

**Files:**
- `claudeclockwork/workspace/boundary.py`
- Capability policy integration

**Change:**
- Deny writes outside project root except runtime root.
- Deny reading sibling repos unless explicitly allowed via imported bundles.

**Acceptance:**
- Attempt to write outside boundary fails with `policy_denied`.

---

## W33.3 — Bundle Import/Link (No Hard Paths)

**Files:**
- Evidence exporter (Phase 23)
- `claudeclockwork/workspace/bundle_import.py`

**Change:**
- Allow importing a redacted evidence bundle into a project as a versioned artifact.
- Reference other project state by bundle id/version, not path.

**Acceptance:**
- Import produces a stable index and does not modify other repos.

---

## W33.4 — Orchestrator Mode

**Files:**
- Orchestrator agent prompt/contract (existing structure)
- `Docs/orchestrator_mode.md` (new)

**Change:**
- Orchestrator can:
  - select project
  - run work graph
  - export incident bundle
  - propose next actions

**Acceptance:**
- Orchestrator respects workspace boundaries.

---
