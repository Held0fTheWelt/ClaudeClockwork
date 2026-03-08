# ClaudeClockwork — MVP Chain (Start at MVP 01)
*As of: 2026-03-02*

> **Scope:** This chain is **ClaudeClockwork only** — the `.claude/` methodology, skills, agents, governance, and Clockwork-specific tooling.  
> **Not in scope:** **LlamaCode** is a separate framework with its own roadmap and MVPs. Do not add LlamaCode MVPs or LlamaCode-framework deliverables to this chain. References to repo paths (e.g. runtime packages) are integration points only; this document does not define the LlamaCode framework.  
> **Parity MVP08:** The specification for **CCW‑MVP08** is canonical and is adopted 1:1.

---

## Chronological MVP Archive

Single table of all MVPs in delivery order. Use this to trace history; full definition of each MVP is in the section with the same ID below.

| # | MVP ID | Name | Status | Date / Milestone |
|---|--------|------|--------|-------------------|
| 1 | CCW-MVP01 | Repo & Runtime Scaffolding (Clockwork Core) | done | 2026-03-02 |
| 2 | CCW-MVP02 | Deterministic Skill Framework v1 | done | 2026-03-02 |
| 3 | CCW-MVP03 | Agent Layer v1 (Prompts + Roles + Routing Policy Stub) | done | 2026-03-02 |
| 4 | CCW-MVP04 | Documentation Ops v1 (Write/Review/Index) | done | 2026-03-02 |
| 5 | CCW-MVP05 | Governance & Policy Enforcement v1 | done | 2026-03-02 |
| 6 | CCW-MVP06 | Reports & Telemetry Layout v1 | done | 2026-03-02 |
| 7 | CCW-MVP07 | Milestone System v1 (.claude-development/ scaffolding) | done | 2026-03-02 |
| 8 | CCW-MVP08 | Parity Scan Skill + MVP Pre-Planning (Clockwork-only) | done | 2026-03-02 |
| 9 | CCW-MVP09 | Parity Follow-up M1: Routing & Model Selection (Design MVP) | done | 2026-03-02 |
| 10 | CCW-MVP10 | QA Gates & CI v1 | done | 2026-03-02 |
| 11 | CCW-MVP11 | Eval Harness / Golden Tests v1 | done | 2026-03-02 |
| 12 | CCW-MVP12 | Telemetry & Feedback Loop v1 | done | 2026-03-02 |
| 13 | CCW-MVP13 | Cleaning Suite Completion | done | 2026-03-02 |
| 14 | CCW-MVP14 | Archive & Prompt Evolution Completion | done | 2026-03-02 |
| 15 | CCW-MVP15 | PDF Quality Skill (DocForge PDF Pipeline) | done | 2026-03-02 |
| 16 | CCW-MVP16 | Parity Scan Planner Implementation + Registry Integrity | done | 2026-03-02 |
| 17 | CCW-MVP17 | Clockwork Invariants + CI Gate + Integration Tests | done | 2026-03-02 |
| 18 | CCW-MVP18 | Adaptive Routing & Telemetry Feedback Loop | done | 2026-03-02 |
| 19 | CCW-MVP19 | Meta-Tooling: QA Gate Extension + Addon CI + skill_runner Hygiene | done | 2026-03-02 |
| 20 | CCW-MVP20 | "Create MVP" Skill (Autonomous MVP Generation) | done | 2026-03-02 |
| 21 | CCW-MVP21 | Clockwork Versioning (Version Bumps + Changelog + Release Tags) | done | 2026-03-02 |
| 22 | CCW-MVP22 | Clockwork Invariant Cleanup | done | M2 Week 1 (2026-03-02) |
| 23 | CCW-MVP22-D | Runtime Critics Architecture (Design) | done | M2 Week 2 design sprint |
| 24 | CCW-MVP23-D | Capability Policy Design (Design) | done | M2 Week 2 design sprint |
| 25 | CCW-MVP24-D | Eval Harness Completion Design (Design) | done | M2 Week 2 design sprint |
| 26 | CCW-MVP23 | Runtime Critics v1 (Drift + Regression) | planned | M2 Week 3 |
| 27 | CCW-MVP24 | Capability Policy Enforcement | planned | M2 Week 3 |
| 28 | CCW-MVP25 | Eval Harness Completion | planned | M2 Week 3 |
| 29 | CCW-MVP26 | Security Hardening v1 | planned | M2 Week 4 |
| 30 | CCW-MVP30 | CBL Rung Unlock Ceremonies | planned | M2 Week 4 |
| 31 | CCW-MVP25-D | MAPE-K Learning Loop Design | planned | M2 Week 5–6 |
| 32 | CCW-MVP26-D | Plugin Runtime Design | planned | M2 Week 5–6 |
| 33 | CCW-MVP27 | MAPE-K Learning Loop v1 | planned | M2 Week 5–6 |
| 34 | CCW-MVP28 | Full Critics Suite (10 new critics) | planned | M2 Week 5–6 |
| 35 | CCW-MVP29 | Plugin Runtime v1 | planned | M2 Week 7–8 |
| 36 | CCW-MVP33 | Shadow-Operator Mode v1 | planned | M2 Week 7–8 |
| 37 | CCW-MVP27-D | Knowledge Graph Design | planned | M2 Week 9–12 |
| 38 | CCW-MVP28-D | Agent Genome & Evolution Design | planned | M2 Week 9–12 |
| 39 | CCW-MVP31 | Knowledge Graph v1 (SQLite) | planned | M2 Week 9–12 |
| 40 | CCW-MVP32 | Agent Genome & Evolution v1 | planned | M2 Week 9–12 |

**Status:** `done` = delivered; `planned` = not yet started. Evidence for delivered MVPs: `.claude/development/MVP_STATUS.md` and audit logs in `.claude-development/audits/logs/`.

---

## Core principles (for all MVPs)

### Core rules
1) **Design-first:** If a gap requires architectural decisions, ship a **design MVP** before implementation. fileciteturn13file0  
2) **Audit/Planning model policy:** Planning/audits run by default on **Sonnet** (Clockwork side). fileciteturn13file0  
3) **Write locations:**
   - **Development/Audit outputs:** `.claude-development/...` (MVP08+). Milestone plans, designs, audits live here; canonical MVP list: `Clockwork_MVP_Chain.md` in this folder.
   - **Reports (input):** `.report/...` (current cycle; read-only input in MVP08).  
4) **Stop-the-line:** Every new Clockwork milestone requires a parity checkpoint first.  
5) **ClaudeClockwork vs LlamaCode:** This chain defines only ClaudeClockwork MVPs. Deliverables that reference repo paths outside `.claude/` (e.g. runtime or backend modules) are integration points or implementation locations; they do not make the MVP a LlamaCode framework MVP. LlamaCode has its own framework and MVP lifecycle elsewhere.

### Definition of Done (DoD)
- Every capability includes:
  - deterministic contracts (schema + example)
  - 1 playbook + 1 minimal README (discoverable)
  - smoke test / minimal repro command
  - unambiguous storage (no “mystery files”)

---

