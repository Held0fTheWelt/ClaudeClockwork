# Agent Engineering System — Python Orchestrator

> **Single Source of Truth** für alle Agents, Prozesse und Governance-Regeln.
> Dieses Verzeichnis ersetzt vollständig `Docs/Rules/` (deprecated).

---

## Mission

**Clockwork-only:** `.claude/` contains methodology + deterministic tooling only. Project code/docs live outside this folder.

Python Orchestrator ist eine Konsolenanwendung für autonome Ollama/Claude-Agenten-Orchestrierung.
Das System implementiert das Governance-Framework aus `.claude/` in Python und kann autonom arbeiten.
Bidirektionale Zusammenarbeit: Claude Code ruft die App via Bash, die App spawnt Claude-Subagenten via `claude`-CLI.

___

# Claude System — Llama Code (formerly Oodle Code) CMD

This repository uses **Oodle-first governance**.

## Start here
- `OODLE.md` (product spec)
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


## System-Architektur

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

## Unterordner-Referenz

| Verzeichnis | Inhalt |
|---|---|
| `agents/` | Rollen-Definitionen: Team Lead, Designer, Specialists, Research |
| `agents/critics/` | Technical + Systemic Critic |
| `governance/` | Execution Protocol, Decision Policy, Escalation, Review, Git Workflow, Workflow Triggers, Task Archival (BP-005), Document Placement (BP-006), Rule Discovery, Ollama Integration (10 files) |
| `tools/` | `ollama_brief.py` — Lokales LLM Pre-Briefing für Agents |
| `knowledge/` | Knowledge Architecture, Research Archive Template |
| `performance/` | Performance Tracking, Log Template |
| `python/` | Python-Architekturregeln, Projektmuster |

---

## Governance-Prinzipien

- Keine stillen Architekturänderungen.
- Core-Entscheidungen erfordern User-Bestätigung.
- Jede Major Task aktualisiert das Wissen.
- Performance-Metriken werden protokolliert und reviewt.
- Framework-Konsistenz wird vom Designer/Architecture Agent durchgesetzt.

---

## Autonomie-Regeln

| Bereich | Autonomie |
|---|---|
| Implementierung | Autonom |
| Architektur | Bestätigung erforderlich |
| Framework-Änderungen | Designer-Review obligatorisch |
| Eskalationsschwellen ändern | Systemic Critic + User |

---

## Docs/ Zielstruktur

```
Docs/
  TASKS.md                 ← Trigger-Referenz
  Tasks/                   ← Aktive Tasks
  Plans/                   ← Implementierungspläne
  Review/                  ← Reviews + Qualitätsbewertungen
  Critics/                 ← Critics-Outputs, Systemkritiken
  References/              ← Architektur-Referenzen
  Documentation/           ← Technische Docs
  Tutorials/               ← Guides, How-Tos
```

**Agent-Schreibrechte:**

| Agent | Schreibrechte |
|---|---|
| Documentation Agent | `Docs/Documentation/`, `Docs/Tutorials/` |
| Librarian Agent | `Docs/References/`, `.claude/knowledge/` |
| Collector Agent | Validierung quer über alle Docs/ |
| Validation Agent | `Docs/Review/` |
| Critics | `Docs/Critics/` |
| Team Lead / Designer | `.claude/governance/`, `.claude/agents/`, `.claude/python/` |

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

- **German narrative input**: build a **Message Triad** first (`MessageTriadSpec`), then work from `work_brief`.
- **Fallback order**: work_brief → translation → source (original).
- **Hard STOP**: if Drift Sentinel FAILs, stop and fix drift before proceeding.
- **Policy**: use `policy_gatekeeper` to decide if deep_oodle / creative_feedback / rebuild / experiments are allowed.
- **Deep reasoning**: only use Deep Oodle with a Deliberation Pack built by `deliberation_pack_build`.

## Operational defaults (v17.6 additions)

- **PR-blocking QA**: run `qa_gate` before risky work (policy: `governance/qa_gate_policy.md`).
- **Evidence bundles**: build `evidence_bundle_build` outputs for reproducible runs (policy: `governance/evidence_bundle_policy.md`).
- **Security redaction**: redact evidence before sharing (`security_redactor`, policy: `governance/security_redaction_policy.md`).
- **Budgeting**: use `budget_router` for deterministic tier selection (`governance/budgeting_policy.md`).
- **Topology checks**: verify agent hierarchy with `team_topology_verify`.
- **Docs SSoT**: verify backticked path references with `doc_ssot_resolver`.
- **Release cut**: use `release_cut` to generate a deterministic evidence pack (no publishing).

## Operational defaults (v17.7 additions)

- **Docs tool-first**: persist documentation via `doc_write` / `tutorial_write` (diffs for review).
- **Docs lint review**: run `doc_review` after doc updates to catch structural issues early.
- **Baseline compare**: use `repo_compare` for Claude Code ↔ Llama Code deltas (writes a compare report).
- **Docs pipeline**: follow `skills/playbooks/documentation_pipeline.md` for complete doc sets.

## Conventions

- **Product code origin:** all application/plugin source files MUST live under `src/` (see `policies/SRC_ORIGIN_RULE.md`).

## Performance Budgeting
- Token budgeting is **enabled by default** (see `.claude/config/performance_budgeting.yaml`).
- Toggle: `performance_toggle` (TeamLead may disable if too expensive).
- Export at end: `performance_finalize`.
