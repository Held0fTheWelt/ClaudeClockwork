# MVP Phase 15 — Skill Discovery Wave

**Goal:** Create 6 new skills that emerge naturally from what Clockwork already does well. These skills close gaps in the current skill set — particularly around git-aware summarization, automated test execution, dependency analysis, and config validation. Each new skill follows the full manifest + native implementation pattern established in Phase 14.

**Source finding:** NEW_MVPS.md — "Check, if a new skill could be invented by what has been done, or done again."

**Rationale per skill:**
1. `git_summary` — agents currently have no structured way to get git context (log, diff, blame) as a skill output
2. `test_run` — pytest is called manually; no skill wraps test execution with structured pass/fail/coverage results
3. `skill_health` — no consolidated health check across manifests, bridges, and entrypoints
4. `changelog_generate` — CHANGELOG is updated manually; git log → CHANGELOG entry is automatable
5. `dependency_graph` — no skill maps which skills are called in sequence (evidence pipeline dependencies)
6. `config_validate` — `configs/` and `.claude/config/` have JSON/YAML files with no validation skill

---

## Definition of Done

- [ ] `git_summary` implemented (native, `claudeclockwork/core/ops/git_summary.py`)
- [ ] `test_run` implemented (native, `claudeclockwork/core/ops/test_run.py`)
- [ ] `skill_health` implemented (native, `claudeclockwork/core/ops/skill_health.py`)
- [ ] `changelog_generate` implemented (native, `claudeclockwork/core/ops/changelog_generate.py`)
- [ ] `dependency_graph` implemented (native, `claudeclockwork/core/analysis/dependency_graph.py`)
- [ ] `config_validate` implemented (native, `claudeclockwork/core/ops/config_validate.py`)
- [ ] Each skill has a full manifest package: `manifest.json`, `skill.py`, `__init__.py` in `.claude/skills/<category>/<skill_id>/`
- [ ] `tests/test_skill_discovery_phase15.py` — 4 tests per skill = 24 tests
- [ ] Total manifest skills reported by `capability_map_build` is ≥ 103 (97 existing + 6 new)

---

## S15.1 — `git_summary` (ops category)

**Native location:** `claudeclockwork/core/ops/git_summary.py`
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

**Permissions:** `["repo:read"]`

---

## S15.2 — `test_run` (ops category)

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
- Use `pytest --tb=short -q` and parse terminal output; alternatively use `--json-report` if `pytest-json-report` is available (fall back to terminal parsing if import fails)
- This skill does NOT modify any files; it reads test output only
- `exit_code` 0 → `status: ok`; non-zero → `status: fail` with failure details in output (not an exception)

**Permissions:** `["repo:read"]`

---

## S15.3 — `skill_health` (ops category)

**Native location:** `claudeclockwork/core/ops/skill_health.py`
**Class:** `SkillHealthSkill(SkillBase)`
**Manifest package:** `.claude/skills/ops/skill_health/`

**Logic:** Walk all `.claude/skills/*/manifest.json` files. For each manifest skill, perform four checks and collect issues. Return aggregate health counts.

**Issue types checked:**
- `missing_bridge` — `legacy_bridge` key is true but the referenced `.claude/tools/skills/<id>.py` file does not exist
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

## S15.4 — `changelog_generate` (docs category)

**Native location:** `claudeclockwork/core/ops/changelog_generate.py`
**Class:** `ChangelogGenerateSkill(SkillBase)`
**Manifest package:** `.claude/skills/docs/changelog_generate/`

**Logic:** Run `git log --oneline` since an optional tag or for the last N commits. Classify each commit into a type using conventional commit prefixes (`feat:`, `fix:`, `chore:`, `refactor:`, `docs:`, `test:`). Format as a markdown CHANGELOG entry. Optionally write to a file.

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

**Permissions:** `["repo:read", "docs:write"]`

---

## S15.5 — `dependency_graph` (analysis category)

