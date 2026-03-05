# MVP Status Tracker

_Last updated: 2026-03-02_

| MVP | Name | Status |
|---|---|---|
| MVP01 | Repo & Runtime Scaffolding (Clockwork Core) | done |
| MVP02 | Deterministic Skill Framework v1 | done |
| MVP03 | Agent Layer v1 | done |
| MVP04 | Documentation Ops v1 | done |
| MVP05 | Governance & Policy Enforcement v1 | done |
| MVP06 | Reports & Telemetry Layout v1 | done |
| MVP07 | Milestone System v1 (.claude-development/ scaffolding) | done |
| MVP08 | Parity Scan Skill + MVP Pre-Planning (Clockwork-only) | done |
| MVP09 | Escalation Router (cheapest-first model ladder) | done |
| MVP10 | QA Gates & CI v1 | done |
| MVP11 | Eval Harness / Golden Tests v1 | done |
| MVP12 | Telemetry & Feedback Loop v1 | done |
| MVP13 | Cleaning Suite Completion | done |
| MVP14 | Archive & Prompt Evolution Completion | done |
| MVP15 | PDF Quality Skill (DocForge PDF Pipeline) | done |
| MVP16 | Parity Scan Planner Implementation + Registry Integrity | done |
| MVP17 | Clockwork Invariants + CI Gate + Integration Tests | done |
| MVP18 | Adaptive Routing & Telemetry Feedback Loop | done |
| MVP19 | Meta-Tooling: QA Gate Extension + Addon CI + skill_runner Hygiene | done |
| MVP20 | "Create MVP" Skill (Autonomous MVP Generation) | done |
| MVP21 | Clockwork Versioning (Version Bumps + Changelog + Release Tags) | done |

## MVP01 — Delivered (2026-03-02)

- `.claude/tools/boot_check.py` — validates required Clockwork paths and VERSION; exit 0 on all pass
- `.claude/INDEX.md` — "Start Here" and "Boot Check" sections added at top
- `.claude/development/MVP_STATUS.md` — this file

## MVP05 — Delivered (2026-03-02)

- `.claude/policies/POLICY_INDEX.md` — index of 15 active policies with testability status and how-to-test instructions
- `.claude/policies/hardlines.yaml` — machine-readable safety hardlines: destructive action guards, allowed/denied write roots, external provider opt-in rules, commit guards, and dry-run defaults
- `.claude/policies/audit_log_template.md` — template for decision log entries with 2 filled examples (L0 autonomous and L4 escalation)
- `.claude/policies/VIOLATION_REPORT_TEMPLATE.md` — template for policy violation reports (P0/P1/P2 severity) with 1 filled example and filing instructions

## MVP06 — Delivered (2026-03-02)

- `.report/README.md` — updated with full structure docs, naming convention, and `.report/` vs `.claude-performance/` guidance
- `.report/audit/.gitkeep` — audit subdirectory scaffold
- `.report/critics/.gitkeep` — critics subdirectory scaffold
- `.report/qa/.gitkeep` — QA gate results subdirectory scaffold
- `.claude-performance/README.md` — updated with full structure, naming, event format, and writer references
- `.claude-performance/charts/.gitkeep` — charts subdirectory scaffold
- `.claude/tools/telemetry_writer.py` — stdlib-only JSONL event writer; `write_event()` API + CLI entrypoint

## MVP08 — Delivered (2026-03-02)

- `.claude-development/audits/parity/parity_matrix_2026-03-02.md` — 35-row capability parity matrix (16 FULL / 7 PARTIAL / 12 GAP)
- `.claude-development/audits/parity/missing_features_backlog_2026-03-02.md` — 22-item prioritized backlog (4 P0 / 10 P1 / 8 P2)
- `.claude-development/milestones/M1_parity_followup_plan_2026-03-02.md` — dependency-aware M1 milestone plan
- `.claude-development/audits/audit_cadence.md` — full cadence spec (replaced MVP07 placeholder)
- `.claude/skills/parity_scan_and_mvp_planner.md` — skill definition with checklist and templates
- `.claude/contracts/schemas/parity_scan_and_mvp_planner.schema.json` — JSON Schema for skill I/O
- `.claude/contracts/examples/parity_scan_and_mvp_planner_example.json` — runnable example

## MVP07 — Delivered (2026-03-02)

- `.claude-development/milestones/index.md` — canonical milestone index
- `.claude-development/audits/logs/audit_log_2026-03-02.md` — first audit log entry (CCW-MVP01–MVP07 bootstrap)
- `.claude-development/audits/parity/.gitkeep` — placeholder for MVP08 parity outputs
- `.claude-development/audits/audit_cadence.md` — audit cadence (full spec in MVP08)

## MVP09 — Delivered (2026-03-02)

