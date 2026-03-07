# Skills Registry

Skills are deterministic (tool-first) micro-workflows. They exist to reduce token usage:
- Agents **request** a skill via `SkillRequestSpec`
- Tools **execute** and return `SkillResultSpec`
- LLMs are used only for *coordination / relay / interpretation* when needed.

## Available skills (v0)

### 1) repo_validate
Checks repository consistency:
- broken markdown links (local)
- invalid JSON files
- optional secret scan (basic patterns)

### 2) evidence_init
Creates a standard evidence folder:
`validation_runs/YYYY-MM-DD/{logs,artifacts,reports,specs}`

### 3) spec_validate
Validates JSON specs/examples against JSON schemas (Draft 2020-12).

### 4) determinism_proof
Hashes declared deterministic targets twice and reports mismatches.

### 5) economics_regression
Checks routing spend rules (Oodle-first, Claude tier caps) against evidence (RoutingSpec, OpsLedgerSummary, QualitySignal) when present.

## Where the code lives
- `tools/skills/skill_runner.py` (entrypoint)
- `tools/skills/*.py` (skill implementations)

## Minimal usage rule
Prefer running a skill over creating an agent discussion, especially for:
validation, scanning, hashing, and evidence collection.

## Meta roles
- Skill Scout: observes runs and proposes new deterministic skills (max 3 at a time).

### 6) plan_lint
Checks a PlanSpec against max_plan_tasks (8–12) and basic required fields.

### 7) creativity_burst
Clusters and narrows a list of one-line ideas (tool-side). Pair with cheap LLM idea generation.

### 8) plan_mutate
Applies deterministic plan mutation presets (cost_first, reliability_first, speed_first).

### 9) hypothesis_builder
Builds a HypothesisSpec deterministically from short inputs.

### 10) prompt_debt_capture
Writes PromptDebtItem list to a file (max 5 per run).

### 11) route_profile_update
Updates a local route profiles knowledge file (best routes).

### 12) edge_case_selector
Selects a deterministic edge-case template (flaky_tests/big_refactor/security_privacy).

### 13) idea_scoring
Scores ideas deterministically against constraints to pick top candidates.

### 14) plan_diff_apply
Applies a PlanDiffSpec to a PlanSpec (tool-side).

### 15) decision_feedback
Tool-first post-run feedback for Personaler and other special agents (mode-aware: strict/balanced/creative).

### 16) deliberation_pack_build
Builds a compact DeliberationPackSpec for Deep Oodle reasoning (snippets + signals + questions).

### 17) outcome_ledger_append
Append an OutcomeLedgerEvent to a local jsonl ledger (tool-first).

### 18) route_autotune_suggest
Suggest up to 3 routing tweaks from outcome ledger history (tool-first).

### 19) contract_drift_sentinel
Detect schema/example drift and missing schema references in tasks (tool-first).

### 20) policy_gatekeeper
Central deterministic gate for deep oodle, creative feedback, rebuild, experiments, and no-LLM compliance.

### 21) evidence_router
Deterministically selects minimal evidence (files + log tails) for a requested action.

### 22) exec_dryrun
Validates a CommandSpec without executing it (cwd/exit codes/timeout).

### 23) route_profile_patch_pack
Turns RouteAutotuneSuggestion into up to 3 RouteProfileSpec patch files (approval-gated).

### 24) outcome_event_generate
Generates an OutcomeLedgerEvent from routing/quality/ledger evidence (tool-first).

### 25) triad_build
Builds a MessageTriadSpec container (source + optional translation + work brief + fallback policy).

### 26) triad_ref_lint
Validates MessageTriad work_brief completeness and enforces max_words/max_chars + max_plan_tasks.

### 27) qa_gate
Runs the **hard QA gate** (PR-blocking fast checks):
- repo_validate + contract drift + topology + SSoT path resolution + semantic drift

### 28) doc_ssot_resolver
Resolves backticked path references under `.claude/` using Path Semantics rules and reports missing targets.

