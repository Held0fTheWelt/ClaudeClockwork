<!-- current-version: 17.7.2 -->
# CHANGELOG

Dieses Changelog ist der **Single Source of Truth** für Versionshinweise im `.claude/`-Clockwork.

## Versionierung & Hinweis
- Einige frühere Zustände lassen sich nur **teilweise** rekonstruieren (Archive/ZIP-Historie, fehlende Git-Metadaten).
- Deshalb sind Einträge bis einschließlich **v17.7** aus den vorhandenen `FINALIZED_*.md` Release Notes konsolidiert.
- Ab jetzt: neue Änderungen nur noch hier eintragen (Release Notes liegen zusätzlich archiviert unter `.claude/changelog/release_notes/`).


## 17.7 (Hardening + AutoDocs + Legacy Purge)

- Added performance budgeting toggles: `performance_toggle` + `performance_finalize` (default enabled, auto-disable threshold).
- Added Critics Suite: legal/security/moral/creative/methodical with `critics_board_review` consolidation.

- Added `budget_analyze` + `efficiency_review` performance budgeting pack (`.claude-performance/` exports).
- Anchored product-code layout rule: all application/plugin code originates under `src/` (`policies/SRC_ORIGIN_RULE.md`).

- Added `limitation_harvest_scan` pre-step for DocForge (Expected-but-missing, non-goals, future work extraction).
- Added `hardening_scan_fix` (inconsistency detection + optional safe fixes) with a small decision brain store.
- Added `autodocs_generate` (per-skill docs scaffolding for all deterministic skills).
- Eliminated `.oodle/` path references (policy: removed, not deprecated).
- Added AddOn boundaries map (`addons/map.yaml`) and boundary rules.

## 17.7

This package contains **only** the `.claude/` clockwork directory (methodology + deterministic tooling).

## Compatibility promise
- The overall **Claude Code working rhythm** remains unchanged.
- v17.7 is a **documentation authoring upgrade** over v17.6.

## Add-ons (v17.7)

### Documentation authoring skills
- `doc_write`: deterministic doc persistence (single/multi-file) + unified diffs
- `tutorial_write`: spec-first tutorial renderer + section validation + diffs
- `doc_review`: deterministic doc lint review (TODOs, missing sections, broken local links, headings)
- `screencast_script`: spec-first screencast script writer (chapters + shot list) + diffs

### Baseline comparison
- `repo_compare`: deterministic folder diff (added/removed/changed by sha256)
  - writes a compare report under `.claude/knowledge/-Writes/compare_reports/`
  - intended for Claude Code ↔ Llama Code comparisons

### Docs team pack
New docs agents under `agents/docs/`:
- doc orchestration, writing, tutorial authoring, review, comparison
- plus optional specialists (security, architecture, API/CLI, glossary, release notes, diagrams, screencasts)

### Playbook
- `skills/playbooks/documentation_pipeline.md` documents the recommended end-to-end doc workflow.

### Analysis Suite skills
- `pattern_detect`, `mutation_detect`, `system_map`, `mechanic_explain`
- `code_assimilate`, `log_standardize`, `copyright_standardize`, `reference_fix`

### Meta skills (Autodiscovery & Forge)
- `skill_registry_search`: discover matching skills for an intent
- `skill_gap_detect`: detect capability gaps and propose a new skill
- `skill_scaffold`: scaffold a new skill (tool + schema + example + task + registry)

See playbooks:
- `skills/playbooks/analysis_suite_pipeline.md`
- `skills/playbooks/skill_forge_pipeline.md`

## 17.6

This package contains **only** the `.claude/` clockwork directory (methodology + deterministic tooling).

## Compatibility promise
- The overall **Claude Code working rhythm** remains unchanged.
- v17.6 is a **QA usability upgrade** over v17.5.

## Fixes (v17.6)

### QA gate is green out-of-the-box for `.claude-only`
- `doc_ssot_resolver`: `<PROJECT_ROOT>/...` references are now treated as **external** by default and **skipped**.
  - Exception: `<PROJECT_ROOT>/.claude/...` is always validated (internal to this distro).
- `qa_gate`: new inputs
  - `ssot_scope=claude_only|full` (default: `claude_only`)
  - `verify_project_root=true` (equivalent to `ssot_scope=full`)
  - `verify_legacy=true` (also validates `.claude/...` legacy refs)

### Path locator support
- `doc_ssot_resolver`: supports backtick refs with line locators, e.g.:
  - `<PROJECT_ROOT>/src/orchestrator.py:42`
  - `.claude/tools/skills/skill_runner.py#L120`

