# Agent Engineering System — Python Orchestrator

> **Single Source of Truth** for all agents, processes, and governance rules.
> This directory fully replaces `Docs/Rules/` (deprecated).

---

## Mission

**Clockwork-only:** `.claude/` contains methodology + deterministic tooling only. Project code/docs live outside this folder.

The Python Orchestrator is a console application for autonomous Ollama/Claude agent orchestration.
The system implements the governance framework from `.claude/` in Python and can operate autonomously.
Bidirectional collaboration: Claude Code calls the app via Bash; the app spawns Claude sub-agents via the `claude` CLI.

___

# Claude System — Clockwork (formerly Llama Code / Oodle Code)

This repository uses **Clockwork governance**.

## Start here
- `ROADMAP.md` (milestones)
- `ARCHITECTURE.md` (system design)
- `MODEL_POLICY.md` (tiers + triggers)
- `QUALITY_TRACKING.md` (telemetry + stats)

## How to work (Claude Code)
Run tasks in `.claude/tasks/`:

1) `tasks/000_MASTER_PROMPT.md`
2) `tasks/input/000_BUILD_MESSAGE_TRIAD.md`
3) `tasks/planning/000_PLAN_COMPACTION_V2.md`
4) `tasks/planning/010_PLAN_LINT_RUN.md`
5) `tasks/governance/010_POLICY_GATE_CHECK.md`
6) `tasks/qa/000_RUN_QA_GATE.md`
7) `tasks/runbook/000_ONE_BUTTON_RUNBOOK.md`

## Hard constraints
- No autonomous tool execution by default.
- Local-first; external providers only with explicit opt-in and Chef gate.
- Keep context small; use packs and summaries.

---

## System Architecture

```
Team Lead (Strategic)
├── Designer / Architecture Agent (Framework Authority)
├── Specialist Agents (Tactical)
│   ├── Implementation Agent
│   ├── Documentation Agent
│   ├── Librarian Agent
│   ├── Collector Agent
│   ├── Validation Agent
│   └── Pattern Recognition Agent
├── Research Agent (Knowledge)
└── Adversarial Critics (Quality Gates)
    ├── Technical Critic
    └── Systemic Critic
```

---

## Subdirectory Reference

| Directory | Contents |
|---|---|
| `agents/` | Role definitions: Team Lead, Designer, Specialists, Research |
| `agents/critics/` | Technical + Systemic Critic |
| `governance/` | Execution Protocol, Decision Policy, Escalation, Review, Git Workflow, Workflow Triggers, Task Archival (BP-005), Document Placement (BP-006), Rule Discovery, Ollama Integration (10 files) |
| `tools/` | `ollama_brief.py` — local LLM pre-briefing for agents |
| `knowledge/` | Knowledge architecture, research archive template |
| `performance/` | Performance tracking, log template |
| `python/` | Python architecture rules, project patterns |

---

## Governance Principles

- No silent architecture changes.
- Core decisions require user confirmation.
- Every major task updates the knowledge base.
- Performance metrics are logged and reviewed.
- Framework consistency is enforced by the Designer/Architecture Agent.

---

## Autonomy Rules

| Area | Autonomy |
|---|---|
| Implementation | Autonomous |
| Architecture | Confirmation required |
| Framework changes | Designer review mandatory |
| Changing escalation thresholds | Systemic Critic + User |

---

## Project Structure (`.project/`)

Project-operational files for the current project live in `.project/`.
When deploying Clockwork on another project, these move to that project's root.

```
.project/
  MEMORY.md                ← Cross-session knowledge (SSoT)
  ARCHITECTURE.md          ← System design
  ROADMAP.md               ← Milestones
  MODEL_POLICY.md          ← Model tier overrides
  QUALITY_TRACKING.md      ← Telemetry + stats
  memory/                  ← Team Lead cross-session context files
  Docs/
    Plans/                 ← Task descriptions + implementation plans
    Review/                ← Validation reports
    Critics/               ← Critic outputs
    Documentation/         ← Technical docs
    References/            ← Archived reference documents
    Tutorials/             ← Guides, How-Tos
```

**Agent write permissions:**

| Agent | Write permissions |
|---|---|
| Documentation Agent | `.project/Docs/Documentation/`, `.project/Docs/Tutorials/` |
| Librarian Agent | `.project/Docs/References/`, `.claude/knowledge/` |
| Collector Agent | Validation across all `.project/Docs/` |
| Validation Agent | `.project/Docs/Review/` |
| Critics | `.project/Docs/Critics/` |
| Team Lead / Designer | `.claude/governance/`, `.claude/agents/`, `.claude/python/`, `.project/Docs/Plans/`, `.project/memory/` |

---

## Quick Links

- Execution Flow → `governance/execution_protocol.md`
- Ollama Briefing → `governance/ollama_integration.md`
- Escalation → `governance/escalation_matrix.md`
- Decision Policy → `governance/decision_policy.md`
- Git Workflow → `governance/git_workflow.md`
- Workflow Triggers (Task:/Review:/Implement:) → `governance/workflow_triggers.md`
- Rule Discovery → `governance/rule_discovery.md`
- Python Patterns → `python/patterns.md`
- Python Architecture → `python/architecture.md`
- Agent Roles → `agents/specialists.md`

## Operational defaults (v17.x)

- **Message Triad input workflow:** build a `MessageTriadSpec` first (`tasks/input/000_BUILD_MESSAGE_TRIAD.md`), then work from `work_brief`.
- **Fallback order:** work_brief → translation → source (original).
- **Hard STOP:** if Drift Sentinel FAILs, stop and fix drift before proceeding.
- **Policy:** use `policy_gatekeeper` to decide if deep reasoning / creative_feedback / rebuild / experiments are allowed.
- **Deep reasoning:** only use Deep Oodle with a Deliberation Pack built by `deliberation_pack_build`.

## Operational defaults (v17.6 additions)

- **PR-blocking QA:** run `qa_gate` before risky work (policy: `governance/qa_gate_policy.md`).
- **Evidence bundles:** build `evidence_bundle_build` outputs for reproducible runs (policy: `governance/evidence_bundle_policy.md`).
- **Security redaction:** redact evidence before sharing (`security_redactor`, policy: `governance/security_redaction_policy.md`).
- **Budgeting:** use `budget_router` for deterministic tier selection (`governance/budgeting_policy.md`).
- **Topology checks:** verify agent hierarchy with `team_topology_verify`.
- **Docs SSoT:** verify backticked path references with `doc_ssot_resolver`.
- **Release cut:** use `release_cut` to generate a deterministic evidence pack (no publishing).

## Operational defaults (v17.7 additions)

- **Docs tool-first:** persist documentation via `doc_write` / `tutorial_write` (diffs for review).
- **Docs lint review:** run `doc_review` after doc updates to catch structural issues early.
- **Baseline compare:** use `repo_compare` for Claude Code ↔ Clockwork deltas (writes a compare report).
- **Docs pipeline:** follow `skills/playbooks/documentation_pipeline.md` for complete doc sets.

## Conventions

- **Product code origin:** application/plugin source files live in `claudeclockwork/` (see `policies/SRC_ORIGIN_RULE.md` — note: policy references `src/` which is a stale path; `claudeclockwork/` is the actual package).

## Performance Budgeting
- Token budgeting is **enabled by default** (see `.claude/config/performance_budgeting.yaml`).
- Toggle: `performance_toggle` (Team Lead may disable if too expensive).
- Export at end: `performance_finalize`.