### 29) drift_semantic_check
Semantic drift sentinel:
- Skills Registry ↔ Skill Runner mismatch
- Contract drift sentinel
- SSoT path references

### 30) team_topology_verify
Verifies required agent hierarchy files/folders exist and that critics/learning roles are present.

### 31) capability_map_build
Builds a machine-readable map of available capabilities (skills, agents, contracts, governance, tasks).

### 32) budget_router
Deterministic **cost/latency budgeting** for routing:
- recommends Oodle/Claude tiers + constraints
- provider-agnostic; does not call models

### 33) evidence_bundle_build
Builds an evidence bundle:
- `artifacts/evidence_bundle_manifest.json`
- `artifacts/evidence_bundle.zip`

### 34) security_redactor
Creates a redacted copy of an evidence folder and emits `reports/redaction_report.json`.

### 35) determinism_harness
Deterministic digest over files/dirs with optional JSON normalization (stable hashing for regression).

### 36) refactor_bridge_scan
Scans a repo for legacy markers (`src/`, `.claude/`, `claude-documents/`, etc.) and suggests refactor bridge steps.

### 37) release_cut
One-button release cut:
- evidence_init → qa_gate → evidence_bundle_build → (optional) security_redactor → pack_manifest

### 38) schema_batch_validate
Validates **all** contract schemas against their matching examples (batch mode). Useful for extended QA / releases.

### 39) doc_write
Deterministic documentation file writer:
- writes one or many markdown files from prepared content
- produces a unified diff for review
- blocks path traversal (stays inside `project_root`)

### 40) tutorial_write
Deterministic tutorial renderer + writer:
- accepts `tutorial_spec` (structured) or ready-made markdown
- validates required tutorial sections and emits warnings
- writes via `doc_write` and returns a diff

### 41) doc_review
Deterministic doc lint review:
- TODO/TBD leftovers
- missing required sections (tutorial/user guide/architecture/security)
- basic broken local links
- code fence language tag hints
- heading level jump detection

### 42) repo_compare
Deterministic folder diff tool:
- added/removed/changed (sha256)
- optional markdown report written under `.llama_runtime/knowledge/writes/compare_reports/`
- intended for comparing Claude Code ↔ Llama Code baselines

### 43) screencast_script
Deterministic screencast script writer:
- renders a chapter + shot list script from `script_spec`
- writes Markdown via `doc_write` and returns a diff

## Analysis Suite AddOns

### 44) pattern_detect
Detect recurring code patterns (heuristic first-pass) and write a report.

### 45) mutation_detect
Compare two snapshots and detect renames/moves plus change sets.

### 46) system_map
Heuristic module dependency map (imports/includes) with Mermaid output.

### 47) mechanic_explain
Generate a structured mechanic explanation scaffold from evidence files.

### 48) code_assimilate
Draft an integration plan to assimilate foreign code into a host framework.

### 49) log_standardize
Lint logging usage and conventions (first-pass).

### 50) copyright_standardize
Lint copyright/license header compliance.

### 51) reference_fix
Detect (and optionally rewrite) broken markdown references after folder moves.

## Meta Skills (Autodiscovery & Forge)

### 52) skill_registry_search
Search registry + tool names by keywords and return candidate skills.

### 53) skill_gap_detect
Detect capability gaps for an intent and suggest a minimal new skill.

### 54) skill_scaffold
Scaffold a new deterministic skill (tool + schema + example + task + registry entry).

### 55) pdf_render
Render a high-quality PDF from an already-prepared Markdown manuscript, optional diagram specs, and style options.
- deterministic: no LLM calls
- inputs: markdown (string or path), diagrams (JSON spec or path), output pdf_path
- outputs: pdf_path, render_warnings



### 56) repo_clean_scan
Deterministic repo cleaning scanner:
- finds junk artifacts (caches, temp files)
- detects unreferenced docs (heuristic reachability)
- detects duplicates (sha256) and large files
- outputs a cleanup plan (archive-first)

### 57) code_clean_scan
Deterministic code cleaning scanner:
- builds a lightweight import graph (Python)
- finds orphan modules and unregistered skill modules
- flags markers (deprecated/todo/legacy/path drift)
- outputs a conservative report with limitations