**Native location:** `claudeclockwork/core/analysis/dependency_graph.py`
**Class:** `DependencyGraphSkill(SkillBase)`
**Manifest package:** `.claude/skills/analysis/dependency_graph/`

**Logic:** Scan `.claude/tasks/` task YAML/MD files and `.claude/skills/*/skill.py` for `run_manifest_skill(` call patterns. Extract the `skill_id` argument string from each call site. Build a directed adjacency list (`from_skill → calls → to_skill`). Also scan evidence pipeline task files for sequential skill references.

**Inputs:**
- `root` (str, optional — defaults to working directory)
- `format` (str: `"json"` | `"markdown"`, default `"json"`)

**Outputs:**
- `nodes` (list of skill_id strings)
- `edges` (list of `{from, to, via}` — `via` is the file path where the dependency was found)
- `edge_count` (int)
- `graph_text` (str — markdown adjacency list, only present when `format` is `"markdown"`)

**Implementation notes:**
- Use `re.findall(r'run_manifest_skill\(\s*["\'](\w+)["\']', source_text)` as the primary extraction pattern
- Do not attempt to execute any scanned files

**Permissions:** `["repo:read"]`

---

## S15.6 — `config_validate` (ops category)

**Native location:** `claudeclockwork/core/ops/config_validate.py`
**Class:** `ConfigValidateSkill(SkillBase)`
**Manifest package:** `.claude/skills/ops/config_validate/`

**Logic:** Walk the specified config directories. For each `.json` file attempt `json.loads()`; for each `.yaml` / `.yml` file attempt `yaml.safe_load()` (with `ImportError` fallback to skip YAML files gracefully if PyYAML is absent). Collect all parse errors. Return counts and issue list.

**Inputs:**
- `config_paths` (list of str, optional — defaults to `[".claude/config/", "configs/"]`)

**Outputs:**
- `files_checked` (int)
- `valid` (int)
- `invalid` (int)
- `issues` (list of `{path, error}`)

**Implementation notes:**
- Relative paths in `config_paths` are resolved against the working directory
- Non-existent directories are skipped silently (not an error)
- Binary files and files without `.json`/`.yaml`/`.yml` extensions are skipped

**Permissions:** `["repo:read"]`

---

## S15.7 — Tests (`tests/test_skill_discovery_phase15.py`)

4 tests per skill × 6 skills = 24 tests. Pattern per skill:

1. **Registry check** — skill ID is present in the registry returned by `build_registry(ROOT)`
2. **Status check** — `run_manifest_skill(...)` returns a dict with `"status"` key that is either `"ok"` or `"fail"` (never `None`, never raises)
3. **Output keys** — output dict contains all documented required output keys
4. **Empty/default inputs** — calling with `{}` (all inputs optional) does not raise an unhandled exception

```python
# Example test pattern (git_summary shown)

def test_git_summary_in_registry():
    registry = build_registry(ROOT)
    assert registry.get("git_summary") is not None

def test_git_summary_returns_status():
    result = run_manifest_skill({"skill_id": "git_summary", "inputs": {}}, ROOT)
    assert result.get("status") in ("ok", "fail")

def test_git_summary_output_keys():
    result = run_manifest_skill({"skill_id": "git_summary", "inputs": {}}, ROOT)
    if result["status"] == "ok":
        for key in ("commits", "files_changed", "commit_count"):
            assert key in result["outputs"]

def test_git_summary_defaults():
    # No required inputs — must not raise
    result = run_manifest_skill({"skill_id": "git_summary", "inputs": {}}, ROOT)
    assert result is not None
```

---

## Implementation Pattern

All new skills are fully native (no `LegacySkillAdapter`). Each skill package follows the established structure:

```
.claude/skills/<category>/<skill_id>/
  manifest.json       ← new; legacy_bridge: false
  skill.py            ← re-exports or thin wrapper over claudeclockwork.core module
  __init__.py         ← empty
```

