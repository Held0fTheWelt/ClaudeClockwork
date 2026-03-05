# Clockwork Rebaseline Audit — 2026-03-02

**Audit type:** Full rebaseline (post-MVP21 chain completion)
**Auditor:** Claude Code (Sonnet 4.6) — ClockworkUpdate mission
**Baseline source:** 10 Power Audit reports in `/mnt/d/OllamaCode/.report/` (Opus 4.6 independent run, 2026-03-02)
**Previous scan:** MVP08 parity scan (2026-03-02)
**Clockwork version:** 17.7.0 (per `.claude/VERSION`)

---

## 1. Re-index: Current State Map

### 1.1 Top-Level `.claude/` Directories

| Directory | Description | Notes |
|-----------|-------------|-------|
| `agents/` | Agent definitions | 10 subdirs, 76 .md files total |
| `addons/` | Addon skill packs | 8 addon packs + map.yaml |
| `brain/` | Routing stats (VIOLATION — see §4) | Contains mutable JSON |
| `changelog/` | Release notes | v17.3–v17.7 |
| `config/` | Configuration files | 5 files |
| `contracts/` | Skill I/O contracts | 94 schemas + 99 examples = 193 JSON files |
| `development/` | MVP chain tracking | MVP_STATUS.md |
| `docs/` | Internal docs | Varies |
| `eval/` | Evaluation harness | Golden fixtures + runner |
| `governance/` | Execution rules | 35 files |
| `humaninterface/` | User-facing docs | — |
| `knowledge/` | Knowledge base (PARTIAL VIOLATION — see §4) | Mutable files remain |
| `performance/` | Performance tracking | Log templates |
| `policies/` | Machine-readable policies | 6 files |
| `python/` | Python guidance | — |
| `skills/` | Skill definitions | 83 subdirs, 105 .md files |
| `tasks/` | Task definitions | ~70 tasks across 10 subdirs |
| `templates/` | Boilerplate | skill_forge template |
| `tools/` | Python implementations | 103 .py files total |

### 1.2 `agents/` — Detailed Breakdown

| Subdirectory | .md File Count | Contents |
|--------------|-------------:|----------|
| `agents/` (root) | 16 | team_lead, designer, personaler, context_packer, critic_dispatcher, librarian, tester, specialists, research, escalation_controller, qualitysignal_aggregator, skill_dispatcher, task_compactor, (+ README) |
| `agents/critics/` | 8 | technical, systemic, creative, legal, security, moral, methodical, README |
| `agents/analysis/` | 8 | Code/pattern/system analysis agents |
| `agents/docs/` | 14 | Documentation agents |
| `agents/learning/` | 13 | Per-agent learning logs (includes `critics/` sub-sub-dir) |
| `agents/meta/` | 3 | skill_forge, skill_navigator, skill_scout |
| `agents/operations/` | 6 | bulk_job_planner, department_lead_ops_ledger, skill_planning_agent, skill_scout, translator_local_oodle, work_brief_editor |
| `agents/quality/` | 2 | batch_schema_validator, local_verifier_o3 |
| `agents/testops/` | 4 | testops_orchestrator, testrunner_heavy, testrunner_light, testrunner_medium |
| `agents/workers/` | 2 | implementation_worker, report_worker |
| **Total** | **76** | Across 10 subdirectories |

### 1.3 `skills/` — Detailed Breakdown

| Metric | Count |
|--------|------:|
| Skill subdirectories (including `__init__`, `_event_logger`, etc.) | 84 |
| Skill `.md` definition files | 105 |
| Skills with `README.md` | 82 |
| Skills without README (stubs or non-standard) | 23 |