### 58) last_train_merge
Deterministic zip evolution analyzer + merger:
- scans multiple zips, ignores cache artifacts
- generates evolution vs loss timeline
- emits combined zip containing the union (latest wins)

### 59) shadow_prompt_minify
Shadow prompt generator:
- builds `.claude_shadow/` with condensed prompt instructions
- deterministic minify + optional LLM refinement playbook
- produces a quality gap report


### 60) cleanup_plan_apply
Applies a cleanup plan (archive-first):
- dry_run by default
- delete disabled by default
- refuses ops outside root
- writes a cleanup_apply_report


### 61) autodocs_generate
Deterministic per-skill documentation generator:
- creates `skills/<id>/README.md` for each `tools/skills/<id>.py`
- classifies core vs addon via `addons/map.yaml`

### 62) hardening_scan_fix
Deterministic hardening pass:
- finds and classifies inconsistencies
- optional safe fixes (explicit apply mode)
- maintains a small decision brain store


### 63) limitation_harvest_scan
Limitation Harvest pre-step for DocForge:
- scans repo/tasks/skills for limitations, non-goals, future work
- generates a writer-ready Expected-but-missing list with evidence
- flags unimplemented skill gaps (task/registry vs tool/mapping)


### 64) budget_analyze
Token budget analysis:
- aggregates events by role/model/task
- outputs CLI-friendly ASCII bars
- exports matplotlib charts under `.claude-performance/`

### 65) efficiency_review
Efficiency review consolidation:
- merges worker/teamlead/judge panel JSON with budget report
- outputs scores + suggestions + charts

### 66) performance_toggle
Enable/disable performance budgeting (token cost reporting) via config.

### 67) performance_finalize
End-of-run budgeting export runner (budget report + optional efficiency review) with auto-disable threshold.

### 68) critics_board_review
Consolidate multi-critic panel outputs (legal/security/moral/creative/methodical) into one go/no-go report.

### 69) token_event_log
Append one `budget_event` line to `.claude-performance/events/<run_id>.jsonl`.
- used by wrappers to attribute token spend by role/model/task

### 70) work_scope_assess
Heuristic workload/effort assessment for routing decisions (low/medium/high tiers).

### 71) model_routing_select
Personaler model selector:
- chooses cheapest model likely good enough based on tier + hit list stats
- writes routing report under `.report/routing/<run_id>/`

### 72) model_routing_record_outcome
Update routing hit list stats after a run (success/quality/tokens per task_type).

## MVP02 — Deterministic Skill Framework v1

| Skill | Description | Contract | Implementation |
|-------|-------------|---------|----------------|
| hello | Simple greeting skill | contracts/schemas/hello.schema.json | tools/skills/hello.py |
| scan | Directory glob scanner skill | contracts/schemas/scan.schema.json | tools/skills/scan.py |
| report | Markdown report builder skill | contracts/schemas/report.schema.json | tools/skills/report.py |

### 73) hello
Simple deterministic greeting skill (MVP02).
- Input: `{"name": "string"}`
- Output: `{"message": "Hello, <name>!", "status": "ok"}`
- Standalone: `python tools/skills/hello.py '{"name": "World"}'`

### 74) scan
Deterministic directory glob scanner (MVP02).
- Input: `{"path": "string", "pattern": "string (glob)"}`
- Output: `{"files": ["string"], "count": integer, "status": "ok"}`
- Standalone: `python tools/skills/scan.py '{"path": ".", "pattern": "**/*.py"}'`

### 75) report
Deterministic Markdown report builder (MVP02).
- Input: `{"title": "string", "items": ["string"]}`
- Output: `{"report": "string (markdown)", "item_count": integer, "status": "ok"}`
- Standalone: `python tools/skills/report.py '{"title": "My Report", "items": ["a", "b"]}'`

