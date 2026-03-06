# MVP Phase 10 — Plugin Compaction

**Goal:** Make `.claude/` a fully self-contained, deployable plugin unit. A consuming project should be able to copy `.claude/` (plus install the `claudeclockwork` package) and have the full Clockwork system. Currently, essential config (`configs/permissions.json`) and non-deployable project files (`mvps/`, `roadmaps/`, `.claude-development/`, `Docs/`) are scattered at the repo root with no clear "deploy this / don't deploy that" boundary.

**Source finding:** NEW_MVPS.md — "Everything that needs to be included in other projects resides inside the .claude folder"

---

## Definition of Done

- [ ] `configs/permissions.json` moved into `.claude/config/permissions.json`; all references updated
- [ ] `.claude/config/` is the single location for all Clockwork config (no root-level `configs/` directory)
- [ ] `.claude/DEPLOY.md` created — documents exactly what a consuming project copies and what `claudeclockwork` package version to install
- [ ] Non-deployable root directories marked with `_DO_NOT_DEPLOY` sentinels or documented in `.claude/DEPLOY.md` exclusion list: `mvps/`, `roadmaps/`, `Docs/`, `.claude-development/`, `validation_runs/`, `validation_runs_redacted/`, `scripts/`, `memory/`, `tests/`
- [ ] `CLAUDE.md` updated to reflect new config location and deploy boundary
- [ ] `configs/permissions.json` reference in `tests/test_gates.py` updated to `.claude/config/permissions.json`
- [ ] All existing tests pass

---

## P10.1 — Move `configs/permissions.json` into `.claude/config/`

**Finding:** `configs/permissions.json` is the only file in the root `configs/` directory and is the sole runtime-required config that lives outside `.claude/`. Moving it makes `.claude/` fully self-contained for deployment.

**Steps:**
1. Copy `configs/permissions.json` → `.claude/config/permissions.json`
2. Delete `configs/` directory
3. Update `tests/test_gates.py` — `test_permission_lint` loads `configs/permissions.json`; update path to `.claude/config/permissions.json`
4. Grep for any other references to `configs/permissions` across `claudeclockwork/` and `.claude/`:

```bash
grep -r "configs/permissions" . --include="*.py" --include="*.json" --include="*.md" --include="*.yaml"
# Must return zero results after change
```

5. If `.claude/skills/meta/manifest_validate/skill.py` references the old path, update it
6. If `claudeclockwork/runtime.py` or any other module uses the path, update those references

**Validation:**
```bash
# Confirm move succeeded
python3 -c "import json; json.load(open('.claude/config/permissions.json')); print('OK')"

# Confirm old location is gone
ls configs/ 2>&1 && echo FAIL || echo PASS
```

**Acceptance:** `grep -r "configs/permissions" .` returns zero results. `.claude/config/permissions.json` is valid JSON.

---

## P10.2 — Create `.claude/DEPLOY.md`

**Finding:** There is no authoritative document describing what a downstream project must copy. This creates ambiguity: deployers may copy dev-only directories (`mvps/`, `tests/`) or miss required config.

**Content requirements:**

### What to Copy
```
.claude/          # Entire directory — governance, agents, skills, config, contracts
```

### What to Install
```bash
pip install claudeclockwork
# or for local development:
pip install -e /path/to/ClaudeClockwork
```

### Post-Copy Setup
1. Update `.claude/VERSION` to record the Clockwork version being deployed
2. Create `.project/MEMORY.md` for the new project (use `.project/MEMORY.md` from Clockwork repo as template)
3. Create `.project/` directory structure: `Docs/Plans/`, `Docs/Review/`, `Docs/Critics/`, `Docs/References/`, `Docs/Documentation/`, `Docs/Tutorials/`, `memory/`
4. Update `.claude/config/permissions.json` to reflect the consuming project's permission profile

### Exclusion List (Clockwork-dev-only — do not copy)
| Directory / File | Reason |
|-----------------|--------|
| `mvps/` | Clockwork internal MVP plans |
| `roadmaps/` | Clockwork internal roadmaps |
| `.claude-development/` | Legacy development archive |
| `Docs/` | Legacy skill audit artifacts |
| `tests/` | Clockwork test suite (not deployable) |
| `scripts/` | Clockwork dev scripts |
| `validation_runs/` | Local validation output |
| `validation_runs_redacted/` | Redacted validation output |
| `memory/` | Dev session memory |
| `claudeclockwork/` | Runtime package — install via pip, do not copy raw |
| `CLAUDE.md` | Replace with project-specific CLAUDE.md |

### Runtime Package Note
The `claudeclockwork/` package lives outside `.claude/` by design. It is the execution runtime, not the governance layer. The `.claude/` directory contains governance rules, agent definitions, skill scripts, and config. They are distinct layers — `.claude/` is portable, `claudeclockwork/` is installed as a Python package dependency.

---

## P10.3 — Update `CLAUDE.md`

**Changes:**
1. Under "Directory Structure", replace the `configs/` entry with:
```
.claude/config/    # All Clockwork config (permissions.json, pricing, budgeting, routing).
                   # Previously: root-level configs/ (removed in Phase 10).
```

2. Add a new subsection under "Architecture" or "Deployment":
```
### Deployment Boundary
See `.claude/DEPLOY.md` for the authoritative list of what to copy when deploying Clockwork
to a new project. The deployable unit is `.claude/` + `pip install claudeclockwork`.
Root-level directories (mvps/, roadmaps/, tests/, Docs/, .claude-development/) are
Clockwork-development artifacts and must not be copied to consuming projects.
```

---

## Files Changed

| File | Change |
|------|--------|
| `configs/permissions.json` | Moved to `.claude/config/permissions.json` |
| `configs/` | Deleted (directory removed) |
| `.claude/DEPLOY.md` | New — deployment guide and exclusion list |
| `tests/test_gates.py` | Update `configs/permissions.json` path to `.claude/config/permissions.json` |
| `CLAUDE.md` | Note about config relocation; add Deployment Boundary section |

---

## Acceptance Criteria

- `grep -r "configs/permissions" .` returns zero results
- `.claude/config/permissions.json` exists and is valid JSON
- `.claude/DEPLOY.md` exists and lists all exclusion directories
- All existing tests pass