```json
{
  "id": "<skill_id>",
  "category": "<category>",
  "description": "<one-line description>",
  "entrypoint": "claudeclockwork.core.<subpackage>.<module>:<ClassName>",
  "legacy_bridge": false,
  "permissions": ["repo:read"],
  "inputs": {},
  "outputs": {}
}
```

The canonical implementation lives in `claudeclockwork/core/<subpackage>/<module>.py` and inherits from `SkillBase`. No corresponding legacy `.py` is created in `.claude/tools/skills/` — these are new skills, not promotions.

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
| `.claude/skills/ops/git_summary/manifest.json` | New manifest skill package |
| `.claude/skills/ops/git_summary/skill.py` | New |
| `.claude/skills/ops/git_summary/__init__.py` | New (empty) |
| `.claude/skills/ops/test_run/manifest.json` | New manifest skill package |
| `.claude/skills/ops/test_run/skill.py` | New |
| `.claude/skills/ops/test_run/__init__.py` | New (empty) |
| `.claude/skills/ops/skill_health/manifest.json` | New manifest skill package |
| `.claude/skills/ops/skill_health/skill.py` | New |
| `.claude/skills/ops/skill_health/__init__.py` | New (empty) |
| `.claude/skills/docs/changelog_generate/manifest.json` | New manifest skill package |
| `.claude/skills/docs/changelog_generate/skill.py` | New |
| `.claude/skills/docs/changelog_generate/__init__.py` | New (empty) |
| `.claude/skills/analysis/dependency_graph/manifest.json` | New manifest skill package |
| `.claude/skills/analysis/dependency_graph/skill.py` | New |
| `.claude/skills/analysis/dependency_graph/__init__.py` | New (empty) |
| `.claude/skills/ops/config_validate/manifest.json` | New manifest skill package |
| `.claude/skills/ops/config_validate/skill.py` | New |
| `.claude/skills/ops/config_validate/__init__.py` | New (empty) |
| `tests/test_skill_discovery_phase15.py` | New — 24 tests (4 per skill × 6 skills) |

---

## Dependencies

- Phase 14 (`NativeSkills`) complete — native skill pattern (`SkillBase`, manifest `legacy_bridge: false`) is established and tested
- `claudeclockwork/core/analysis/` directory may need to be created if `dependency_graph` is the first skill in that subpackage; add `__init__.py`
- `git` must be available in `PATH` for `git_summary` and `changelog_generate` (checked at runtime; graceful error if absent)
- `pytest` must be available in `PATH` for `test_run` (checked at runtime; graceful error if absent)
- PyYAML is optional for `config_validate` — skill degrades gracefully (skips `.yaml` files) if not installed

## Notes

- None of the 6 new skills have legacy equivalents in `.claude/tools/skills/` — they are net-new additions, not promotions
- `test_run` must not be called during CI runs that are themselves running tests (would cause recursion); gate this with a `DRY_RUN` environment variable check
- `dependency_graph` output is intentionally best-effort: it uses static text scanning, not import tracing; dynamic `run_manifest_skill` calls with variable skill IDs will not be captured

---

## Acceptance Criteria

- `python3 -m claudeclockwork.cli --skill-id capability_map_build --inputs '{}'` reports `manifest_skill_count >= 103`
- All 6 new skills are discoverable: `python3 -m claudeclockwork.cli --skill-id <id> --inputs '{}'` returns a response for each of the 6 skill IDs
- `python3 -m claudeclockwork.cli --skill-id config_validate --inputs '{}'` returns `status: ok` and a `files_checked` count greater than 0 on the Clockwork repository
- `python3 -m claudeclockwork.cli --skill-id skill_health --inputs '{}'` returns `total >= 97` (all existing manifest skills scanned)
- 24 new tests in `tests/test_skill_discovery_phase15.py` pass
- All pre-existing tests continue to pass (no regression)