### 76) escalation_router
Cheapest-first model routing with automatic escalation (wraps `.claude/tools/skills/escalation_router.py`; claudeclockwork native: planned Phase 3).
- Input: `{"ladder": "haiku"|"sonnet", "messages": [...], "max_tokens": int, "dry_run": bool}`
- Output: `{"model_used": str, "rung": int, "content": str, "escalated": bool, "escalation_reason": str|null}`
- Escalates on HTTP 429/529/503/500, timeout, or empty response
- `dry_run=true` returns ladder config without any API call
- Schema: `contracts/schemas/escalation_router.schema.json`
- Example: `contracts/examples/escalation_router_example.json`
- Standalone: `python tools/skills/escalation_router.py '{"skill_id":"escalation_router","inputs":{"ladder":"haiku","messages":[{"role":"user","content":"hello"}],"dry_run":true}}'`

### 77) create_mvp
Autonomously creates new MVP entries in the Clockwork MVP chain (CCW-MVP20).
- Input: `{"trigger": "user_instruction"|"audit_gap"|"defect"|"parity_scan"|"manual", "trigger_ref": str|null, "mvp_name": str|null, "domain": str, "scope": [str], "dry_run": bool}`
- Output: `{"mvp_id": str, "mvp_entry": str, "written_to": str|null, "status": "ok"|"dry_run"|"error"}`
- Reads chain file to determine next MVP number; appends using atomic write (.tmp → rename)
- Logs creation to `.claude-development/audits/logs/audit_log_<date>.md`
- Schema: `contracts/schemas/create_mvp.schema.json`
- Example: `contracts/examples/create_mvp_example.json`
- Standalone: `python3 tools/skills/create_mvp.py '{"skill_id":"create_mvp","inputs":{"trigger":"manual","mvp_name":"Test MVP","domain":"testing","scope":["test_skill"],"dry_run":true}}'`

### 78) clockwork_version_bump
Bumps the Clockwork semver, writes a changelog entry, and optionally creates a git tag (CCW-MVP21).
- Input: `{"bump_type": "major"|"minor"|"patch", "summary": str, "affected_mvps": [str], "tag_git": bool, "dry_run": bool}`
- Output: `{"previous_version": str, "new_version": str, "changelog_entry": str, "tag_created": bool, "status": "ok"|"dry_run"|"error"}`
- Reads version from `.claude/VERSION`; writes date-stamped entry to `.claude/changelog/`; updates `.claude/CHANGELOG.md` header
- Schema: `contracts/schemas/clockwork_version_bump.schema.json`
- Example: `contracts/examples/clockwork_version_bump_example.json`
- Standalone: `python3 tools/skills/clockwork_version_bump.py '{"skill_id":"clockwork_version_bump","inputs":{"bump_type":"minor","summary":"Added Create MVP skill","affected_mvps":["CCW-MVP20"],"dry_run":true}}'`

### 79) clockwork_changelog_entry
Lightweight companion to clockwork_version_bump — adds a changelog line without bumping version (CCW-MVP21).
- Input: `{"version": str, "entry_text": str, "category": "added"|"changed"|"fixed"|"removed"}`
- Output: `{"written_to": str, "status": "ok"|"error"}`
- Appends a single categorized entry to the active changelog file
- Schema: `contracts/schemas/clockwork_version_bump.schema.json` (shared)
- Example: `contracts/examples/clockwork_version_bump_example.json` (shared)

### 80) eval_run
Eval harness runner — executes golden tests and detects regressions (CCW-MVP11).
- Input: `{"golden_dir": str, "output_dir": str, "skills_dir": str, "compare_previous": bool}`
- Output: `{"tests_run": int, "pass_count": int, "fail_count": int, "error_count": int, "regression_count": int, "results_file": str}`
- Loads all `*.json` fixtures from `golden_dir`, runs each via the skill's `run(req)` interface, saves timestamped results, compares against previous run for regressions
- Exit status `ok` only when all tests pass and regression_count == 0
- Schema: `contracts/schemas/eval_run.schema.json`
- Example: `contracts/examples/eval_run_example.json`
- Standalone: `python3 .claude/tools/skills/eval_run.py '{"skill_id":"eval_run","inputs":{"golden_dir":".claude/eval/golden","compare_previous":true}}'`
- Direct runner: `python3 .claude/eval/eval_runner.py`