# CCW-MVP01 — Repo & Runtime Scaffolding (Clockwork Core)
**Goal:** A minimal, clean foundation for `.claude/` + backend + CLI, including clear folder conventions.

## Deliverables
- Standard layout documented (top-level navigation in `.claude/INDEX.md`)
- Minimal “boot check” (CLI command): validates paths, required files, version info
- Naming/path conventions: “what goes where” (policies/skills/agents/contracts/tasks)

## Acceptance
- A fresh checkout can start without guesswork (“Start here” doc).
- No write access outside defined output locations.

---

# CCW-MVP02 — Deterministic Skill Framework v1
**Goal:** Deterministic skills are the base for all operational work (scan/report/apply).

## Deliverables
- `skill_runner` with standardized I/O:
  - `skill_request_spec` → `skill_result_spec`
- Contracts folder:
  - `schemas/` and `examples/`
- Registry: `skills/registry.md` as the catalog
- Safe-write convention: all skill outputs deterministic and diffable

## Acceptance
- At least 3 example skills (hello/scan/report) run end-to-end.
- Every skill can be executed via an example JSON.

---

# CCW-MVP03 — Agent Layer v1 (Prompts + Roles + Routing Policy Stub)
**Goal:** A clear agent layer (roles) without chaos.

## Deliverables
- `agents/` structure + READMEs:
  - TeamLead / Worker / Critic (systemic, technical)
- Model policy doc (Clockwork): default Sonnet for planning/audits
- Minimal orchestration standard:
  - “which role does what” + output format

## Acceptance
- Roles are discoverable and consistent.
- Each role has a clear output format (JSON or MD).

---

# CCW-MVP04 — Documentation Ops v1 (Write/Review/Index)
**Goal:** Documentation is not “text”; it is operational: generatable, reviewable, versioned.

## Deliverables
- Docs index + terminology:
  - glossary / naming / canonical docs
- Doc skills/workflows (deterministic): write + review + link health
- Minimum templates: First Steps, Architecture, API stub

## Acceptance
- Docs are repo-local linked with no broken references.
- “First Steps” leads to the first successful action.

---

# CCW-MVP05 — Governance & Policy Enforcement v1
**Goal:** Rules are enforceable, not just “nice to have”.

## Deliverables
- Policies (e.g., destructive actions, output roots, allowlists)
- Audit log template (who decided what)
- Safety hardlines for tools/apply: opt-in, dry-run defaults

## Acceptance
- Policies are testable as checklists.
- Violations are emitted as reports (not silently ignored).

---

# CCW-MVP06 — Reports & Telemetry Layout v1 (`.report` + raw telemetry)
**Goal:** Clear separation: “human reports” vs “raw telemetry”.

## Deliverables
- `.report/README.md` + standard structure
- Raw telemetry folder (tooling-specific) + minimal writer
- Naming: `<kind>_<run_id>_<timestamp>.*`

## Acceptance
- Each run can store reports cleanly without polluting the repo root.

---

# CCW-MVP07 — Milestone System v1 (`.claude-development/` scaffolding)
**Goal:** Prep for MVP08: development/audit outputs are standardized, linked, repeatable.

## Deliverables
- `.claude-development/milestones/index.md` (canonical index)
- `.claude-development/audits/` structure: `parity/`, `logs/`
- `.claude-development/audits/logs/audit_log_<YYYY-MM-DD>.md` template + first entry

## Acceptance
- Everything under `.claude-development/` is discoverable and linked from the index. Canonical MVP list: `Clockwork_MVP_Chain.md` in `.claude-development/`.

---

# CCW-MVP08 — Parity Scan Skill + MVP Pre-Planning (Clockwork-only)
> **Canonical specification:** see `CCW-MVP08 — Parity Scan Skill + MVP Pre-Planning (Clockwork-only)`. fileciteturn13file0  
> **Hard rules:** no runtime implementation; design-first; Sonnet default; outputs under `.claude-development/`. fileciteturn13file0

## Deliverables (from spec, 1:1)
1) Parity matrix: `.claude-development/audits/parity/parity_matrix_<YYYY-MM-DD>.md`
2) Missing features backlog: `.claude-development/audits/parity/missing_features_backlog_<YYYY-MM-DD>.md`
3) MVP pre-plan: `.claude-development/milestones/M1_parity_followup_plan_<YYYY-MM-DD>.md` (or M2_…)
4) Audit cadence spec: `.claude-development/audits/audit_cadence.md` + audit log template/entry  
5) New skill: `parity_scan_and_mvp_planner` incl. templates + checklist fileciteturn13file0  

## Acceptance (from spec)
- Evidence-backed parity matrix (repo pointers)
- Backlog is prioritized (security/correctness, leverage, effort)
- Plan is dependency-aware and Sonnet-policy compliant fileciteturn13file0  

---

# CCW-MVP09 — Parity Follow-up M1: Routing & Model Selection (Design MVP)
**Goal:** The parity matrix reveals gaps in routing/model selection → design first, then implementation.

## Deliverables
- Target architecture (routing pipeline, decision memory, rollback on failure)
- Integration points (backend/cli, agents, policies)
- Test plan (golden routing cases)

## Acceptance
- Decision points are explicit (when Haiku vs Sonnet vs Opus).
- Non-goals & boundaries are documented.

---

# CCW-MVP10 — QA Gates & CI v1 (Gate definition + enforcement)
**Goal:** Reproducible gates: docs health, policy integrity, security posture.

## Deliverables
- Gate checklist + CLI command
- Minimal CI wiring (repo-local)
- Report output to `.report/critics/<run_id>/` or `.report/hardening/<run_id>/`

## Acceptance
- Gate produces pass/fail + blockers + next actions.

---

# CCW-MVP11 — Eval Harness / Golden Tests v1
**Goal:** Make regressions visible: golden tests + trend.

## Deliverables
- Eval harness skeleton
- Golden cases (routing + docs + policy)
- Trend report format

## Acceptance
- A run produces a comparison against the previous run.

---

# CCW-MVP12 — Telemetry & Feedback Loop v1
**Goal:** Token/effort/quality feedback loop to improve routing and workflows.

## Deliverables
- Standard event schema
- Budget report aggregator
- Review panels (worker/teamlead/judge) format + consolidation

## Acceptance
- You can trace “where costs happened and by whom” (at least by role/model/task).

---

## Note
From **MVP09+**, MVP ordering and scope are intentionally parity-driven: the output of **MVP08 `parity_scan_and_mvp_planner`** determines the next sequence. fileciteturn13file0

---

# CCW-MVP13 — Cleaning Suite Completion (Ops / Repo Health)
**Goal:** Complete the three stub skills in the cleaning domain that have schemas but no Python implementation and no `skill_runner` dispatch entry: `cleanup_apply`, `repo_clean`, and `code_clean`.

Evidence: `.claude/skills/cleanup_apply/README.md`, `.claude/skills/repo_clean/README.md`, `.claude/skills/code_clean/README.md`; schemas present at `contracts/schemas/cleanup_apply_report.schema.json`, `repo_clean_report.schema.json`, `code_clean_report.schema.json`; no matching `.py` in `.claude/tools/skills/`; neither in `SKILLS` dispatch table in `skill_runner.py`; parity matrix row 17, defect P1-003.