Skill subdirectory list (83 content dirs + root):
`__init__`, `_event_logger`, `_report_publish`, `autodocs_generate`, `budget_analyze`, `budget_router`, `capability_map_build`, `cleanup_apply`, `cleanup_plan_apply`, `code_assimilate`, `code_clean`, `code_clean_scan`, `contract_drift_sentinel`, `copyright_standardize`, `creativity_burst`, `critics_board_review`, `decision_feedback`, `deliberation_pack_build`, `determinism_harness`, `determinism_proof`, `doc_review`, `doc_ssot_resolver`, `doc_write`, `drift_semantic_check`, `economics_regression`, `edge_case_selector`, `efficiency_review`, `evidence_bundle_build`, `evidence_init`, `evidence_router`, `exec_dryrun`, `hardening_scan_fix`, `hypothesis_builder`, `idea_dedupe`, `idea_scoring`, `last_train`, `last_train_merge`, `limitation_harvest_scan`, `log_standardize`, `mechanic_explain`, `model_routing_record_outcome`, `model_routing_select`, `mutation_detect`, `outcome_event_generate`, `outcome_ledger_append`, `pattern_detect`, `pdf_quality`, `pdf_render`, `performance_finalize`, `performance_toggle`, `plan_diff_apply`, `plan_lint`, `plan_mutate`, `playbooks`, `policy_gatekeeper`, `prompt_debt_capture`, `qa_gate`, `refactor_bridge_scan`, `reference_fix`, `release_cut`, `repo_clean`, `repo_clean_scan`, `repo_compare`, `repo_validate`, `route_autotune_suggest`, `route_profile_patch_pack`, `route_profile_update`, `schema_batch_validate`, `screencast_script`, `security_redactor`, `shadow_prompt`, `shadow_prompt_minify`, `skill_gap_detect`, `skill_registry_search`, `skill_scaffold`, `spec_validate`, `system_map`, `team_topology_verify`, `token_event_log`, `triad_build`, `triad_ref_lint`, `tutorial_write`, `work_scope_assess`

### 1.4 `tools/skills/` — Python Skill Implementations

| Metric | Count |
|--------|------:|
| Total `.py` files in `tools/skills/` | 95 |
| Root `tools/` `.py` files (non-skills) | 6 (`boot_check.py`, `ollama_brief.py`, `run_agent_step.py`, `telemetry_writer.py`, `test_ollama.py`, `token_event_autologger.py`) |
| **Total `.py` in `tools/`** | **103** |

Notable `.py` files in `tools/skills/` (added in MVP09–MVP21):
`bandit_router_select.py`, `clockwork_version_bump.py`, `create_mvp.py`, `escalation_router.py`, `eval_run.py`, `last_train.py`, `pdf_export.py`, `pdf_quality.py`, `parity_scan_and_mvp_planner.py`, `review_panel.py`, `shadow_prompt.py`, `telemetry_summarize.py`

### 1.5 `contracts/` — Schema & Example Counts

| Subdirectory | File Count | Notes |
|--------------|----------:|-------|
| `contracts/schemas/` | 94 JSON Schema files | JSON Schema Draft 2020-12 |
| `contracts/examples/` | 99 example JSON files | Runnable contract instances |
| **Total** | **193** | |

### 1.6 `governance/` — File List (35 files)

`LEGACY_POLICY.md`, `artifacts_and_paths.md`, `budgeting_policy.md`, `capability_map_policy.md`, `decision_policy.md`, `deep_oodle_mode.md`, `derived_copy_header_template.md`, `document_placement.md`, `escalation_matrix.md`, `evidence_bundle_policy.md`, `execution_protocol.md`, `experiment_budget.md`, `feedback_policy.md`, `file_ownership.md`, `git_workflow.md`, `legacy_purge_report.md`, `message_triad_protocol.md`, `model_escalation_policy.md`, `naming_canon.md`, `no_llm_mode.md`, `ollama_integration.md`, `path_semantics.md`, `paths_and_placeholders.md`, `planning_policy.md`, `policy_gatekeeper.md`, `prompt_debt_policy.md`, `qa_gate_policy.md`, `review_process.md`, `routing_matrix.md`, `rule_discovery.md`, `security_redaction_policy.md`, `self_improvement.md`, `skill_scout_triggers.md`, `task_archival.md`, `workflow_triggers.md`

### 1.7 `policies/` — File List (6 files)

`POLICY_INDEX.md`, `SRC_ORIGIN_RULE.md`, `VIOLATION_REPORT_TEMPLATE.md`, `audit_log_template.md`, `hardlines.yaml`, `skill_autodiscovery_and_forge.md`

### 1.8 `addons/` — Addon Packs from `map.yaml`