### 81) cleanup_apply
Applies a cleanup plan (JSON) to the filesystem (CCW-MVP13).
- Input: `{"plan_path": str, "root": str, "dry_run": bool, "allow_delete": bool, "on_conflict": "skip"|"overwrite"|"rename", "write_report": bool, "report_dir": str}`
- Output: `{"operations": [...], "summary": {moved, deleted, skipped, missing, errors, total}, "dry_run": bool}`
- dry_run=True by default — safety first; no filesystem changes unless explicitly disabled
- allow_delete=False by default; delete ops skipped with warning unless enabled
- Supported actions: move, delete, archive, rename
- Paths outside root are refused for security
- Schema: `contracts/schemas/cleanup_apply_report.schema.json`
- Example: `contracts/examples/cleanup_apply_example.json`
- Standalone: `python3 tools/skills/cleanup_apply.py '{"skill_id":"cleanup_apply","inputs":{"plan_path":"plan.json","dry_run":true}}'`

### 82) repo_clean
Repository clutter scanner (CCW-MVP13).
- Input: `{"root": str, "scan_only": bool, "patterns": [str]}`
- Output: `{"findings": [{category, path, size_bytes}], "duplicates": [...], "summary": {files_found, total_size_bytes, categories}}`
- scan_only=True by default — never modifies filesystem
- Detects: cache dirs (__pycache__, .pytest_cache, etc.), temp/system files (*.pyc, .DS_Store, etc.), empty dirs, duplicate filenames
- Schema: `contracts/schemas/repo_clean_report.schema.json`
- Example: `contracts/examples/repo_clean_example.json`
- Standalone: `python3 tools/skills/repo_clean.py '{"skill_id":"repo_clean","inputs":{"root":".","scan_only":true}}'`

### 83) code_clean
Python code quality scanner (CCW-MVP13).
- Input: `{"root": str, "scan_only": bool, "emit_plan": bool}`
- Output: `{"findings": [{category, file, line, detail}], "summary": {files_scanned, findings_total, by_category}, "plan": [...] (when emit_plan=True)}`
- scan_only=True by default — never modifies filesystem
- Detects: TODO/FIXME/HACK markers, unused imports (heuristic), long functions (>100 lines), stub files
- emit_plan=True adds a "plan" field with suggested remediation actions
- Schema: `contracts/schemas/code_clean_report.schema.json`
- Example: `contracts/examples/code_clean_example.json`
- Standalone: `python3 tools/skills/code_clean.py '{"skill_id":"code_clean","inputs":{"root":".","scan_only":true,"emit_plan":false}}'`

### 84) telemetry_summarize
Aggregates JSONL telemetry events into grouped token/cost/quality summaries (CCW-MVP12).
- Input: `{"events_dir": str, "run_id_filter": str|null, "group_by": [str], "top_n": int}`
  - `events_dir` defaults to `.claude-performance/events/`
  - `group_by` defaults to `["role", "model"]`; supports any TelemetryEvent fields
  - `top_n` defaults to 10
- Output: `{type: telemetry_summary, groups: [{key, total_tokens, avg_tokens, run_count, total_cost_cents, avg_quality_score}], totals: {events, total_tokens, total_cost_cents}, period: {from, to}, status}`
- Groups sorted by total_tokens descending; empty events_dir returns status: ok with zero groups
- stdlib only: json, pathlib, glob, collections, datetime, sys
- Schema (output): `contracts/schemas/telemetry_summary.schema.json`
- Example (input): `contracts/examples/telemetry_summarize_example.json`
- Event schema: `contracts/schemas/telemetry_event.schema.json`
- Event example: `contracts/examples/telemetry_event_example.json`
- Standalone: `python3 tools/skills/telemetry_summarize.py '{"skill_id":"telemetry_summarize","inputs":{"events_dir":".claude-performance/events/","group_by":["role","model"],"top_n":5}}'`