- `.claude/config/model_escalation_ladder.yaml` — haiku (3-rung) and sonnet (4-rung) escalation ladders with trigger config and 24 h state reset
- `llamacode/core/escalation_router.py` — `EscalationRouter` class; detects overload/timeout/empty-response triggers, persists winning rung to `.llama_runtime/router_state.json`
- `llamacode/core/escalation_router_demo.py` — demo script; supports `--dry-run` (no API calls) and live mode
- `.claude/skills/escalation_router.md` — skill definition with I/O spec, usage example, and triggers table
- `.claude/config/model_routing.yaml` — converted to valid YAML; added companion pointer to `model_escalation_ladder.yaml`

## MVP10 — Delivered (2026-03-02)

- `.claude/tools/skills/qa_gate.py` — rewritten skill with 8 deterministic checks (BOOT_001, LAYOUT_001, SCHEMA_001, SKILL_001, POLICY_001, REPORT_001, POINTER_001, VERSION_001); stdlib only; `run(req)` API + CLI entrypoint; exit code 0 = gate pass
- `.claude/contracts/schemas/qa_gate_request.schema.json` — JSON Schema for qa_gate skill inputs (`project_root`, `checks`, `output_dir`, `write_report`)
- `.claude/contracts/examples/qa_gate_example.json` — minimal runnable example
- `.github/workflows/gate.yml` — updated to trigger on push to master/main/claude and PRs to master/main; added "Run Clockwork skill QA gate" step

## MVP20 — Delivered (2026-03-02)

- `.claude/tools/skills/create_mvp.py` — autonomous MVP entry generator; reads chain, finds next ID, appends entry, logs to audit
- `.claude/contracts/schemas/create_mvp.schema.json` — input schema
- `.claude/contracts/examples/create_mvp_example.json` — dry_run example
- `.claude/skills/registry.md` — entry #77

## MVP21 — Delivered (2026-03-02)

- `.claude/tools/skills/clockwork_version_bump.py` — semver bump + changelog + optional git tag
- `.claude/VERSION` — current version: 17.7.0
- `.claude/contracts/schemas/clockwork_version_bump.schema.json` — schema
- `.claude/contracts/examples/clockwork_version_bump_example.json` — dry_run example
- `.claude/skills/registry.md` — entries #78, #79

## MVP11 — Delivered (2026-03-02)

- `.claude/eval/golden/hello_golden.json` — golden fixture: basic hello skill smoke test
- `.claude/eval/golden/scan_golden.json` — golden fixture: scan skill status check
- `.claude/eval/golden/qa_gate_golden.json` — golden fixture: QA gate smoke test
- `.claude/eval/eval_runner.py` — standalone eval runner (stdlib only); loads fixtures, runs skills, saves timestamped results, detects regressions; exit 0 = all pass
- `.claude/eval/results/.gitkeep` — results directory scaffold
- `.claude/eval/trend_report.md` — manual trend table template
- `.claude/eval/README.md` — harness guide (purpose, structure, add-test instructions, regression definition)
- `.claude/tools/skills/eval_run.py` — Clockwork skill wrapper for eval_runner; `run(req)` API + standalone entrypoint
- `.claude/contracts/schemas/eval_run.schema.json` — JSON Schema for eval_run inputs and outputs
- `.claude/contracts/examples/eval_run_example.json` — runnable example

## MVP12 — Delivered (2026-03-02)

- `.claude/contracts/schemas/telemetry_event.schema.json` — standard event schema (JSON Schema Draft 2020-12); required fields: ts, run_id, role, model, task; optional: phase, prompt_tokens, completion_tokens, total_tokens, estimated_cost_cents, quality_score, duration_ms, escalation_level, notes
- `.claude/contracts/examples/telemetry_event_example.json` — runnable example event (mvp12-test-001, team_lead, claude-sonnet-4-6, code_review)
- `.claude/tools/skills/telemetry_summarize.py` — stdlib-only skill; globs *.jsonl from events_dir, groups by configurable fields (default: role+model), computes total_tokens/avg_tokens/run_count/total_cost_cents/avg_quality_score per group, returns top_n by total_tokens; handles empty dir gracefully
- `.claude/contracts/schemas/telemetry_summary.schema.json` — output schema for telemetry_summarize
- `.claude/contracts/examples/telemetry_summarize_example.json` — skill request example
- `.claude/tools/skills/review_panel.py` — stdlib-only skill; consolidates worker/team_lead/judge verdicts using majority, unanimous, or weighted strategies; tracks dissenting reviewers and aggregates recommendations from warn/fail notes
- `.claude/contracts/schemas/review_panel_request.schema.json` — input schema for review_panel
- `.claude/contracts/schemas/review_panel_result.schema.json` — output schema for review_panel
- `.claude/contracts/examples/review_panel_example.json` — skill request example (3-reviewer majority vote)
- `.claude/contracts/examples/telemetry_summarize.skill_request.example.json` — canonical skill_request_spec example (type+request_id+inputs; group_by role+model, top_n 10)
- `.claude/contracts/examples/review_panel.skill_request.example.json` — canonical skill_request_spec example (type+request_id+inputs; 3-reviewer majority consolidation)
- `.claude/skills/registry.md` — entries #84 (telemetry_summarize) and #85 (review_panel) appended