### Documentation updates
- `governance/path_semantics.md` and `governance/qa_gate_policy.md` document the new scope/flags.
- Minor version header bump to v17.6 across v17.5 policy docs.

## 17.5

This package contains **only** the `.claude/` clockwork directory (methodology + deterministic tooling).

## Compatibility promise
- The **Claude Code working rhythm** remains unchanged.
- v17.5 is a **bugfix & consistency upgrade** over v17.4.

## Fixes (v17.5)

### QA gate reliability
- `skill_runner.py`: now enforces running from repo root (where `.claude/` is visible) to prevent **false-green** checks.
- `drift_semantic_check`: now extracts skill IDs from the `SKILLS = {...}` dict via AST, preventing false positives.

### SSoT path resolver correctness
- `doc_ssot_resolver`: stricter path heuristics to avoid treating inline code (e.g. `main.py`, `error_code`) as file paths.
- Ignores globs/templates/placeholders in backticks and makes legacy `.claude/` references optional (`verify_legacy=true` to enforce).

### Contract validation safety
- `schema_batch_validate`: hard-fails if `contracts/schemas` or `contracts/examples` folders are missing.

### Hygiene
- `capability_map_build`: only lists real skills (modules exporting `run(req)`).
- Fixed duplicated `<PROJECT_ROOT>/<PROJECT_ROOT>/...` occurrences in docs.
- Fixed numbering duplication in `model_escalation_policy.md`.

## 17.4

This package contains **only** the `.claude/` clockwork directory (methodology + deterministic tooling).

## Compatibility promise
- The **Claude Code working rhythm** remains unchanged.
- v17.4 is an **additive upgrade**: new optional skills, tasks, governance policies.

## Additions (v17.4)
### New skills
- `qa_gate` — PR-blocking deterministic QA gate
- `doc_ssot_resolver` — validates backticked path semantics
- `drift_semantic_check` — registry↔runner + contracts + SSoT
- `team_topology_verify` — verifies the agent hierarchy structure
- `capability_map_build` — emits machine-readable capability snapshot
- `budget_router` — deterministic tier budgeting
- `evidence_bundle_build` — evidence manifest + zip
- `security_redactor` — redacts evidence for sharing
- `determinism_harness` — normalized digest for regression
- `refactor_bridge_scan` — legacy marker scanner for bridge refactors
- `release_cut` — one-button evidence release pack (no publishing)
- `schema_batch_validate` — validates all contract schemas vs examples (extended QA)

### New governance policies
- `governance/qa_gate_policy.md`
- `governance/evidence_bundle_policy.md`
- `governance/security_redaction_policy.md`
- `governance/budgeting_policy.md`
- `governance/capability_map_policy.md`

### New tasks
- `tasks/qa/000_RUN_QA_GATE.md`
- `tasks/qa/010_RUN_EXTENDED_QA.md`
- `tasks/evidence/010_BUILD_EVIDENCE_BUNDLE.md`
- `tasks/security/000_REDACT_EVIDENCE.md`
- `tasks/ops/110_ONE_BUTTON_RELEASE_CUT.md`
- `tasks/ops/120_BUILD_CAPABILITY_MAP.md`
- `tasks/ops/130_SEMANTIC_DRIFT_CHECK.md`
- `tasks/ops/140_REFACTOR_BRIDGE_SCAN.md`

## Notes
- Runtime/evidence/state must live outside `.claude/` (default: `validation_runs/`).
- This clockwork is intended for a private/unpublished branch and must not be merged into Llama Code main.

## 17.3

This package contains **only** the `.claude/` clockwork directory.

- v17.2 is treated as **finalized** for the Claude Code working rhythm.
- v17.3 is a **packaging release**: no project files, no runtime state, no extra folders.
- Intended usage: keep on a private/unpublished branch; do not merge into Llama Code main.

Runtime/evidence/state must live outside `.claude/` (e.g. `.claude/knowledge/-Writes/` in the main repo).

- Added token auto-logger hook: `token_event_log` + `.claude/tools/token_event_autologger.py`.

- Added unified agent step wrapper: `.claude/tools/run_agent_step.py` (runs command + logs one token event).

- Added local pricing snapshot for USD cost estimation in `budget_analyze`.

- Added .report/ canonical report folder + report publishing for performance and critics.
- Added Personaler model routing pack (scope assess + selection + outcome hit list).
- Improved agent step wrapper parsing for Claude Code summary lines (tool uses, k-tokens, duration).