### 85) review_panel
Consolidates multi-reviewer verdicts (worker/team_lead/judge) into a final panel decision (CCW-MVP12).
- Input: `{"reviews": [{reviewer, role, verdict, score, notes}], "task_ref": str, "consolidation": "majority"|"unanimous"|"weighted"}`
  - `consolidation` defaults to `"majority"`
  - majority: most common verdict wins; ties resolved by severity (fail > warn > pass)
  - unanimous: pass only if all reviewers vote pass; any warn → warn; any fail → fail
  - weighted: worker=0.3, team_lead=0.5, judge=0.2 applied to score; >= 0.6 → pass, >= 0.4 → warn, else fail
- Output: `{type: review_panel_result, task_ref, final_verdict, confidence, individual_reviews, dissenting, recommendations, status}`
  - `dissenting`: reviewer names whose verdict differs from final_verdict
  - `recommendations`: deduplicated notes collected from warn/fail reviewers
- stdlib only: json, collections, sys
- Schema (request): `contracts/schemas/review_panel_request.schema.json`
- Schema (result): `contracts/schemas/review_panel_result.schema.json`
- Example: `contracts/examples/review_panel_example.json`
- Standalone: `python3 tools/skills/review_panel.py '{"skill_id":"review_panel","inputs":{"task_ref":"test","consolidation":"majority","reviews":[{"reviewer":"alice","role":"worker","verdict":"pass","score":0.9,"notes":""},{"reviewer":"bob","role":"team_lead","verdict":"warn","score":0.6,"notes":"Needs edge-case tests"}]}}'`

## MVP14 — Archive & Prompt Evolution (CCW-MVP14)

### 86) last_train
Summarizer/viewer for a `last_train_report.json` produced by `last_train_merge` (CCW-MVP14).
- Input: `{"report_path": str, "output_format": "json"|"markdown", "write_summary": bool, "summary_dir": str}`
- Output: `{"type": "last_train_summary", "timeline": [{step, verdict, notes}], "combined_zip": str|null, "total_evolution_steps": int, "total_loss_steps": int, "total_mixed_steps": int, "output_format": str, "status": "ok"|"error"}`
- Counts evolution / loss / mixed verdicts across the timeline; optionally writes JSON or Markdown summary
- Schema (report consumed): `contracts/schemas/last_train_report.schema.json`
- Example: `contracts/examples/last_train_example.json`
- Standalone: `python3 .claude/tools/skills/last_train.py '{"skill_id":"last_train","inputs":{"report_path":"path/to/last_train_report.json","output_format":"json"}}'`

### 87) shadow_prompt
Triage skill for a `shadow_prompt_report.json` produced by `shadow_prompt_minify` (CCW-MVP14).
- Input: `{"report_path": str, "min_quality_score": float, "write_triage": bool, "triage_dir": str}`
- Output: `{"type": "shadow_prompt_triage", "accept_sections": [str], "flagged_sections": [str], "rejected_sections": [str], "ranked_fixes": [{section, current_score, suggested_action}], "quality_gate_pass": bool, "status": "ok"|"error"}`
- Classifies sections: accept (>= threshold), flag (>= 0.3 and < threshold), reject (< 0.3)
- Ranks fixes ascending by score (worst first); suggests rewrite / expand / remove
- Schema (output): `contracts/schemas/shadow_prompt_triage.schema.json`
- Example: `contracts/examples/shadow_prompt_example.json`
- Standalone: `python3 .claude/tools/skills/shadow_prompt.py '{"skill_id":"shadow_prompt","inputs":{"report_path":"path/to/shadow_prompt_report.json"}}'`

## MVP15 — PDF Quality Skill (CCW-MVP15)