| Pack Name | Skills Declared |
|-----------|----------------|
| `docforge_pdf_quality` | `pdf_render` |
| `cleaning_suite` | `repo_clean_scan`, `code_clean_scan`, `cleanup_plan_apply` |
| `last_train_suite` | `last_train_merge` |
| `shadow_prompts` | `shadow_prompt_minify` |
| `meta_doc_ops` | `autodocs_generate`, `hardening_scan_fix`, `limitation_harvest_scan` |
| `performance_budgeting` | `budget_analyze`, `efficiency_review`, `performance_finalize`, `performance_toggle`, `token_event_log` |
| `critics_suite` | `critics_board_review` |
| `model_routing_personaler` | `model_routing_record_outcome`, `model_routing_select`, `work_scope_assess` |

Source: `.claude/addons/map.yaml`

### 1.9 `config/` — File List (5 files)

`anthropic_pricing_snapshot.json`, `model_escalation_ladder.yaml` (added MVP09), `model_routing.yaml`, `pdf_quality_ollama_profiles.yaml`, `performance_budgeting.yaml`

### 1.10 `eval/` — Structure

```
.claude/eval/
├── README.md                         # Harness guide
├── eval_runner.py                    # Standalone eval runner (stdlib only)
├── __pycache__/                      # VIOLATION: compiled cache in clockwork
│   └── eval_runner.cpython-310.pyc
├── golden/                           # Golden fixtures
│   ├── hello_golden.json
│   ├── qa_gate_golden.json
│   └── scan_golden.json
├── results/                          # Eval run results
│   ├── .gitkeep
│   ├── run_20260302_083150.json
│   ├── run_20260302_083216.json
│   ├── run_20260302_083220.json
│   └── run_20260302_083224.json
└── trend_report.md                   # Manual trend table template
```

Note: `task_suite.yaml` and `schedules.yaml` (designed in Report 06) do not yet exist. `shadow/` and `ab/` subdirs do not yet exist.

### 1.11 `knowledge/` — Files (post-MVP17)

| File | Status | Correct Location |
|------|--------|-----------------|
| `architecture.md` | Static reference doc — OK | Remains in `.claude/knowledge/` |
| `decisions.md` | Static reference doc — OK | Remains in `.claude/knowledge/` |
| `index.md` | Static reference doc — OK | Remains in `.claude/knowledge/` |
| `localAIs.md` | Static reference doc — OK | Remains in `.claude/knowledge/` |
| `research_archive_template.md` | Template — OK | Remains in `.claude/knowledge/` |
| `routing.md` | Static reference doc — OK | Remains in `.claude/knowledge/` |
| `outcome_ledger.jsonl` | **VIOLATION** — mutable runtime ledger | Should be `.llama_runtime/knowledge/outcome_ledger.jsonl` (moved in MVP17 but original copy remains) |
| `route_profiles.json` | **VIOLATION** — mutable routing data | Should be `.llama_runtime/knowledge/route_profiles.json` (moved in MVP17 but original copy remains) |
| `-Writes/` (directory) | **VIOLATION** — generated artifacts | Should be `.llama_runtime/writes/` (moved in MVP17 but original directory remains) |

---

## 2. Changes Since Last Audit (MVP08 Parity Scan)

The following were added by MVP09 through MVP21 (all 2026-03-02):

