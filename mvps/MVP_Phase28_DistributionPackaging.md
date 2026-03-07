# MVP Phase 28 — Distribution & Installation (Packaging)

**Goal:** Make ClaudeClockwork installable and upgradable like a real tool: reproducible setup, first-run checks, and deterministic environment validation.

**Why now:** After Phase 22 (release discipline) and Phase 19 (runtime root normalization), distribution becomes tractable and safe.

---

## Definition of Done

- [x] A supported installation path exists (pick at least one):
  - `pipx install ...` OR
  - `pip install ...` OR
  - single-file `bootstrap.py` that creates a venv and installs dependencies
- [x] First-run wizard exists (creates runtime root, validates versions, checks optional deps)
- [x] Deterministic environment check command exists (`env_check`)
- [x] Documentation exists: install, upgrade, uninstall
- [x] CI verifies packaging artifacts (build + smoke install)
- [x] All existing tests pass

---

## P28.1 — Packaging Strategy

**Files:**
- `pyproject.toml` (preferred) or `setup.cfg`/`setup.py`
- `Docs/install.md` (new)

**Change:**
- Choose packaging standard and define supported Python versions.
- Ensure entrypoints expose a stable CLI command.

**Acceptance:**
- `pip install -e .` works locally and exposes CLI.

---

## P28.2 — First-Run Wizard

**Files:**
- `claudeclockwork/cli/first_run.py`
- `Docs/first_run.md` (new)

**Change:**
- Create runtime root (Phase 19), write minimal config, verify permissions.
- Optional dependency checks (LocalAI runners, GPU detection, etc.).

**Acceptance:**
- Running first-run twice is idempotent.

---

## P28.3 — Environment Check Command

**Files:**
- `claudeclockwork/cli/env_check.py`
- `tests/test_env_check.py`

**Change:**
- Verify:
  - canonical version
  - runtime root exists/writable
  - required binaries (if any) are present
  - python version supported

**Acceptance:**
- `env_check` returns 0 when healthy, non-zero with actionable errors otherwise.

---

## P28.4 — CI Packaging Smoke Test

**Files:**
- CI workflow config
- `tests/test_packaging_smoke.py` (or script)

**Change:**
- Build wheel/sdist and install into a clean env.
- Run minimal CLI command(s).

**Acceptance:**
- Packaging smoke runs on CI without manual steps.

---
