# MVP Phase 16 — Skill Discovery Wave

**Goal:** Create 6 new skills that emerge naturally from what Clockwork already does well. These skills close gaps in the current skill set — particularly around git-aware summarization, automated test execution, dependency analysis, and config validation. Each new skill follows the full manifest + native implementation pattern established in Phase 14.

**Source finding:** NEW_MVPS.md — "Check, if a new skill could be invented by what has been done, or done again."

**Rationale per skill:**
1. `git_summary` — agents currently have no structured way to get git context (log, diff, blame) as a skill output
2. `test_run` — pytest is called manually; no skill wraps test execution with structured pass/fail/coverage results
3. `skill_health` — no consolidated health check across manifests, bridges, and entrypoints
4. `changelog_generate` — CHANGELOG is updated manually; git log → CHANGELOG entry is automatable
5. `dependency_graph` — no skill maps which skills are called in sequence (evidence pipeline dependencies)
6. `config_validate` — `configs/` and `.claude/config/` have JSON/YAML files with no validation skill

**Prerequisite:** Phase 15 (Obsolete Data Prune) complete — repo must be clean before new skills are added.

---

## Definition of Done

- [x] `git_summary` implemented (native, `.claude/skills/ops/git_summary/skill.py`)
- [x] `test_run` implemented (native, `.claude/skills/ops/test_run/skill.py`)
- [x] `skill_health` implemented (native, `.claude/skills/ops/skill_health/skill.py`)
- [x] `changelog_generate` implemented (native, `.claude/skills/docs/changelog_generate/skill.py`)
- [x] `dependency_graph` implemented (native, `.claude/skills/analysis/dependency_graph/skill.py`)
- [x] `config_validate` implemented (native, `.claude/skills/ops/config_validate/skill.py`)
- [x] Each skill has a full manifest package: `manifest.json`, `skill.py`, `__init__.py` in `.claude/skills/<category>/<skill_id>/`
- [x] `tests/test_skill_discovery_phase16.py` — 4 tests per skill = 24 tests (all passing)
- [x] Total manifest skills reported by registry is ≥ 103 (104 actual)

---

## S16.1 — `git_summary` (ops category)

**Native location:** `.claude/skills/ops/git_summary/skill.py` (implementation in manifest package; optional mirror in `claudeclockwork/core/ops/git_summary.py` not required)
**Class:** `GitSummarySkill(SkillBase)`
**Manifest package:** `.claude/skills/ops/git_summary/`

**Logic:** Run `git log` and optionally `git diff` via `subprocess.run` (stdlib only — no third-party git library). Parse output into structured commit records. If `include_diff` is true, include a unified diff string.

**Inputs:**
- `root` (str, optional — repo root; defaults to working directory)
- `max_commits` (int, optional, default 10)
- `include_diff` (bool, optional, default false)

**Outputs:**
- `commits` (list of `{hash, author, date, message}`)
- `files_changed` (list of str — union of files touched across the commit range)
- `commit_count` (int)
- `diff_text` (str — only present when `include_diff` is true)

**Implementation notes:**
- `git log --oneline --format="%H|%an|%ad|%s" --date=short -n <max_commits>`
- `git diff --name-only HEAD~<max_commits>..HEAD` for `files_changed`
- Gracefully return empty lists if not inside a git repo (check return code)

**Permissions:** `["repo:read", "git:read"]`

---

## S16.2 — `test_run` (ops category)

**Native location:** `claudeclockwork/core/ops/test_run.py`
**Class:** `TestRunSkill(SkillBase)`
**Manifest package:** `.claude/skills/ops/test_run/`

**Logic:** Run `pytest` via `subprocess.run` against a specified test path. Parse output for pass/fail/error counts and individual failure messages. Optionally collect coverage percentage from `--cov` output.

**Inputs:**
- `test_path` (str, optional, default `"tests/"`)
- `marker` (str, optional — passed as `-m <marker>` to pytest)
- `coverage` (bool, optional, default false — adds `--cov=claudeclockwork --cov-report=term-missing`)

**Outputs:**
- `passed` (int)
- `failed` (int)
- `errors` (int)
- `duration_ms` (float)
- `coverage_pct` (float — only present when `coverage` is true)
- `failures` (list of `{test, message}`)
- `exit_code` (int)

**Implementation notes:**
- Use `pytest --tb=short -q` and parse terminal output
- `exit_code` 0 → `status: ok`; non-zero → `status: fail` with failure details in output (not an exception)
- Do NOT call during CI runs that are themselves running tests — gate with `CLOCKWORK_CI` environment variable

**Permissions:** `["repo:read"]`

---

## S16.3 — `skill_health` (ops category)

**Native location:** `claudeclockwork/core/ops/skill_health.py`
**Class:** `SkillHealthSkill(SkillBase)`
**Manifest package:** `.claude/skills/ops/skill_health/`

**Logic:** Walk all `.claude/skills/*/manifest.json` files. For each manifest skill, perform four checks and collect issues.

**Issue types checked:**
- `missing_bridge` — `legacy_bridge` key is truthy but the referenced `.claude/tools/skills/<id>.py` file does not exist
- `bad_entrypoint` — attempt `importlib.import_module` on the declared entrypoint module path; record import errors
- `invalid_manifest` — `json.loads()` fails on the `manifest.json` file
- `missing_metadata` — required keys (`id`, `category`, `description`, `entrypoint`) are absent from the manifest

**Inputs:**
- `root` (str, optional — defaults to working directory)