| MVP | Key Deliverables Added |
|-----|----------------------|
| MVP09 | `.claude/config/model_escalation_ladder.yaml`, `llamacode/core/escalation_router.py`, `.claude/skills/escalation_router.md` |
| MVP10 | `.claude/tools/skills/qa_gate.py` (8 checks), `.github/workflows/gate.yml`, contract schemas/examples for qa_gate |
| MVP11 | `.claude/eval/eval_runner.py`, `.claude/eval/golden/` (3 fixtures), `.claude/tools/skills/eval_run.py`, contract schema/example for eval_run |
| MVP12 | `telemetry_event.schema.json`, `telemetry_summarize.py`, `review_panel.py`, 4 new contract schemas/examples; registry entries #84–#85 |
| MVP13 | `cleanup_apply.py`, `repo_clean.py`, `code_clean.py`; 3 new contract examples; registry entries #81–#83 |
| MVP14 | `last_train.py`, `shadow_prompt.py`; `shadow_prompt_triage.schema.json`; registry entries #86–#87 |
| MVP15 | `pdf_quality.py`; `pdf_quality_request.schema.json`, `pdf_export_request.schema.json`; registry entries #88–#89 |
| MVP16 | `parity_scan_and_mvp_planner.py`, `idea_dedupe.py`; `idea_dedupe_spec.schema.json`; 22 skills wired in `skill_runner.py`; registry entries #90–#91 |
| MVP17 | Runtime files moved: `outcome_ledger.jsonl`, `route_profiles.json`, `brain/model_routing_stats.json` → `.llama_runtime/`; `tests/test_integration_pipeline.py`; `.gitignore` updated |
| MVP18 | `llamacode/core/bandit_router.py`, `bandit_router_select.py`; `bandit_routing_decision.schema.json`; `validate_input` opt-in in `skill_runner.py` |
| MVP19 | `qa_gate.py` extended (12 checks total, 4 new); `scripts/tag_stub_skills.py`; `scripts/validate_addons.py`; `gate.yml` updated with addon validation step |
| MVP20 | `create_mvp.py`; `create_mvp.schema.json`; `create_mvp_example.json`; registry entry #77 |
| MVP21 | `clockwork_version_bump.py`; `.claude/VERSION` (17.7.0); `clockwork_version_bump.schema.json`; registry entries #78–#79 |

**Net additions (MVP09–MVP21):**
- ~18 new Python skill implementations
- ~15 new contract schemas
- ~12 new contract examples
- CI pipeline (GitHub Actions) established
- Integration test added
- Eval harness scaffolded with 3 golden fixtures
- Bandit adaptive router implemented in `llamacode/`
- Version control system for clockwork itself

---

## 3. Drift & Pointer Check

| File | Points To | Target Exists | Fix |
|------|-----------|:-------------:|-----|
| `.claude/ARCHITECTURE.md` | `<PROJECT_ROOT>/ARCHITECTURE.md` | **NO** | Create `/mnt/d/OllamaCode/ARCHITECTURE.md` — the pointer says "create it if missing". Acceptance: file exists at repo root with architecture overview referencing `llamacode/` as primary package. |
| `.claude/ROADMAP.md` | `<PROJECT_ROOT>/ROADMAP.md` | **NO** | Create `/mnt/d/OllamaCode/ROADMAP.md` — pointer says "create it if missing". Acceptance: file exists at repo root with current roadmap from Report 09. |
| `.claude/MODEL_POLICY.md` | `<PROJECT_ROOT>/MODEL_POLICY.md` | **NO** | Create `/mnt/d/OllamaCode/MODEL_POLICY.md` — pointer says "create it if missing". Acceptance: file covers token budget policy, performance_budgeting.yaml reference, src/ origin rule. |
| `.claude/INDEX.md` (link: `knowledge/-Writes/`) | `.claude/knowledge/-Writes/` | **YES** (but violation) | Update INDEX.md to point to `.llama_runtime/writes/` instead — the write root moved in MVP17 but INDEX.md was not updated. Acceptance: INDEX.md line "Generated artifacts / diffs → `.claude/knowledge/-Writes/`" corrected to `.llama_runtime/writes/`. |
| `.claude/INDEX.md` (link: `boot_check.py`) | `.claude/tools/boot_check.py` | **YES** | No fix needed. |
| `.claude/INDEX.md` (link: `skills/registry.md`) | `.claude/skills/registry.md` | **YES** | No fix needed. |
| `.claude/INDEX.md` (link: `CHANGELOG.md`) | `.claude/CHANGELOG.md` | **YES** | No fix needed. |
| `.claude/INDEX.md` (VERSION note: "6.5.0-MVP9") | Stale — actual clockwork version is 17.7.0 | **STALE** | Update INDEX.md VERSION reference to 17.7.0. Acceptance: INDEX.md reflects current clockwork version. |

### Pointer Fix Summary

| Fix Type | Count | Actions |
|----------|------:|--------|
| Create missing target | 3 | `ARCHITECTURE.md`, `ROADMAP.md`, `MODEL_POLICY.md` at repo root |
| Update stale internal link | 2 | `INDEX.md` `-Writes/` path + VERSION string |

