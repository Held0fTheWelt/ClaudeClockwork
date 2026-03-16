# MVP Phase 37 — Workspace UX & Project Templates (Onboarding)

**Goal:** Make workspaces easy and safe to use: project templates, onboarding flows, and a workspace dashboard that reduces operator errors (wrong repo, mixed runtime roots).

**Why now:** Workspaces (Phase 33) are powerful but error-prone without UX. After Remote Workers/CAS tracks, operator clarity becomes even more important.

---

## Definition of Done

- [x] `clockwork new` (or equivalent) creates a new project from templates
- [x] Workspace dashboard exists (CLI/TUI) showing:
  - active project
  - runtime root
  - recent runs + failures
  - current version
- [x] Guardrails exist: clear warnings before modifying non-active project
- [x] Workspace import wizard exists for existing repos (minimal)
- [x] Documentation exists (templates, dashboard, import)
- [x] Tests cover template creation + workspace switching guardrails
- [x] All existing tests pass

---

## U37.1 — Project Templates

**Files:**
- `templates/` (new)
- `Docs/project_templates.md` (new)

**Change:**
- Provide at least 2 templates:
  - `python_lib`
  - `docs_only`
- Templates include:
  - minimal README
  - suggested runtime root
  - basic `.gitignore` snippets

**Acceptance:**
- Template creation is deterministic and idempotent.

---

## U37.2 — `clockwork new` Command

**Files:**
- `claudeclockwork/cli/new_project.py`
- `tests/test_new_project.py`

**Change:**
- Create repo skeleton from template.
- Add workspace entry and set as active project.

**Acceptance:**
- Re-running with same name fails safely with an actionable error.

---

## U37.3 — Workspace Dashboard (CLI/TUI)

**Files:**
- `claudeclockwork/cli/workspace_dashboard.py`
- `Docs/workspace_dashboard.md` (new)

**Change:**
- Show:
  - active project
  - last N runs (status, duration)
  - top errors (from telemetry)
  - quick links (paths) to runtime root and latest export bundle

**Acceptance:**
- Output ordering is stable and deterministic.

---

## U37.4 — Guardrails (Wrong Project Protection)

**Files:**
- Workspace boundary system (Phase 33)
- `claudeclockwork/workspace/guards.py`
- `tests/test_workspace_guards.py`

**Change:**
- Before destructive actions:
  - print active project
  - require explicit confirmation token (optional)
- In non-interactive/CI:
  - require explicit flag to proceed

**Acceptance:**
- Attempts to modify a non-active project are blocked by default.

---

## U37.5 — Import Wizard (Minimal)

**Files:**
- `claudeclockwork/cli/import_project.py`
- `Docs/import_project.md` (new)

**Change:**
- Import an existing repo into workspace config:
  - detect repo root
  - propose runtime root
  - validate boundaries

**Acceptance:**
- Import produces stable workspace config entries.

---