**Outputs:**
- `total` (int — total manifest skills scanned)
- `healthy` (int — skills with zero issues)
- `unhealthy` (int — skills with one or more issues)
- `issues` (list of `{skill_id, issue_type, detail}`)

**Permissions:** `["repo:read"]`

---

## S16.4 — `changelog_generate` (docs category)

**Native location:** `claudeclockwork/core/ops/changelog_generate.py`
**Class:** `ChangelogGenerateSkill(SkillBase)`
**Manifest package:** `.claude/skills/docs/changelog_generate/`

**Logic:** Run `git log --oneline` since an optional tag or for the last N commits. Classify each commit into a type using conventional commit prefixes. Format as a markdown CHANGELOG entry. Optionally write to a file.

**Commit classification rules:**
- `feat:` / `add` / `new` → `Added`
- `fix:` / `bug` → `Fixed`
- `refactor:` → `Changed`
- `docs:` / `doc` → `Documentation`
- `chore:` / `test:` / `ci:` → `Maintenance`
- Unclassified → `Changed`

**Inputs:**
- `since_tag` (str, optional — git tag or SHA to start from)
- `max_commits` (int, optional, default 20)
- `output_path` (str, optional — if provided, appends the generated entry to this file)
- `version_label` (str, optional, default `"Unreleased"`)

**Outputs:**
- `entries` (list of `{type, description, hash}`)
- `changelog_text` (str — formatted markdown block)
- `written` (bool — true if `output_path` was provided and write succeeded)

**Permissions:** `["repo:read", "docs:write", "git:read"]`

---

## S16.5 — `dependency_graph` (analysis category)

**Native location:** `claudeclockwork/core/analysis/dependency_graph.py`
**Class:** `DependencyGraphSkill(SkillBase)`
**Manifest package:** `.claude/skills/analysis/dependency_graph/`

**Logic:** Scan `.claude/tasks/` task YAML/MD files and `.claude/skills/*/skill.py` for `run_manifest_skill(` call patterns. Extract the `skill_id` argument string from each call site. Build a directed adjacency list.

**Inputs:**
- `root` (str, optional — defaults to working directory)
- `format` (str: `"json"` | `"markdown"`, default `"json"`)

**Outputs:**
- `nodes` (list of skill_id strings)
- `edges` (list of `{from, to, via}`)
- `edge_count` (int)
- `graph_text` (str — markdown adjacency list, only present when `format` is `"markdown"`)

**Permissions:** `["repo:read"]`

---

## S16.6 — `config_validate` (ops category)

**Native location:** `claudeclockwork/core/ops/config_validate.py`
**Class:** `ConfigValidateSkill(SkillBase)`
**Manifest package:** `.claude/skills/ops/config_validate/`

**Logic:** Walk the specified config directories. For each `.json` file attempt `json.loads()`; for each `.yaml`/`.yml` file attempt `yaml.safe_load()` (with `ImportError` fallback). Collect all parse errors.

**Inputs:**
- `config_paths` (list of str, optional — defaults to `[".claude/config/", "configs/"]`)

**Outputs:**
- `files_checked` (int)
- `valid` (int)
- `invalid` (int)
- `issues` (list of `{path, error}`)

**Permissions:** `["repo:read"]`

---

## S16.7 — Tests (`tests/test_skill_discovery_phase16.py`)

4 tests per skill × 6 skills = 24 tests. Pattern per skill:

1. **Registry check** — skill ID is present in the registry
2. **Status check** — `run_manifest_skill(...)` returns `"status"` = `"ok"` or `"fail"` (never raises)
3. **Output keys** — output dict contains all documented required output keys
4. **Empty/default inputs** — calling with `{}` does not raise an unhandled exception

---

## Files Changed

| File | Change |
|------|--------|
| `claudeclockwork/core/ops/git_summary.py` | New native skill class |
| `claudeclockwork/core/ops/test_run.py` | New native skill class |
| `claudeclockwork/core/ops/skill_health.py` | New native skill class |
| `claudeclockwork/core/ops/changelog_generate.py` | New native skill class |
| `claudeclockwork/core/analysis/dependency_graph.py` | New native skill class |
| `claudeclockwork/core/ops/config_validate.py` | New native skill class |
| `.claude/skills/ops/git_summary/` | New manifest skill package |
| `.claude/skills/ops/test_run/` | New manifest skill package |
| `.claude/skills/ops/skill_health/` | New manifest skill package |
| `.claude/skills/docs/changelog_generate/` | New manifest skill package |
| `.claude/skills/analysis/dependency_graph/` | New manifest skill package |
| `.claude/skills/ops/config_validate/` | New manifest skill package |
| `tests/test_skill_discovery_phase16.py` | New — 24 tests (4 per skill × 6 skills) |

---

## Dependencies

- Phase 15 (Obsolete Data Prune) complete
- Phase 14 (NativeSkills) complete — native skill pattern established
- `claudeclockwork/core/analysis/` directory may need `__init__.py` if first skill there
- `git` must be available in `PATH` for `git_summary` and `changelog_generate`
- `pytest` must be available in `PATH` for `test_run`

## Acceptance Criteria

- `capability_map_build` reports `manifest_skill_count >= 103`
- All 6 new skills discoverable via CLI
- `config_validate` returns `files_checked > 0` on Clockwork repo
- `skill_health` returns `total >= 97`
- 24 new tests in `tests/test_skill_discovery_phase16.py` pass
- All pre-existing tests continue to pass