## Deliverables

- **`cleanup_apply`**: Python implementation in `.claude/tools/skills/cleanup_apply.py`
  - What it does: Executes a `cleanup_apply_report` operation set produced by `cleanup_plan_apply` (dry-run or live). Archives or deletes files per plan. `dry_run: true` by default; `allow_delete: false` by default.
  - Inputs: `plan_path` (string, path/glob), `root` (string), `dry_run` (bool), `allow_delete` (bool), `on_conflict` (enum: skip|overwrite|rename), `write_report` (bool), `report_dir` (string)
  - Outputs: `cleanup_apply_report` with `operations` array, `summary`, `warnings`, `limitations`
  - Missing artifact: `contracts/examples/cleanup_apply.skill_request.example.json`

- **`repo_clean`**: Python implementation in `.claude/tools/skills/repo_clean.py`
  - What it does: Top-level orchestrator that runs `repo_clean_scan` then optionally hands off to `cleanup_apply`; returns a combined report.
  - Inputs: `root` (string), `scan_only` (bool, default true), `auto_apply` (bool, default false)
  - Outputs: `repo_clean_report` with embedded scan results and optional apply summary
  - Missing artifact: `contracts/examples/repo_clean.skill_request.example.json`

- **`code_clean`**: Python implementation in `.claude/tools/skills/code_clean.py`
  - What it does: Top-level orchestrator that runs `code_clean_scan` then optionally emits a `cleanup_plan`; does not modify code directly.
  - Inputs: `root` (string), `scan_only` (bool, default true), `emit_plan` (bool, default false)
  - Outputs: `code_clean_report` with orphan modules, markers, optional plan
  - Missing artifact: `contracts/examples/code_clean.skill_request.example.json`