## MVP13 — Delivered (2026-03-02)

- `.claude/tools/skills/cleanup_apply.py` — applies a JSON cleanup plan to the filesystem; dry_run=True and allow_delete=False by default; supports move/delete/archive/rename actions; refuses paths outside root; writes optional report
- `.claude/tools/skills/repo_clean.py` — scans repo for clutter: cache dirs, temp/system files, empty dirs, duplicate filenames; scan_only=True by default; never modifies filesystem
- `.claude/tools/skills/code_clean.py` — scans Python files for TODO/FIXME/HACK markers, unused imports (heuristic), long functions (>100 lines), and stub files; scan_only=True by default; emit_plan=True adds remediation suggestions
- `.claude/contracts/examples/cleanup_apply_example.json` — minimal runnable example (plan_path, dry_run=true, allow_delete=false)
- `.claude/contracts/examples/repo_clean_example.json` — minimal runnable example (root=".", scan_only=true)
- `.claude/contracts/examples/code_clean_example.json` — minimal runnable example (root="llamacode", scan_only=true, emit_plan=false)
- `.claude/skills/registry.md` — entries #81 (cleanup_apply), #82 (repo_clean), #83 (code_clean)

## MVP14 — Delivered (2026-03-02)

- `.claude/tools/skills/last_train.py` — summarizer/viewer for `last_train_report.json` produced by `last_train_merge`; builds timeline of `{step, verdict, notes}`; counts evolution/loss/mixed verdicts; supports JSON and Markdown output formats; optionally writes summary to `summary_dir`; stdlib only (json, pathlib, sys, datetime, statistics)
- `.claude/tools/skills/shadow_prompt.py` — triage skill for `shadow_prompt_report.json` produced by `shadow_prompt_minify`; classifies sections as accept/flag/reject using configurable `min_quality_score`; builds ranked_fixes sorted ascending by score; `quality_gate_pass = (rejected_sections == 0)`; optionally writes Markdown triage file; stdlib only
- `.claude/contracts/examples/last_train_example.json` — minimal runnable example (nonexistent report_path tests error path)
- `.claude/contracts/examples/shadow_prompt_example.json` — minimal runnable example (nonexistent report_path tests error path)
- `.claude/contracts/schemas/shadow_prompt_triage.schema.json` — output schema for shadow_prompt skill (accept_sections, flagged_sections, rejected_sections, ranked_fixes, quality_gate_pass)
- `.claude/skills/registry.md` — entries #86 (last_train), #87 (shadow_prompt) appended under MVP14 section

## MVP15 — Delivered (2026-03-02)

- `.claude/tools/skills/pdf_quality.py` — deterministic quality rubric scorer for Markdown manuscripts; no LLM calls; scores 5 dimensions: coverage (30%), structure (20%), clarity (20%), correctness (20%), diagrams (10%); gate passes at overall >= 70; builds fix_list sorted worst dimension first; stdlib only (json, re, sys, pathlib, statistics)
- `.claude/contracts/schemas/pdf_quality_request.schema.json` — JSON Schema for pdf_quality skill inputs (manuscript_path, scope, target_audience, max_fixes, write_report, report_dir)
- `.claude/contracts/examples/pdf_quality_example.json` — runnable example (docs/README.md, scope=general, write_report=false)
- `.claude/contracts/schemas/pdf_export_request.schema.json` — JSON Schema for pdf_export skill inputs (ghost-skill registration; covers project_root, doc_files, output_dir, naming_scheme, fallback_fmt, mermaid, dry_run)
- `.claude/contracts/examples/pdf_export_example.json` — runnable example (dry_run=true, docs/README.md)
- `.claude/skills/registry.md` — entries #88 (pdf_quality), #89 (pdf_export) appended under MVP15 section

## MVP16 — Delivered (2026-03-02)

