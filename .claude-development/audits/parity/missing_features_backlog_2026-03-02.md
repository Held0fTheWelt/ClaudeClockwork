# Missing Features Backlog — 2026-03-02

_Generated: 2026-03-02 by parity_scan_and_mvp_planner_

Items are listed in MVP order. Priorities are not assigned in this implementation.

## GAP Items (no evidence found)

- **CCW-MVP02** (Deterministic Skill Framework v1): `skills/registry.md`
- **CCW-MVP03** (Agent Layer v1 (Prompts + Roles + Routing Policy Stub)): no deliverables declared
- **CCW-MVP04** (Documentation Ops v1 (Write/Review/Index)): no deliverables declared
- **CCW-MVP05** (Governance & Policy Enforcement v1): no deliverables declared
- **CCW-MVP08** (Parity Scan Skill + MVP Pre-Planning (Clockwork-only)): `.claude-development/audits/parity/parity_matrix_<YYYY-MM-DD>.md`, `.claude-development/audits/parity/missing_features_backlog_<YYYY-MM-DD>.md`, `.claude-development/milestones/M1_parity_followup_plan_<YYYY-MM-DD>.md`, `.claude-development/audits/audit_cadence.md`
- **CCW-MVP09** (Parity Follow-up M1: Routing & Model Selection (Design MVP)): no deliverables declared
- **CCW-MVP10** (QA Gates & CI v1 (Gate definition + enforcement)): no deliverables declared
- **CCW-MVP11** (Eval Harness / Golden Tests v1): no deliverables declared
- **CCW-MVP12** (Telemetry & Feedback Loop v1): no deliverables declared

## PARTIAL Items (some evidence missing)

- **CCW-MVP07** (Milestone System v1 (`.claude-development/` scaffolding)): missing `.claude-development/audits/logs/audit_log_<YYYY-MM-DD>.md`
- **CCW-MVP13** (Cleaning Suite Completion (Ops / Repo Health)): missing `contracts/schemas/cleanup_apply_report.schema.json`, `repo_clean_report.schema.json`, `code_clean_report.schema.json`, `skill_runner.py`, `contracts/examples/cleanup_apply.skill_request.example.json`, `contracts/examples/repo_clean.skill_request.example.json`, `contracts/examples/code_clean.skill_request.example.json`, `skills/registry.md`, `skill_runner.py`, `addons/map.yaml`, `SKILL_HOWTO.md`
- **CCW-MVP14** (Archive & Prompt Evolution Completion (Packaging / Shadow Prompts)): missing `contracts/schemas/last_train_report.schema.json`, `shadow_prompt_report.schema.json`, `last_train.py`, `shadow_prompt.py`, `last_train_report.json`, `last_train_report.json`, `contracts/examples/last_train.skill_request.example.json`, `last_train_report.schema.json`, `last_train_summary.schema.json`, `shadow_prompt_report.json`, `shadow_prompt_report.json`, `contracts/examples/shadow_prompt.skill_request.example.json`, `contracts/schemas/shadow_prompt_triage.schema.json`, `skills/registry.md`, `skill_runner.py`, `addons/map.yaml`, `SKILL_HOWTO.md`
- **CCW-MVP15** (PDF Quality Skill (DocForge PDF Pipeline)): missing `pdf_export.py`, `skill_runner.py`, `contracts/schemas/pdf_quality_request.schema.json`, `contracts/examples/pdf_quality.skill_request.example.json`, `skills/registry.md`, `contracts/schemas/pdf_export_request.schema.json`, `contracts/examples/pdf_export.skill_request.example.json`, `pdf_export.py`, `addons/map.yaml`, `skills/registry.md`, `skill_runner.py`, `SKILL_HOWTO.md`, `python .claude/tools/skills/skill_runner.py --in .claude/contracts/examples/pdf_quality.skill_request.example.json --out /tmp/out.json`
- **CCW-MVP16** (Parity Scan Planner Implementation + Registry Integrity (Meta / Audit)): missing `contracts/schemas/parity_scan_and_mvp_planner.schema.json`, `contracts/examples/parity_scan_and_mvp_planner_example.json`, `skill_runner.py`, `parity_matrix_<date>.md`, `missing_features_backlog_<date>.md`, `skill_runner.py`, `skills/registry.md`, `contracts/schemas/idea_dedupe_spec.schema.json`, `contracts/examples/idea_dedupe.skill_request.example.json`, `skill_runner.py`, `SKILL_HOWTO.md`, `python .claude/tools/skills/skill_runner.py --in .claude/contracts/examples/parity_scan_and_mvp_planner_example.json --out /tmp/parity_out.json`, `parity_matrix_*.md`, `python .claude/tools/skills/skill_runner.py --in .claude/contracts/examples/hello_example.json --out /tmp/hello_out.json`
- **CCW-MVP17** (Clockwork Invariants + CI Gate + Integration Tests (Infrastructure / P0-P1)): missing `outcome_ledger_append.py`, `route_autotune_suggest.py`, `route_profile_update.py`, `route_profile_patch_pack.py`, `MEMORY.md`, `gate.sh`, `pytest tests/test_integration_pipeline.py`
- **CCW-MVP18** (Adaptive Routing & Telemetry Feedback Loop (Routing / Intelligence)): missing `llamacode/core/bandit_router.py`, `llamacode/core/bandit_router.py`, `outcome_ledger.jsonl`, `contracts/schemas/bandit_routing_decision.schema.json`, `contracts/examples/bandit_routing_decision.example.json`, `.claude-performance/events/*.jsonl`, `telemetry_summary.json`, `contracts/schemas/telemetry_summary.schema.json`, `contracts/examples/telemetry_summarize.skill_request.example.json`, `skills/registry.md`, `skill_runner.py`, `bandit_router.py`, `python .claude/tools/skills/skill_runner.py --in .claude/contracts/examples/telemetry_summarize.skill_request.example.json --out /tmp/tel_out.json`
- **CCW-MVP19** (Meta-Tooling: QA Gate Extension + Addon CI + skill_runner Hygiene (Tooling / P1-P2)): missing `skill_runner.py`, `qa_gate.py`, `registry.md`, `addons/map.yaml`, `scripts/tag_stub_skills.py`, `skill_runner.py`, `scripts/validate_addons.py`, `scripts/validate_addons.py`, `addons/map.yaml`, `SKILL_HOWTO.md`, `scripts/validate_addons.py`, `python scripts/validate_addons.py`
- **CCW-MVP20** ("Create MVP" Skill (Autonomous MVP Generation)): missing `.claude-development/audits/logs/audit_log_<date>.md`
- **CCW-MVP21** (Clockwork Versioning (Version Bumps + Changelog + Release Tags)): missing `17.8.0`, `.claude/governance/versioning_policy.md`