- Registry entries for all 3 skills added to `skills/registry.md` (numbered continuation after #76)
- `SKILLS` dispatch entries added to `skill_runner.py` for all 3
- `addons/map.yaml` `cleaning_suite` key updated to include `cleanup_apply`, `repo_clean`, `code_clean`
- `SKILL_HOWTO.md` updated with cleaning suite pipeline

## Acceptance
- All 3 skills run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke tests:
  - `python .claude/tools/skills/cleanup_apply.py '{"skill_id":"cleanup_apply","inputs":{"plan_path":"nonexistent.json","dry_run":true}}'` returns `status: error` with a clear message
  - `python .claude/tools/skills/repo_clean.py '{"skill_id":"repo_clean","inputs":{"root":".","scan_only":true}}'` returns valid JSON
  - `python .claude/tools/skills/code_clean.py '{"skill_id":"code_clean","inputs":{"root":".","scan_only":true}}'` returns valid JSON

---

# CCW-MVP14 — Archive & Prompt Evolution Completion (Packaging / Shadow Prompts)
**Goal:** Implement the two stub skills `last_train` and `shadow_prompt` that exist as `skills/` directories with READMEs and schemas but have no Python implementation. Their `_merge` and `_minify` siblings already exist; these are the orchestrator / report-consumer layer.

Evidence: `.claude/skills/last_train/README.md`, `.claude/skills/shadow_prompt/README.md`; schemas present at `contracts/schemas/last_train_report.schema.json`, `shadow_prompt_report.schema.json`; examples reference only sibling skills (`last_train_merge`, `shadow_prompt_minify`); no `last_train.py` or `shadow_prompt.py` in `.claude/tools/skills/`; parity matrix row 17, defect P1-003.

## Deliverables

- **`last_train`**: Python implementation in `.claude/tools/skills/last_train.py`
  - What it does: Reads a `last_train_report.json` produced by `last_train_merge` and emits a human-readable evolution timeline summary. Does not re-scan zips.
  - Inputs: `report_path` (string, path to existing `last_train_report.json`), `output_format` (enum: json|markdown, default json), `write_summary` (bool, default false), `summary_dir` (string)
  - Outputs: `type: last_train_summary`, `timeline` (array of verdict items), `combined_zip` (string or null), `total_evolution_steps`, `total_loss_steps`, `total_mixed_steps`, `status`
  - Missing artifact: `contracts/examples/last_train.skill_request.example.json`
  - Schema: re-uses `last_train_report.schema.json`; new output schema `last_train_summary.schema.json`

- **`shadow_prompt`**: Python implementation in `.claude/tools/skills/shadow_prompt.py`
  - What it does: Reads a `shadow_prompt_report.json` produced by `shadow_prompt_minify` and applies a quality-gap triage: classifies sections as accept/flag/reject, emits a ranked fix list, and optionally writes a triage markdown file.
  - Inputs: `report_path` (string, path to existing `shadow_prompt_report.json`), `min_quality_score` (float, default 0.6), `write_triage` (bool, default false), `triage_dir` (string)
  - Outputs: `type: shadow_prompt_triage`, `accept_sections`, `flagged_sections`, `rejected_sections`, `ranked_fixes` (array), `quality_gate_pass` (bool), `status`
  - Missing artifact: `contracts/examples/shadow_prompt.skill_request.example.json`
  - New schema: `contracts/schemas/shadow_prompt_triage.schema.json`

- Registry entries for both skills added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`
- `addons/map.yaml` `last_train_suite` and `shadow_prompts` keys updated
- `SKILL_HOWTO.md` updated with archive and shadow prompt pipeline

## Acceptance
- Both skills run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke tests:
  - `python .claude/tools/skills/last_train.py '{"skill_id":"last_train","inputs":{"report_path":"nonexistent.json"}}'` returns `status: error` with clear message
  - `python .claude/tools/skills/shadow_prompt.py '{"skill_id":"shadow_prompt","inputs":{"report_path":"nonexistent.json"}}'` returns `status: error` with clear message

---

# CCW-MVP15 — PDF Quality Skill (DocForge PDF Pipeline)
**Goal:** Implement `pdf_quality` as a deterministic skill with full schema + example + Python implementation. This is the only skill directory under `.claude/skills/` with zero schema coverage (no schema, no example). The rubric, templates, and playbook are already present.

Evidence: `.claude/skills/pdf_quality/README.md`, `.claude/skills/pdf_quality/rubric.md`, `.claude/skills/pdf_quality/templates/` (4 templates), `.claude/skills/pdf_quality/examples/` (3 sample files); no schema in `contracts/schemas/`; no example in `contracts/examples/`; no `.py` in `.claude/tools/skills/`; playbook at `.claude/skills/playbooks/pdf_quality_docforge.md`; `pdf_render` skill already exists and is registered.

Also addresses `pdf_export`: the `pdf_export.py` in `.claude/tools/skills/` is imported in `skill_runner.py` and dispatched as `"pdf_export"` but has no registry entry, no schema, and no example — a ghost skill.

## Deliverables

- **`pdf_quality`**: Python implementation in `.claude/tools/skills/pdf_quality.py`
  - What it does: Applies the DocForge rubric (`.claude/skills/pdf_quality/rubric.md`) deterministically to a prepared Markdown manuscript; scores it across 5 dimensions (coverage, structure, clarity, correctness, diagrams); emits a `quality_gap_report` with concrete fix list (max 10 items).
  - Inputs: `manuscript_path` (string), `scope` (string, e.g. "lastenheft"), `target_audience` (string), `max_fixes` (int, default 10), `write_report` (bool, default false), `report_dir` (string)
  - Outputs: `type: quality_gap_report`, `score` (0-100), `dimension_scores` (object), `fix_list` (array of {item, dimension, priority}), `gate_pass` (bool, threshold 70), `status`
  - New schema: `contracts/schemas/pdf_quality_request.schema.json`
  - New example: `contracts/examples/pdf_quality.skill_request.example.json`

- **`pdf_export` registry registration**: Add registry entry to `skills/registry.md`
  - Add schema: `contracts/schemas/pdf_export_request.schema.json`
  - Add example: `contracts/examples/pdf_export.skill_request.example.json`
  - `pdf_export.py` already exists; inputs are: `project_root`, `doc_files`, `output_dir`, `naming_scheme`, `fallback_fmt`, `mermaid`, `dry_run`

- `addons/map.yaml` `docforge_pdf_quality` key updated to include `pdf_quality`
- Registry entries for `pdf_quality` and `pdf_export` added to `skills/registry.md`
- `SKILLS` dispatch entry added for `pdf_quality` in `skill_runner.py`
- `SKILL_HOWTO.md` updated with pdf_quality -> pdf_render pipeline

## Acceptance
- `pdf_quality` runs end-to-end via skill_runner
- `pdf_quality` has schema + example + .py
- `pdf_export` has schema + example + registry entry
- Smoke tests:
  - `python .claude/tools/skills/pdf_quality.py '{"skill_id":"pdf_quality","inputs":{"manuscript_path":"nonexistent.md"}}'` returns `status: error`
  - `python .claude/tools/skills/skill_runner.py --in .claude/contracts/examples/pdf_quality.skill_request.example.json --out /tmp/out.json` returns valid JSON with `status: ok` or `status: error`

---

# CCW-MVP16 — Parity Scan Planner Implementation + Registry Integrity (Meta / Audit)
**Goal:** Two related meta-level gaps: (1) `parity_scan_and_mvp_planner` has schema + example + `.md` skill spec but zero Python implementation — the canonical parity audit skill cannot run deterministically. (2) Four skills are unregistered or incorrectly wired in the dispatch table: `idea_dedupe`, `hello`, `scan`, `report`, `escalation_router`.

Evidence:
- `parity_scan_and_mvp_planner`: `.claude/skills/parity_scan_and_mvp_planner.md`; schema at `contracts/schemas/parity_scan_and_mvp_planner.schema.json`; example at `contracts/examples/parity_scan_and_mvp_planner_example.json`; no `.py` in `.claude/tools/skills/`; not in `SKILLS` dict in `skill_runner.py`; backlog item B-006.
- `idea_dedupe`: `.py` exists at `.claude/tools/skills/idea_dedupe.py`; `skills/idea_dedupe/` dir exists; NOT in registry numbered list; no schema; no example.
- `hello`, `scan`, `report`: in registry (#73-75) with schemas + examples; `.py` exists; NOT in `SKILLS` dispatch dict (standalone-only today).
- `escalation_router`: in registry (#76) with schema + example + `.py`; NOT in `SKILLS` dispatch dict; uses `llamacode/core/escalation_router.py` via wrapper.

## Deliverables

- **`parity_scan_and_mvp_planner`**: Python implementation in `.claude/tools/skills/parity_scan_and_mvp_planner.py`
  - What it does: Reads the MVP chain, scans the repo for file evidence, classifies each capability as FULL / PARTIAL / GAP, writes `parity_matrix_<date>.md` + `missing_features_backlog_<date>.md`, optionally writes MVP pre-plan. Sonnet-default (planning skill); deterministic file I/O only (no LLM call in tool layer).
  - Inputs (per existing schema): `run_date` (string), `scan_scope` (array), `reference_mvp_chain` (string), `output_dir` (string), `generate_mvp_plan` (bool), `mvp_plan_output_dir` (string)
  - Outputs (per existing schema): `parity_matrix`, `backlog`, `mvp_plan`, `gap_count`, `partial_count`, `full_count`, `p0_count`, `p1_count`, `p2_count`, `status`, `errors`
  - `SKILLS` dispatch entry added to `skill_runner.py`

- **`idea_dedupe` registration**:
  - Add registry entry (next number after #76) to `skills/registry.md`
  - Add schema: `contracts/schemas/idea_dedupe_spec.schema.json` -- inputs: `ideas` (array of strings), `similarity_threshold` (float), `method` (enum: exact|normalized|levenshtein); outputs: `unique_ideas` (array), `duplicate_groups` (array), `removed_count` (int)
  - Add example: `contracts/examples/idea_dedupe.skill_request.example.json`
  - Add `SKILLS` dispatch entry if not already present

- **Dispatch table fixes** for `hello`, `scan`, `report`, `escalation_router`:
  - Add all four to the `SKILLS` dict in `skill_runner.py` with appropriate `run` function imports
  - These already have .py + schema + example; this is a wiring-only fix

- `SKILL_HOWTO.md` updated with parity scan usage

## Acceptance
- `parity_scan_and_mvp_planner` runs end-to-end via skill_runner
- `idea_dedupe` has schema + example + registry entry
- `hello`, `scan`, `report`, `escalation_router` callable via skill_runner (not just standalone)
- Smoke tests:
  - `python .claude/tools/skills/skill_runner.py --in .claude/contracts/examples/parity_scan_and_mvp_planner_example.json --out /tmp/parity_out.json` produces a `parity_matrix_*.md` under `.claude-development/audits/parity/`
  - `python .claude/tools/skills/skill_runner.py --in .claude/contracts/examples/hello_example.json --out /tmp/hello_out.json` returns `status: ok`

---

# CCW-MVP17 — Clockwork Invariants + CI Gate + Integration Tests (Infrastructure / P0-P1)
**Goal:** Fix the four P0 invariant violations (runtime state inside `.claude/`), wire the CI gate, and add the first integration test for the core pipeline. These are backlog items B-001-B-005, B-011 -- the highest-priority structural defects from the parity scan.

Evidence:
- B-001: `.claude/knowledge/-Writes/` contains generated artifacts; defect P0-001 in `.report/03_clockwork_qa_findings_and_defects.md`
- B-002: `.claude/knowledge/outcome_ledger.jsonl` is mutable ledger in read-only clockwork; defect P0-002
- B-003: `.claude/knowledge/route_profiles.json` is mutable routing data; defect P0-003
- B-004: `.claude/brain/` contains mutable routing statistics; defect P1-006
- B-005: `.github/workflows/` is empty; `scripts/gate.sh` runs manually only; defect P1-005
- B-011: zero integration tests; `tests/` is unit-only; defect P2-006

## Deliverables

- **Invariant fixes (P0 + P1)**:
  - Move `.claude/knowledge/-Writes/` -> `.llama_runtime/writes/` (or `docs/_exports/`); update all references
  - Move `.claude/knowledge/outcome_ledger.jsonl` -> `.llama_runtime/knowledge/outcome_ledger.jsonl`; update `outcome_ledger_append.py` and `route_autotune_suggest.py` path references
  - Move `.claude/knowledge/route_profiles.json` -> `.llama_runtime/knowledge/route_profiles.json`; update `route_profile_update.py` and `route_profile_patch_pack.py` path references
  - Move `.claude/brain/` -> `.llama_runtime/brain/`; update all reader/writer references
  - For each: add `.llama_runtime/` path to `.gitignore` (if not already present) to prevent accidental commit of mutable state

- **CI gate** (B-005):
  - Create `.github/workflows/gate.yml` running `scripts/gate.sh` on every push + PR to `main`/`master`
  - Gate must exit non-zero on any failure (no swallowed errors)
  - Gate output goes to Actions log; no artifacts committed to repo

- **Integration test** (B-011): `tests/test_integration_pipeline.py`
  - Covers the core SkillRequestSpec -> `skill_runner` dispatch -> SkillResultSpec round-trip for at least 3 skills (`repo_validate`, `plan_lint`, `qa_gate`)
  - Uses temporary directories; no real filesystem side effects
  - Must pass in the CI gate

- `MEMORY.md` / `memory/MEMORY.md` updated with new runtime paths

## Acceptance
- `scripts/gate.sh` exits 0 on a clean repo
- `.github/workflows/gate.yml` file exists and references `gate.sh`
- `tests/test_integration_pipeline.py` passes (`pytest tests/test_integration_pipeline.py`)
- No mutable files remain under `.claude/` (verified by `contract_drift_sentinel` + repo_validate)
- `outcome_ledger_append` and `route_profile_update` skills write to new paths without error

---

# CCW-MVP18 — Adaptive Routing & Telemetry Feedback Loop (Routing / Intelligence)
**Goal:** Close the MAPE-K feedback loop: telemetry is collected but never consumed; routing is static YAML; the outcome ledger exists but does not inform model selection. Addresses backlog items B-013, B-015, B-016, B-019.

Evidence:
- B-013: `.claude/config/model_routing.yaml` is static; no `llamacode/core/bandit_router.py`; gap #1 in `.report/07_clockwork_power_addendum_gap_analysis.md`
- B-015: `.claude-performance/` data collected but unused; gap #7
- B-016: No runtime schema validation in skill execution path; defect P2-002
- B-019: `llamacode/core/salt_store.py` exists but not wired to LLM skill calls; gap #12

## Deliverables

- **Adaptive routing v1** (`llamacode/core/bandit_router.py`):
  - What it does: Epsilon-greedy bandit that consumes `outcome_ledger.jsonl` (now at `.llama_runtime/knowledge/`) to bias model selection; falls back to static YAML if ledger is absent or small
  - Inputs: `task_type` (string), `quality_threshold` (float), `cost_cap` (float), `epsilon` (float, default 0.1)
  - Outputs: `model_id`, `rung`, `confidence`, `source` (enum: bandit|static|fallback)
  - Must be importable without network access; no LLM calls
  - New schema: `contracts/schemas/bandit_routing_decision.schema.json`
  - New example: `contracts/examples/bandit_routing_decision.example.json`

- **Telemetry summarize skill** (`telemetry_summarize`):
  - What it does: Reads `.claude-performance/events/*.jsonl`; aggregates by role/model/task; emits a `telemetry_summary.json` consumed by `route_autotune_suggest` and the bandit router
  - Inputs: `events_dir` (string), `run_id_filter` (string or null), `group_by` (array, e.g. `["role","model"]`)
  - Outputs: `type: telemetry_summary`, `groups` (array of {key, total_tokens, avg_tokens, run_count}), `period`, `status`
  - New schema: `contracts/schemas/telemetry_summary.schema.json`
  - New example: `contracts/examples/telemetry_summarize.skill_request.example.json`
  - Implementation: `.claude/tools/skills/telemetry_summarize.py`
  - Registry entry added to `skills/registry.md`
  - `SKILLS` dispatch entry added to `skill_runner.py`

- **Runtime schema validation** (B-016): wire `spec_validate` into skill_runner hot path
  - Add optional `validate_input: true` flag to `SkillRequestSpec`; when set, `skill_runner` validates inputs against the skill's schema before dispatching
  - No breaking change: flag defaults to `false`; opt-in per request

- **Salt wiring** (B-019): extend `exec_dryrun` and LLM-calling skills to read from `llamacode/core/salt_store.py`
  - Each LLM call in a skill includes a deterministic `seed` derived from `salt_store.get_salt(run_id, skill_id, call_index)`
  - Salt stored in evidence bundle (`evidence_bundle_build` updated to include salt manifest)

## Acceptance
- `bandit_router.py` importable; returns routing decisions without network call
- `telemetry_summarize` runs end-to-end via skill_runner
- `validate_input: true` in a request causes `spec_validate` to run before dispatch
- Salt store wired; at least 2 existing LLM skills pass salt in their calls
- Smoke tests:
  - `python -c "from llamacode.core.bandit_router import BanditRouter; r = BanditRouter(); print(r.select('planning', 0.8, 0.01))"` returns a decision dict
  - `python .claude/tools/skills/skill_runner.py --in .claude/contracts/examples/telemetry_summarize.skill_request.example.json --out /tmp/tel_out.json` returns `status: ok`

---

# CCW-MVP19 — Meta-Tooling: QA Gate Extension + Addon CI + skill_runner Hygiene (Tooling / P1-P2)
**Goal:** Strengthen the tooling layer itself: extend the QA gate with 4 missing checks (B-009), validate addon packs in CI (B-020), mark stub skills correctly (B-006), and clean up `skill_runner.py` wiring gaps discovered in this parity cycle.

Evidence:
- B-006: skills listed as fully defined in registry but missing `.py`; creates false capability claims; defect P1-003 in `.report/03_clockwork_qa_findings_and_defects.md`
- B-009: QA gate missing 4 checks: pointer-file validation, skill-coverage check, addon-pack validation, agent-registry consistency; defects P1-004, P2-007
- B-020: 8 addon packs in `.claude/addons/` not validated by any gate; defect P2-007
- skill_runner orphan keys: grep of `SKILLS` dict revealed non-skill entries (`"model"`, `"role"`, `"run_id"`, `"task"`) from embedded env-var comment lines

## Deliverables

- **QA gate extensions** (4 new checks added to `qa_gate.py` and/or `scripts/gate.sh`):

  1. **Pointer-file validation** (B-009 / defect P1-004): for each file listed in `.claude/ARCHITECTURE.md`, `.claude/ROADMAP.md`, `.claude/MODEL_POLICY.md`, verify the redirect target exists in the project root; emit `FAIL` if any target is missing
  2. **Skill coverage check** (B-009 / defect P1-003): count skills in `registry.md` vs `.py` files in `tools/skills/`; emit `WARN` (not FAIL) if coverage < 95%; emit `FAIL` if a registered skill has no `SKILLS` dispatch entry
  3. **Addon pack validation** (B-020 / defect P2-007): for each pack in `addons/map.yaml`, verify every listed skill has a `.py` implementation; emit `FAIL` for any missing implementation
  4. **Agent registry consistency check** (B-009 / defect P2-001): compare `agents/` file count vs `llamacode/agents/registry.json` entry count; emit `WARN` if ratio > 5:1 (methodology far ahead of implementation)

- **Stub skill tagging** (B-006): add `status: stub` front-matter line to the README of each skill directory that has no `.py` implementation
  - Script: `scripts/tag_stub_skills.py` -- idempotent; reads `SKILLS` dict from `skill_runner.py`; adds/updates `status:` line in each stub skill README
  - `--dry-run` flag lists affected files without modifying them

- **Addon pack CI validation** (B-020): extend `.github/workflows/gate.yml` (created in MVP17) with a step that runs `scripts/validate_addons.py`
  - Script: `scripts/validate_addons.py` -- reads `addons/map.yaml`; for each pack + skill, checks `.py` exists; exits non-zero on any missing implementation

- **skill_runner hygiene**:
  - Remove orphan non-skill entries from `SKILLS` dict if present
  - Confirm `hello`, `scan`, `report`, `escalation_router`, `idea_dedupe` are in `SKILLS` dict (consolidating leftover wiring from MVP16 if not completed there)
  - Add `cleanup_apply`, `repo_clean`, `code_clean`, `last_train`, `shadow_prompt`, `pdf_quality`, `telemetry_summarize`, `parity_scan_and_mvp_planner` to `SKILLS` dict as their implementations land in earlier MVPs

- `SKILL_HOWTO.md` updated with stub-tagging and gate extension notes

## Acceptance
- `qa_gate` (via skill_runner) emits results for all 4 new checks
- `scripts/gate.sh` exits non-zero when a registered skill has no dispatch entry
- `scripts/validate_addons.py` exits 0 on a complete repo; non-zero if any addon skill is missing `.py`
- All stub skill READMEs contain `status: stub` line (verifiable before MVP13-16 implementations land)
- Smoke tests:
  - `python .claude/tools/skills/qa_gate.py '{"skill_id":"qa_gate","inputs":{"project_root":"."}}' ` covers all checks and returns `status: ok` or `status: partial` with specific blockers listed
  - `python scripts/tag_stub_skills.py --dry-run` prints list of affected READMEs without modifying files
  - `python scripts/validate_addons.py` exits 0 on a fully-implemented addon map

---

# CCW-MVP20 — "Create MVP" Skill (Autonomous MVP Generation)
**Goal:** A skill that autonomously creates new MVP entries in the chain — triggered by user instruction, audit findings (parity scan, defect reports, gap analysis), or any structured trigger. Enables the system to grow itself.

## Deliverables

1. **Skill: `create_mvp`**
   - Input:
     - `trigger`: `"user_instruction"` | `"audit_gap"` | `"defect"` | `"parity_scan"` | `"manual"`
     - `trigger_ref`: path to triggering artifact (e.g. parity_matrix or defect report)
     - `mvp_name`: proposed name (optional — skill can infer from trigger)
     - `domain`: domain/area of the MVP
     - `scope`: list of skill IDs or capability gaps to address
     - `dry_run`: bool (default false) — if true, return draft without writing
   - Output:
     - `mvp_id`: e.g. "CCW-MVP21"
     - `mvp_entry`: full Markdown text of the new MVP
     - `written_to`: file path where it was appended
     - `status`: ok | dry_run | error
   - Logic:
     - Reads Clockwork_MVP_Chain.md to determine next MVP number
     - Reads triggering artifact if provided
     - Generates MVP entry following exact chain format
     - Appends to Clockwork_MVP_Chain.md (unless dry_run)
     - Logs creation to `.claude-development/audits/logs/audit_log_<date>.md`

2. **Schema:** `.claude/contracts/schemas/create_mvp.schema.json`
3. **Example:** `.claude/contracts/examples/create_mvp_example.json`
4. **Implementation:** `.claude/tools/skills/create_mvp.py`
   - `run(req) -> dict` pattern
   - Reads chain file, finds last MVP number, generates next ID
   - Builds MVP markdown from inputs
   - Appends to chain file using atomic write (.tmp → rename)
   - Logs to audit log
5. **Trigger table:**

   | Trigger | Source | Example |
   |---------|--------|---------|
   | `user_instruction` | Direct user request | "create MVP for X" |
   | `audit_gap` | parity_matrix GAP row | B-013 adaptive routing |
   | `defect` | QA defects report P0/P1 | P0-001 runtime state |
   | `parity_scan` | parity_scan_and_mvp_planner output | missing_features_backlog |
   | `manual` | Ad-hoc, no specific trigger | — |

## Acceptance
- `python3 .claude/tools/skills/create_mvp.py '{"skill_id":"create_mvp","inputs":{"trigger":"manual","mvp_name":"Test MVP","domain":"testing","scope":["test_skill"],"dry_run":true}}'` returns a valid MVP draft as JSON
- When `dry_run=false`, the entry is appended to Clockwork_MVP_Chain.md and a log entry is written

---

# CCW-MVP21 — Clockwork Versioning (Version Bumps + Changelog + Release Tags)
**Goal:** Every meaningful Clockwork change gets a version bump, changelog entry, and optional git tag — fully traceable. Enables reproducible Clockwork releases.

## Deliverables

1. **Skill: `clockwork_version_bump`**
   - Input:
     - `bump_type`: `"major"` | `"minor"` | `"patch"` (semver)
     - `summary`: short description of what changed
     - `affected_mvps`: list of MVP IDs that triggered this bump (e.g. ["CCW-MVP20", "CCW-MVP21"])
     - `tag_git`: bool (default false) — whether to create a git tag
     - `dry_run`: bool (default false)
   - Output:
     - `previous_version`: e.g. "17.7.0"
     - `new_version`: e.g. "17.8.0"
     - `changelog_entry`: markdown text written
     - `tag_created`: bool
     - `status`: ok | dry_run | error
   - Logic:
     - Reads current version from `.claude/CHANGELOG.md` header or `.claude/VERSION` file
     - Increments according to bump_type
     - Appends entry to `.claude/changelog/` (date-stamped file)
     - Updates `.claude/CHANGELOG.md` header
     - Optionally runs `git tag v<version>` (only if tag_git=true AND not dry_run)

2. **Skill: `clockwork_changelog_entry`**
   - Lightweight companion — just adds a changelog line without bumping version
   - Input: `version`, `entry_text`, `category` (`added`|`changed`|`fixed`|`removed`)
   - Output: `written_to`, `status`

3. **Version file:** `.claude/VERSION`
   - Plain text, single line: `17.8.0`
   - Written/updated by `clockwork_version_bump`

4. **Versioning policy doc:** `.claude/governance/versioning_policy.md`
   - When to bump major vs minor vs patch
   - What triggers a version bump (new MVP completed, breaking change, security fix)
   - Clockwork version format: MAJOR.MINOR.PATCH
     - MAJOR: breaking changes to clockwork API/contracts
     - MINOR: new MVPs, new skills, new capabilities
     - PATCH: fixes, doc updates, registry entries
   - Rule: every completed MVP = at minimum a MINOR bump

5. **Schema:** `.claude/contracts/schemas/clockwork_version_bump.schema.json`
6. **Example:** `.claude/contracts/examples/clockwork_version_bump_example.json`
7. **Implementation:** `.claude/tools/skills/clockwork_version_bump.py`

## Acceptance
- `python3 .claude/tools/skills/clockwork_version_bump.py '{"skill_id":"clockwork_version_bump","inputs":{"bump_type":"minor","summary":"Added Create MVP skill","affected_mvps":["CCW-MVP20"],"dry_run":true}}'` returns previous + new version as JSON
- `.claude/VERSION` exists and contains current version after a non-dry run

---

## Note
From **MVP09+**, MVP ordering and scope are intentionally parity-driven: the output of **MVP08 `parity_scan_and_mvp_planner`** determines the next sequence. **MVP20** and **MVP21** introduce meta-capabilities — autonomous MVP generation and Clockwork versioning — enabling the system to grow and version itself in a traceable, reproducible manner.

---

# M2 — Clockwork Audit Follow-up (MVP22–MVP33)

*Source: M2_clockwork_audit_followup_plan_2026-03-02; gaps from Power Audit (.report/01–10). All MVP definitions live in this chain; milestone plan: `.claude-development/milestones/M2_clockwork_audit_followup_plan_2026-03-02.md`.*

---

## Design MVPs (do first)

| MVP ID | Name | Design outputs | Priority |
|--------|------|----------------|----------|
| MVP22-D | Runtime Critics Architecture | ADR Runtime Critics Integration; critic_result.schema.json; critic_gates.yaml spec; pipeline interface | P0 |
| MVP23-D | Capability Policy Design | capabilities.yaml (spec); command_allowlist.yaml; per-agent matrix; enforcement ADR | P0 |
| MVP24-D | Eval Harness Completion Design | task_suite.yaml; schedules.yaml; shadow/ and ab/ spec; CBL rung benchmarks | P0 |
| MVP25-D | MAPE-K Learning Loop Design | Data flow; feedback_event.schema.json; Monitor→Analyze→Plan→Execute→Knowledge | P1 |
| MVP26-D | Plugin Runtime Design | Plugin API; lifecycle; plugin_manifest.schema.json v2 | P1 |
| MVP27-D | Knowledge Graph Design | Entity model; SQLite DDL; query interface; migration .jsonl→SQLite | P2 |
| MVP28-D | Agent Genome & Evolution Design | Genome JSON schema; mutation operators; fitness; promotion/rollback | P2 |

---

# CCW-MVP22 — Clockwork Invariant Cleanup
**Goal:** Remove remaining invariant violations (V-001–V-006); add pointer docs at repo root; update INDEX.md.

## Deliverables
- V-001–V-004: Delete stale originals (verify M1 already done); V-005: add `.claude/eval/__pycache__/` to .gitignore, remove dir; V-006: move eval results to `.llama_runtime/eval/results/`, update defaults in eval_runner/eval_run.
- Create ARCHITECTURE.md, ROADMAP.md, MODEL_POLICY.md at project root.
- Update INDEX.md: VERSION string and paths.

## Acceptance
- No runtime files/caches under `.claude/`; eval output in `.llama_runtime/eval/results/`; root pointers exist; integration tests pass.

---

# CCW-MVP22-D — Runtime Critics Architecture (Design)
**Goal:** Before implementation: CriticResult schema, activation per escalation level, integration with quality_signal.

## Deliverables (Design)
- ADR: Runtime Critics Integration (`.claude-development/designs/adr_runtime_critics_integration.md`).
- `critic_result.schema.json`; critic_gates.yaml spec; critic–pipeline interface (diagram in ADR).

## Acceptance
- Schema and spec approved; implementation (MVP23) can start.

---

# CCW-MVP23 — Runtime Critics v1 (Drift + Regression)
**Goal:** Two runtime critics (Drift, Regression) wired to quality_signal; critic_gates.yaml.

**Depends on:** MVP22-D.

## Deliverables
- `llamacode/core/critics/drift_critic.py`, `regression_critic.py`; `critic_result.schema.json`; `critic_gates.yaml`; wire to quality_signal; contract + example; registry entry.

## Acceptance
- Both critics run after gate/eval; output as CriticResult; gate fails on threshold breach.

---

# CCW-MVP23-D — Capability Policy Design (Design)
**Goal:** Full spec for capabilities.yaml, command_allowlist, enforcement before wiring file_gateway/sandbox_runner.

## Deliverables (Design)
- capabilities.yaml (full spec); command_allowlist.yaml; per-agent capability matrix; enforcement ADR. See `.claude-development/designs/`.

## Acceptance
- Spec and ADR approved; MVP24 can implement.

---

# CCW-MVP24 — Capability Policy Enforcement
**Goal:** Deploy capabilities.yaml, command_allowlist.yaml, path_allowlist.yaml; capability_enforcer; wire file_gateway and sandbox_runner.

**Depends on:** MVP23-D.

## Deliverables
- `.claude/policies/capabilities.yaml`, `command_allowlist.yaml`, `path_allowlist.yaml`; `llamacode/core/capability_enforcer.py`; update file_gateway.py and sandbox_runner.py.

## Acceptance
- Read/write and command checks per agent; violations logged.

---

# CCW-MVP24-D — Eval Harness Completion Design (Design)
**Goal:** task_suite.yaml, schedules.yaml, shadow/ and ab/ spec, CBL rung benchmark definitions.

## Deliverables (Design)
- `.claude/eval/task_suite.yaml`, `.claude/eval/schedules.yaml`; spec for shadow/ and ab/ (`.claude-development/designs/eval_shadow_ab_cbl_spec.md`); CBL benchmark files (e.g. `.claude/eval/cbl/`).

## Acceptance
- Suite and schedules present; implementation (MVP25) can build runner and nightly CI.

---

# CCW-MVP25 — Eval Harness Completion
**Goal:** Task suite (core/stress/exploration), schedules, shadow/ and ab/ scaffold, CBL benchmarks, nightly CI step.

**Depends on:** MVP24-D.

## Deliverables
- task_suite.yaml and schedules.yaml (already created); `.claude/eval/shadow/` and `.claude/eval/ab/` or `.llama_runtime/` scaffold; CBL rung benchmark files; nightly CI step.

## Acceptance
- Eval runner uses task_suite; nightly job runs; shadow/ab structure present.

---

# CCW-MVP26 — Security Hardening v1
**Goal:** Input sanitization; budget hard kill (2x); audit log chaining (SHA-256); snapshot secret scan; audit_log.schema.json.

**Depends on:** MVP24.

## Deliverables
- Input sanitization layer; budget circuit breaker (2x kill); audit log chaining; snapshot secret scan; audit_log.schema.json (Report 04 §3).

## Acceptance
- T-001, T-006, T-010 addressed; audit entries cryptographically chained.

---

# CCW-MVP27 — MAPE-K Learning Loop v1
**Goal:** Monitor→Analyze→Plan→Execute; feedback event writer; telemetry→routing adapter; bandit_router consumes feedback.

**Depends on:** MVP25-D.

## Deliverables
- `llamacode/core/mape_k.py`; feedback event writer; telemetry→routing adapter; extend bandit_router.

## Acceptance
- Telemetry feeds routing decisions; feedback schema persisted.

---

# CCW-MVP28 — Full Critics Suite (10 new critics)
**Goal:** 10 additional critics (Performance, Determinism, Regression, Cost, Drift, Dependency, Adversarial, Completeness, Consistency, Accessibility); auto-critics as Python; manual stubs where needed.

**Depends on:** MVP23, MVP22-D.

## Deliverables
- 10 new critic .md in `.claude/agents/critics/`; auto-critics (Cost, Drift, Regression, Determinism, Performance) as Python; manual stubs (Adversarial, Dependency, Completeness, Consistency, Accessibility).

## Acceptance
- All activatable in critic_gates.yaml; output as CriticResult.

---

# CCW-MVP29 — Plugin Runtime v1
**Goal:** Plugin loader, lifecycle, manifest schema v2, compatibility check; load/execute/unload test for one plugin; signature verification stub.

**Depends on:** MVP26-D.

## Deliverables
- `llamacode/plugins/loader.py`; lifecycle manager; plugin_manifest.schema.json v2; compatibility checker; test for one existing plugin; signature stub.

## Acceptance
- One plugin loads, executes, unloads without error.

---

# CCW-MVP30 — CBL Rung Unlock Ceremonies
**Goal:** Formalize CBL position (Rung 1); run Rung 2 ceremony (multi-agent suite); deploy unlock_rules.yaml; rung progress in `.llama_runtime/cbl/`.

**Depends on:** MVP25, MVP23.

## Deliverables
- Document current CBL position (Rung 1); run Rung 2 ceremony; deploy unlock_rules.yaml; rung log in `.llama_runtime/cbl/`.

## Acceptance
- Rung 2 ceremony run; progress traceable.

---

# CCW-MVP31 — Knowledge Graph v1 (SQLite)
**Goal:** SQLite schema for outcome/routing; migration from outcome_ledger.jsonl; query interface; wire bandit_router.

**Depends on:** MVP27-D.

## Deliverables
- SQLite schema; migration script; query interface; bandit_router integration.

## Acceptance
- Routing can use history; ledger migrated.

---

# CCW-MVP32 — Agent Genome & Evolution v1
**Goal:** Agent genome JSON; genome store in `.llama_runtime/genome/`; 2 mutation operators; shadow validation; rollback.

**Depends on:** MVP28-D.

## Deliverables
- Genome format; genome store; prompt variation and threshold adjustment as operators; shadow gate; rollback mechanism.

## Acceptance
- Mutation→shadow→promote cycle testable; rollback works.

---

# CCW-MVP33 — Shadow-Operator Mode v1
**Goal:** `.llama_runtime/shadow/` structure; shadow run runner; comparator; shadow critics (Quality/Cost delta, Consistency, Regression, Stability); promotion rules YAML.

**Depends on:** MVP25.

## Deliverables
- Shadow directory structure; runner script; comparator; shadow critics; promotion_rules.yaml.

## Acceptance
- Shadow run against baseline; comparison report; promotion decision by rules.

---

# CCW-MVP34 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP35 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP36 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP37 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP38 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP39 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP40 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP41 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP42 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP43 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP44 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP45 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP46 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP47 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP48 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP49 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP50 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP51 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP52 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP53 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP54 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP55 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP56 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP57 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP58 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP59 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP60 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP61 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP62 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP63 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP64 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP65 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP66 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP67 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP68 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP69 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP70 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP71 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP72 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP73 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP74 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP75 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP76 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP77 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP78 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP79 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP80 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP81 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP82 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP83 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP84 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP85 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP86 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP87 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP88 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP89 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP90 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP91 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP92 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP93 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP94 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP95 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP96 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP97 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP98 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP99 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP100 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP101 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP102 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP103 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP104 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP105 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP106 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP107 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP108 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP109 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP110 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP111 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP112 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP113 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP114 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP115 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP116 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP117 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP118 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP119 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP120 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP121 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP122 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP123 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP124 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP125 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP126 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP127 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP128 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP129 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP130 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP131 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP132 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP133 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP134 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP135 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP136 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP137 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP138 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP139 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP140 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP141 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP142 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP143 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP144 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP145 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP146 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP147 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP148 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP149 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP150 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP151 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP152 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP153 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP154 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP155 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP156 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP157 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP158 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP159 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP160 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP161 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP162 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP163 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP164 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP165 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP166 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP167 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP168 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP169 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP170 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP171 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP172 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP173 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP174 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP175 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP176 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP177 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP178 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP179 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP180 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP181 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP182 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP183 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP184 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP185 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP186 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP187 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP188 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP189 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP190 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP191 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP192 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP193 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP194 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP195 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP196 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP197 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP198 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP199 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP200 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP201 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP202 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP203 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP204 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP205 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP206 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP207 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP208 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP209 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP210 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP211 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP212 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP213 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP214 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP215 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP216 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP217 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP218 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP219 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP220 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP221 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP222 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP223 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP224 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP225 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP226 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP227 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP228 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP229 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP230 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP231 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP232 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP233 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP234 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP235 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP236 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP237 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP238 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP239 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP240 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP241 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP242 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP243 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP244 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP245 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP246 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP247 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP248 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP249 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP250 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP251 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP252 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP253 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP254 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP255 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP256 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP257 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP258 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP259 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP260 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP261 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP262 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP263 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP264 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP265 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP266 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP267 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP268 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP269 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP270 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP271 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP272 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP273 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP274 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP275 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP276 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP277 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP278 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP279 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP280 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP281 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP282 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP283 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP284 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP285 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP286 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP287 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP288 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP289 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP290 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP291 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP292 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP293 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP294 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP295 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP296 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP297 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP298 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP299 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP300 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP301 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP302 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP303 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP304 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP305 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP306 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP307 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP308 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP309 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP310 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP311 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP312 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP313 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP314 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP315 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP316 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP317 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP318 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP319 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP320 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP321 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP322 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP323 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP324 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP325 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP326 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP327 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP328 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP329 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP330 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP331 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP332 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP333 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP334 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP335 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP336 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP337 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP338 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP339 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP340 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP341 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP342 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP343 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP344 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP345 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP346 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP347 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP348 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP349 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP350 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP351 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP352 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP353 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP354 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP355 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP356 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP357 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP358 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP359 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP360 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP361 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP362 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP363 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP364 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP365 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP366 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP367 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP368 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP369 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP370 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP371 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP372 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP373 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP374 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP375 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP376 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP377 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP378 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP379 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP380 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP381 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP382 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP383 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP384 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP385 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP386 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP387 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP388 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP389 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP390 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP391 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP392 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP393 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP394 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP395 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP396 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP397 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP398 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP399 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP400 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP401 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP402 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message

---

# CCW-MVP403 — General Enhancement
**Goal:** Implement capabilities in the **general** domain as identified by trigger `manual`.

## Deliverables

- Scope (skill IDs / capability gaps addressed):
  - (none specified)
- Schema, example, and Python implementation for each new skill
- Registry entries added to `skills/registry.md`
- `SKILLS` dispatch entries added to `skill_runner.py`

## Acceptance
- All skills listed in scope run end-to-end via skill_runner
- Each skill has schema + example + .py
- Smoke test for each skill returns `status: ok` or `status: error` with clear message