- `.claude/tools/skills/parity_scan_and_mvp_planner.py` — deterministic file-evidence parity scanner; reads MVP chain, classifies each section as FULL/PARTIAL/GAP; writes parity matrix + missing features backlog; optionally writes M2 pre-plan; no LLM calls (stdlib only)
- `.claude/tools/skills/idea_dedupe.py` — updated with full `run(req)` skill interface and standalone entrypoint; deterministic deduplication via exact/normalized/levenshtein methods
- `.claude/contracts/schemas/idea_dedupe_spec.schema.json` — JSON Schema for idea_dedupe skill inputs/outputs
- `.claude/contracts/examples/idea_dedupe.skill_request.example.json` — canonical skill_request_spec example (normalized method, 7 input ideas)
- `.claude/skills/registry.md` — entries #90 (parity_scan_and_mvp_planner) and #91 (idea_dedupe) appended under MVP16 section
- `.claude/tools/skills/skill_runner.py` — 22 previously-missing skills wired in: hello, scan, report, escalation_router, eval_run, create_mvp, clockwork_version_bump, telemetry_summarize, review_panel, cleanup_apply, repo_clean, code_clean, last_train, shadow_prompt, pdf_quality, parity_scan_and_mvp_planner, idea_dedupe (and 5 additional from earlier MVPs)

## MVP18 — Delivered (2026-03-02)

- `llamacode/core/bandit_router.py` — `BanditRouter` class; epsilon-greedy bandit that reads `.llama_runtime/knowledge/outcome_ledger.jsonl`; falls back to static YAML or hardcoded defaults when ledger is too small (<10 entries globally); `select(task_type, quality_threshold, cost_cap)` returns `{model_id, rung, confidence, source}`; stdlib only (json, pathlib, random, statistics, sys)
- `.claude/contracts/schemas/bandit_routing_decision.schema.json` — JSON Schema for BanditRouter inputs (task_type, quality_threshold, cost_cap, epsilon, ladder_name) and outputs (model_id, rung, confidence, source enum: bandit|static|fallback)
- `.claude/contracts/examples/bandit_routing_decision.example.json` — example showing a bandit routing decision for task_type='code_review' with source='bandit' and confidence=0.87
- `.claude/tools/skills/bandit_router_select.py` — Clockwork skill wrapper; `run(req)` interface; calls `BanditRouter(ladder_name, epsilon).select(task_type, quality_threshold, cost_cap)`; returns skill_result_spec
- `.claude/tools/skills/skill_runner.py` — `bandit_router_select` wired into SKILLS dict; `validate_input` opt-in feature added to `main()` (non-breaking: defaults to absent/False)

## MVP19 — Delivered (2026-03-02)

- `.claude/tools/skills/qa_gate.py` — 4 new checks added: POINTER_002 (pointer-file target validation), COVERAGE_001 (skill dispatch coverage), ADDON_001 (addon pack completeness), AGENT_001 (agent registry consistency); CHECKS list now has 12 entries
- `scripts/tag_stub_skills.py` — idempotent script; reads SKILLS dict from skill_runner.py; prepends `status: stub` to READMEs in `.claude/skills/` subdirs that have no `.py` in `.claude/tools/skills/`; supports `--dry-run`
- `scripts/validate_addons.py` — reads `.claude/addons/map.yaml`; validates each addon pack skill has a `.py` in `.claude/tools/skills/`; prints per-skill pass/fail; exits non-zero on missing implementations; supports `--dry-run`
- `.github/workflows/gate.yml` — new "Validate addon packs" step added after QA gate step
- `skill_runner.py` hygiene audit — no orphan non-skill dict keys in SKILLS block; all MVP16 required skills confirmed present (`hello`, `scan`, `report`, `escalation_router`, `idea_dedupe`, `eval_run`, `create_mvp`, `clockwork_version_bump`)

## MVP17 — Delivered (2026-03-02)

- `.llama_runtime/knowledge/outcome_ledger.jsonl` — mutable ledger moved from `.claude/knowledge/` (P0-001 fix)
- `.llama_runtime/knowledge/route_profiles.json` — mutable routing data moved from `.claude/knowledge/` (P0-003 fix)
- `.llama_runtime/brain/model_routing_stats.json` — mutable routing stats moved from `.claude/brain/` (P1-006 fix)
- `.llama_runtime/writes/` — artifact write root moved from `.claude/knowledge/-Writes/` (P0-001 fix)
- `.claude/tools/skills/outcome_ledger_append.py` — updated default path to `.llama_runtime/knowledge/outcome_ledger.jsonl`
- `.claude/tools/skills/route_autotune_suggest.py` — updated default ledger path to `.llama_runtime/knowledge/outcome_ledger.jsonl`
- `.claude/tools/skills/route_profile_update.py` — updated default path to `.llama_runtime/knowledge/route_profiles.json`
- `.gitignore` — `.llama_runtime/` added to prevent committing mutable runtime state
- `tests/test_integration_pipeline.py` — integration test covering SkillRequestSpec → skill dispatch → SkillResultSpec for `repo_validate`, `plan_lint`, `qa_gate`