### 88) pdf_quality
Deterministic quality rubric scorer for Markdown manuscripts — no LLM calls (CCW-MVP15).
- Input: `{"manuscript_path": str, "scope": "general"|"lastenheft"|"tutorial"|"api_docs", "target_audience": str, "max_fixes": int, "write_report": bool, "report_dir": str}`
- Output: `{"type": "quality_gap_report", "score": float, "dimension_scores": {coverage, structure, clarity, correctness, diagrams}, "fix_list": [{item, dimension, priority}], "gate_pass": bool, "status": "ok"|"error"}`
- Scores 5 dimensions: coverage (30%), structure (20%), clarity (20%), correctness (20%), diagrams (10%)
- Gate passes when overall score >= 70; fix_list sorted worst dimension first
- Schema (request): `contracts/schemas/pdf_quality_request.schema.json`
- Example: `contracts/examples/pdf_quality_example.json`
- Standalone: `python3 .claude/tools/skills/pdf_quality.py '{"skill_id":"pdf_quality","inputs":{"manuscript_path":"docs/README.md","scope":"general"}}'`

### 89) pdf_export
Batch-export Markdown documentation files to PDF (or HTML fallback) — ghost-skill registration (CCW-MVP15).
- Input: `{"project_root": str, "doc_files": [str], "output_dir": str, "naming_scheme": "flat_underscore"|"hierarchical", "fallback_fmt": "html"|"markdown", "mermaid": "embed_as_text"|"skip", "dry_run": bool}`
- Output: `{"exported": [{input_file, output_file, status, tool, bytes, warnings}], "skipped": [{input_file, reason}], "tool_used": str, "output_dir": str, "dry_run": bool}`
- Auto-detects pandoc → reportlab → html fallback; `dry_run=true` (default) plans without writing
- Schema (request): `contracts/schemas/pdf_export_request.schema.json`
- Example: `contracts/examples/pdf_export_example.json`
- Standalone: `python3 .claude/tools/skills/pdf_export.py '{"skill_id":"pdf_export","inputs":{"doc_files":["docs/README.md"],"dry_run":true}}'`

## MVP16 — Parity Scan Planner Implementation + Registry Integrity (CCW-MVP16)

### 90) parity_scan_and_mvp_planner
Deterministic file-evidence parity scanner (CCW-MVP16).
- Input: `{"run_date": str, "scan_scope": [str], "reference_mvp_chain": str, "output_dir": str, "generate_mvp_plan": bool, "mvp_plan_output_dir": str}`
- Output: `{"parity_matrix": str, "backlog": str, "mvp_plan": str|null, "gap_count": int, "partial_count": int, "full_count": int, "p0_count": int, "p1_count": int, "p2_count": int, "status": "ok"|"error"}`
- Reads MVP chain markdown, classifies each section as FULL/PARTIAL/GAP based on file evidence
- Writes `parity_matrix_<run_date>.md` and `missing_features_backlog_<run_date>.md` to `output_dir`
- Optionally writes `M2_parity_followup_plan_<run_date>.md` when `generate_mvp_plan=true`
- No LLM calls — stdlib only (json, pathlib, sys, datetime, re)
- Schema: `contracts/schemas/parity_scan_and_mvp_planner.schema.json`
- Example: `contracts/examples/parity_scan_and_mvp_planner_example.json`
- Standalone: `python3 .claude/tools/skills/parity_scan_and_mvp_planner.py '{"skill_id":"parity_scan_and_mvp_planner","inputs":{"run_date":"2026-03-02"}}'`

### 91) idea_dedupe
Deterministic idea deduplication skill (CCW-MVP16).
- Input: `{"ideas": [str], "method": "exact"|"normalized"|"levenshtein", "similarity_threshold": float}`
  - `method` defaults to `"normalized"` (case+punctuation-insensitive)
  - `similarity_threshold` defaults to `0.8` (used only by levenshtein method)
- Output: `{"unique_ideas": [str], "duplicate_groups": [{canonical, duplicates}], "removed_count": int}`
- No LLM calls — stdlib only (json, re, sys)
- Schema: `contracts/schemas/idea_dedupe_spec.schema.json`
- Example: `contracts/examples/idea_dedupe.skill_request.example.json`
- Standalone: `python3 .claude/tools/skills/idea_dedupe.py '{"skill_id":"idea_dedupe","inputs":{"ideas":["hello world","Hello World","foo bar"],"method":"normalized"}}'`