---

## 4. Remaining `.claude/` Invariant Violations

Per CLAUDE.md: "Never write runtime state, caches, reports, ledgers, snapshots, or generated artifacts into `.claude/`."

MVP17 was supposed to resolve P0-001, P0-002, P0-003, and P1-006 by moving files to `.llama_runtime/`. However, the **originals were not deleted** after the move. Additionally, new violations appeared.

| Violation ID | File/Dir | Violation Type | Evidence | Resolution |
|-------------|---------|---------------|----------|------------|
| V-001 | `.claude/knowledge/outcome_ledger.jsonl` | Mutable runtime ledger in clockwork | File present; canonical copy moved to `.llama_runtime/knowledge/outcome_ledger.jsonl` in MVP17 but original not deleted | Delete `.claude/knowledge/outcome_ledger.jsonl`; update any paths still pointing to old location |
| V-002 | `.claude/knowledge/route_profiles.json` | Mutable routing data in clockwork | File present; canonical copy moved to `.llama_runtime/knowledge/route_profiles.json` in MVP17 but original not deleted | Delete `.claude/knowledge/route_profiles.json`; update any paths still pointing to old location |
| V-003 | `.claude/knowledge/-Writes/` (directory + 7 generated files) | Generated artifact cache in clockwork | `autodocs_report_*.json` files (6 files) + `depth_analysis_reorg_*.md` — all timestamped generated outputs; canonical write root moved to `.llama_runtime/writes/` in MVP17 | Delete or move entire `-Writes/` subtree to `.llama_runtime/writes/`; remove directory from `.claude/knowledge/` |
| V-004 | `.claude/brain/model_routing_stats.json` | Mutable routing stats in clockwork | File present; canonical copy moved to `.llama_runtime/brain/` in MVP17 but original not deleted | Delete `.claude/brain/model_routing_stats.json`; directory `.claude/brain/` should be empty or removed |
| V-005 | `.claude/eval/__pycache__/eval_runner.cpython-310.pyc` | Compiled Python bytecode cache in clockwork | `__pycache__/` directory present in `.claude/eval/` | Add `.claude/eval/__pycache__/` to `.gitignore`; delete the `__pycache__/` directory |
| V-006 | `.claude/eval/results/run_20260302_0831*.json` (4 files) | Eval run results (runtime state) in clockwork | Timestamped result files in `.claude/eval/results/` — these are generated runtime artifacts | Move results to `.llama_runtime/eval/results/` or `.report/`; update `eval_runner.py` default output path |

**Total active violations:** 6 (4 are stale originals from MVP17 incomplete cleanup; 2 are new post-MVP17)

---

## 5. Audit Log Entry

```
---
Audit ID:        rebaseline_2026-03-02
Type:            Full Rebaseline (post-MVP21 chain)
Date:            2026-03-02
Auditor:         Claude Code (Sonnet 4.6) — ClockworkUpdate mission
Clockwork ver.:  17.7.0
Previous scan:   MVP08 parity scan (2026-03-02)
Scope:           .claude/ full re-index + drift check + invariant violations
Method:          File scanning (Glob, Bash, Read tools) — no LLM inference

Summary:
  - Agents:      76 .md files across 10 subdirs (16 root-level + 60 in subdirs)
  - Skills:      105 .md definitions across 83 skill dirs (82 with README)
  - Tools/py:    103 .py files (95 skills/ + 6 root tools/ + 2 other)
  - Contracts:   94 schemas + 99 examples = 193 JSON files
  - Governance:  35 files
  - Policies:    6 files
  - Addons:      8 packs (map.yaml)
  - Config:      5 files
  - Eval:        1 runner + 3 golden fixtures + 4 result runs

Drift findings:
  - 3 pointer targets missing at project root (ARCHITECTURE.md, ROADMAP.md, MODEL_POLICY.md)
  - INDEX.md has stale -Writes/ path and stale VERSION string

Invariant violations:
  - 6 active violations (V-001 through V-006)
  - 4 are incomplete cleanup from MVP17 (original files not deleted after move)
  - 2 are new: __pycache__ in eval/ and eval results in clockwork

Next audit due: Weekly power test (next Sunday); or pre-release if version bump planned
---
```
