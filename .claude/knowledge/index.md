# Knowledge Base Index — Python Orchestrator

> Zentrale Wissensbasis für den Librarian Agent.
> Agents fragen den Librarian — dieser Index ist die Grundlage für zielgenaue Lieferung.
> Zuletzt aktualisiert: 2026-02-27

---

## Thematischer Index

### Agent-System & Governance

Dateien, die das `.claude/`-System, Rollen, Prozesse und Governance-Regeln beschreiben.

- `.claude/SYSTEM.md` — Einstiegspunkt, System-Architektur, Unterordner-Referenz
- `.claude/collaboration.md` — Team-Komposition pro Szenario, Workload-Balancing
- `.claude/governance/execution_protocol.md` — Vollständiger Ausführungsflow (Phase 0–5)
- `.claude/governance/escalation_matrix.md` — L0–L5 Eskalationsschwellen
- `.claude/governance/decision_policy.md` — Entscheidungs-Hierarchie mit Beispielen
- `.claude/governance/review_process.md` — Standard Review-Schritte (Collector, Validation)
- `.claude/governance/git_workflow.md` — Commit-Regeln, verbotene Aktionen, Branch-Strategie
- `.claude/governance/ollama_integration.md` — Ollama Workload-System, Modelle, Task-Types
- `.claude/governance/rule_discovery.md` — Wann/wie neue Regeln erkannt und dokumentiert werden
- `.claude/governance/self_improvement.md` — Post-Task-Zyklus, Self-Improvement-Mechanismus
- `.claude/governance/workflow_triggers.md` — Stichwörter (Task:, Review:, Implement:, Archive:, Critics:)
- `.claude/governance/task_archival.md` — Task-Archivierung (BP-005): Ref + Documentation + Index
- `.claude/governance/document_placement.md` — Dokument-Platzierungskorrektur (BP-006)

### Agent-Rollen (Definitionen)

- `.claude/agents/team_lead.md` — Rolle, Verantwortlichkeiten, Task-Brief-Format
- `.claude/agents/designer.md` — Framework-Wächter, Architektur-Konsistenz
- `.claude/agents/specialists.md` — Alle Specialist-Agents, Ollama-First-Pflicht
- `.claude/agents/research.md` — Research Agent, Archivierungs-Workflow
- `.claude/agents/critics/technical.md` — Technical Critic, L3-Aktivierungsschwelle
- `.claude/agents/critics/systemic.md` — Systemic Critic, L4-Aktivierungsschwelle

### Agent-Rollen (Learning Logs)

- `.claude/agents/learning/team_lead.md` — Best Practices, Routing-Entscheide
- `.claude/agents/learning/implementation_agent.md` — Python-Patterns, OllamaUnavailableError, Imports
- `.claude/agents/learning/architecture_agent.md` — Modul-Hierarchie, Dependency-Richtungen, Split-Regeln
- `.claude/agents/learning/documentation_agent.md` — Source-First-Prinzip, Struktur
- `.claude/agents/learning/librarian_agent.md` — Deduplizierung, Cross-References
- `.claude/agents/learning/collector_agent.md` — Akzeptanzkriterien-Prüfung
- `.claude/agents/learning/validation_agent.md` — Edge-Case-Tests, Extremwerte
- `.claude/agents/learning/pattern_recognition_agent.md` — Pattern-Extraktion (mind. 2 Instanzen)
- `.claude/agents/learning/skill_agent.md` — Meta-Beobachter, Routing-Schwächen
- `.claude/agents/learning/critics/technical_critic.md` — Severity-System, Kritik-Philosophie
- `.claude/agents/learning/critics/systemic_critic.md` — Langzeit-Risiken, Komplexitäts-Drift

### Python Projektmuster & Standards

- `.claude/python/architecture.md` — Python-Architektur-Pointer, Modul-Standards
- `.claude/python/README.md` — Python-Subsystem-Übersicht
- `.claude/agents/learning/implementation_agent.md` — Python-Implementierungs-Patterns
- `.claude/agents/learning/architecture_agent.md` — Modul-Hierarchie, Split-Regeln

### Wissens-Infrastruktur

- `.claude/knowledge/architecture.md` — Wissens-Taxonomie (Task/Reference/System Knowledge)
- `.claude/knowledge/routing.md` — Agent+Modell-Mapping pro Task-Typ, Kompositions-Prinzip
- `.claude/knowledge/decisions.md` — Append-only Entscheidungslog (Architektur- & Policy-Entscheide)
- `.claude/knowledge/research_archive_template.md` — Template für Research-Archive-Einträge
- `.claude/knowledge/index.md` — Dieser Index (Librarian Agent Primär-Referenz)

### Performance & Tracking

- `.claude/performance/tracking.md` — Per-Agent Metriken, System-Metriken
- `.claude/performance/log_template.md` — Template für Post-Task Performance-Logs

### Python-Subsysteme (Quellcode)

> **Hinweis:** Diese Dateien liegen im **Projekt-Repository** (z. B. LlamaCode) unter `<PROJECT_ROOT>/src/`.
> Im Ruleset-Archiv selbst sind sie ggf. nicht enthalten.

- `<PROJECT_ROOT>/src/main.py` — Entry point, REPL, CLI args, stdin-pipe
- `<PROJECT_ROOT>/src/orchestrator.py` — Team Lead Logik: classify, route, coordinate
- `<PROJECT_ROOT>/src/workflow.py` — Trigger-Erkennung, Dok-Naming
- `<PROJECT_ROOT>/src/ollama_client.py` — HTTP-Client gegen localhost:11434
- `<PROJECT_ROOT>/src/claude_client.py` — Spawnt claude-CLI-Subprozesse
- `<PROJECT_ROOT>/src/config.py` — Pfade, Modell-Präferenzen, Ollama-Endpoint
- `<PROJECT_ROOT>/src/agents/base.py` — Basis-Agenten-Klasse
- `<PROJECT_ROOT>/src/agents/implementation.py` — Implementation Agent
- `<PROJECT_ROOT>/src/agents/documentation.py` — Documentation Agent
- `<PROJECT_ROOT>/src/agents/validation.py` — Validation Agent
- `<PROJECT_ROOT>/src/agents/librarian.py` — Librarian Agent

### Cross-Session-Gedächtnis

- `<PROJECT_ROOT>/MEMORY.md` (falls im Projekt vorhanden) — Stabile Findings, Architektur-Entscheide, User-Präferenzen (aktuelle SSoT)
- `<PROJECT_ROOT>/Docs/TASKS.md` (falls im Projekt vorhanden) — Trigger-Referenz für Workflow-Stichwörter

### Aktive Tasks

- `<PROJECT_ROOT>/Docs/Tasks/` (falls im Projekt vorhanden) — Aktive Task-Beschreibungen

### Oodle-Quellen (Product / Memory Mesh)

Für Llama Code (formerly Oodle Code) CMD und Task-Kontext (z. B. `<PROJECT_ROOT>/.claude/tasks/<TASK_FILE>.md`):

- `<PROJECT_ROOT>/quellen/oodle/oodle_memory_mesh_v1_protocol_hub_and_spoke.md` — Memory Mesh v1: Hub-and-Spoke-Protokoll, Event-Schema (JSONL), Node/Hub-Layout, Namespaces, Policies, deterministisches Replay, Sync (Push/Pull)
- `<PROJECT_ROOT>/quellen/README.md` — Übersicht aller canonical Oodle-Quellen

---

## Vollständige Datei-Karte

| Datei | Zweck | Typische Requester | Themen-Tags |
|---|---|---|---|
| `.claude/SYSTEM.md` | System-Einstiegspunkt, Unterordner-Referenz, Governance-Prinzipien | Alle Agents | agent-system, governance, einstieg |
| `.claude/collaboration.md` | Team-Komposition pro Szenario, Ollama-Modell-Auswahl | Team Lead, Skill Agent | routing, team-komposition, ollama |
| `.claude/governance/execution_protocol.md` | Phase-0-bis-5-Flow, Übergabe-Protokolle, Parallelisierung | Team Lead | governance, execution, flow |
| `.claude/governance/escalation_matrix.md` | L0–L5 Eskalationsschwellen, schnelle Entscheidungsmatrix | Team Lead, alle Agents | governance, eskalation, entscheidung |
| `.claude/governance/decision_policy.md` | Entscheidungs-Hierarchie mit konkreten Beispielen pro Level | Team Lead, Designer | governance, entscheidung, policy |
| `.claude/governance/review_process.md` | Standard Review-Schritte: Korrektheit, Imports, Integration | Collector, Validation Agent | governance, review, qualität |
| `.claude/governance/git_workflow.md` | Commit-Regeln, verbotene Aktionen, Branch-Strategie | Alle Agents | governance, git, version-control |
| `.claude/governance/ollama_integration.md` | Modelle, Task-Types, Hardware-Setup, Freeze-Protokoll | Team Lead, alle Agents | ollama, modelle, workflow |
| `.claude/governance/rule_discovery.md` | Wann neue Regeln erkannt werden, wie dokumentiert | Pattern Recognition Agent, Team Lead | governance, regeln, patterns |
| `.claude/governance/self_improvement.md` | Post-Task-Analyse, Verbesserungs-Zyklus | Team Lead | governance, self-improvement, performance |
| `.claude/governance/workflow_triggers.md` | Stichwörter: Task:, Review:, Implement:, Archive:, Critics:, Document: | Team Lead | governance, workflow, trigger |
| `.claude/governance/task_archival.md` | BP-005: Task-Archivierung, Ref/Documentation/Index | Team Lead, Librarian, Documentation Agent | governance, archive, tasks |
| `.claude/governance/document_placement.md` | BP-006: Dokument-Platzierungskorrektur, Owner-Rücksprache | Team Lead, alle Agents | governance, document-placement, ownership |
| `.claude/governance/file_ownership.md` | Datei-Ownership-Regeln, Spawn-Prompt-Pflichtinhalt | Alle Agents | governance, ownership, spawn |
| `.claude/governance/model_escalation_policy.md` | Small-first Routing, Oodle→Claude Eskalationsleiter, Trust Modes, QualitySignal | Team Lead, Personaler | governance, routing, escalation |
| `.claude/agents/team_lead.md` | Rolle, Verantwortlichkeiten, Task-Brief-Format | Team Lead | agent-rollen, team-lead |
| `.claude/agents/designer.md` | Framework-Wächter, L2-Review-Pflicht, Python-Modul-Hierarchie | Designer, Team Lead | agent-rollen, designer, architektur |
| `.claude/agents/specialists.md` | Alle Specialist-Agents, Ollama-First-Pflicht | Specialist Agents | agent-rollen, specialists, ollama |
| `.claude/agents/task_compactor.md` | Low-Effort Intake → TasklistSpec (Departments + Pack Hints) | Team Lead, Personaler | agent-rollen, intake, compact |
| `.claude/agents/testops/testops_orchestrator.md` | TestOps Dispatch (light/medium/heavy) + Auto-Delegation | Team Lead, Tester | quality, testops, dispatch |
| `.claude/agents/testops/testrunner_light.md` | Light Triage → FixPlanSpec | TestOps | quality, testops, triage |
| `.claude/agents/testops/testrunner_medium.md` | Medium Triage → FixPlanSpec+Patch Strategy | TestOps | quality, testops, triage |
| `.claude/agents/testops/testrunner_heavy.md` | Heavy Triage → Root Cause + Risk Notes | TestOps | quality, testops, reasoning |
| `.claude/agents/workers/implementation_worker.md` | Standard Worker für Implementierung (Pack+Acceptance) | Team Lead | engineering, worker, implementation |
| `.claude/agents/workers/report_worker.md` | Report+QualitySignal für Routing-Korrekturen | Team Lead, Personaler | docs, reporting, quality |
| `.claude/agents/research.md` | Research Agent Workflow, Archivierungs-Pflicht | Research Agent | agent-rollen, research, archiv |
| `.claude/agents/critics/technical.md` | Technical Critic Rolle, L3-Aktivierung | Technical Critic, Team Lead | critics, technical, performance |
| `.claude/agents/critics/systemic.md` | Systemic Critic Rolle, L4-Aktivierung | Systemic Critic, Team Lead | critics, systemic, governance |
| `.claude/agents/learning/team_lead.md` | Team Lead Best Practices, Routing-Lessons | Team Lead | learning, team-lead |
| `.claude/agents/learning/implementation_agent.md` | Python-Patterns, OllamaUnavailableError, Import-Fehler | Implementation Agent | learning, python, implementation |
| `.claude/agents/learning/architecture_agent.md` | Modul-Hierarchie, Dependency-Richtungen, Split-Schwelle | Architecture Agent, Designer | learning, architektur, module |
| `.claude/agents/learning/documentation_agent.md` | Source-First, keine Vermutungen, Cross-References | Documentation Agent | learning, dokumentation |
| `.claude/agents/learning/librarian_agent.md` | Deduplizierung, Retrieval-Optimierung, Merge-vor-Neu | Librarian Agent | learning, librarian, knowledge |
| `.claude/agents/learning/collector_agent.md` | Akzeptanzkriterien-Prüfung, Konsistenz-Check | Collector Agent | learning, collector, validation |
| `.claude/agents/learning/validation_agent.md` | Extremwerte, Edge-Cases, Report-Format | Validation Agent | learning, validation, testing |
| `.claude/agents/learning/pattern_recognition_agent.md` | 2-Instanzen-Regel, Abstraktionskandidaten | Pattern Recognition Agent | learning, patterns, abstraktion |
| `.claude/agents/learning/skill_agent.md` | Still beobachten, erst bei Muster eingreifen | Skill Agent | learning, skills, meta |
| `.claude/agents/learning/critics/technical_critic.md` | Severity-System, Kritik-Philosophie | Technical Critic | learning, critics, technical |
| `.claude/agents/learning/critics/systemic_critic.md` | Monate-Horizont, Komplexitäts-Drift, Dependency-Creep | Systemic Critic | learning, critics, systemic |
| `.claude/knowledge/architecture.md` | Wissens-Taxonomie (3 Typen), Indexierungs-Regeln | Librarian Agent | knowledge, taxonomie |
| `.claude/knowledge/routing.md` | Agent+Modell-Mapping, L0–L2+ Kompositions-Prinzip | Team Lead, Skill Agent | routing, modelle, agent-auswahl |
| `.claude/knowledge/decisions.md` | Append-only Entscheidungslog: Architektur- & Policy-Entscheide | Team Lead | decisions, architektur, policy |
| `.claude/knowledge/research_archive_template.md` | Template für Research-Archive-Einträge (RES-YYYY-NNN) | Research Agent, Librarian Agent | research, archiv, template |
| `.claude/knowledge/index.md` | Dieser Index — vollständige Datei-Karte | Librarian Agent | index, knowledge, librarian |
| `.claude/performance/tracking.md` | Per-Agent und System-Metriken, Gut/Schlecht-Schwellen | Team Lead, Skill Agent | performance, metriken |
| `.claude/performance/log_template.md` | Performance-Log-Template für abgeschlossene Major Tasks | Team Lead | performance, log, template |
| `<PROJECT_ROOT>/src/main.py` | Entry point: REPL, --task CLI, stdin-pipe | Implementation Agent | python, entry-point, repl |
| `<PROJECT_ROOT>/src/orchestrator.py` | Task-Klassifikation L0–L5, Agent-Routing, Ollama-Guard | Implementation Agent, Architecture Agent | python, orchestration, routing |
| `<PROJECT_ROOT>/src/workflow.py` | Trigger-Erkennung (Task:/Review:/ etc.), Dok-Naming, Docs/-Gerüst | Implementation Agent | python, workflow, trigger |
| `<PROJECT_ROOT>/src/ollama_client.py` | HTTP-Client localhost:11434, 5 task_types, OllamaUnavailableError | Implementation Agent | python, ollama, client |
| `<PROJECT_ROOT>/src/claude_client.py` | Spawnt claude-CLI-Subprozesse, self-contained Prompts | Implementation Agent | python, claude, subprocess |
| `<PROJECT_ROOT>/src/config.py` | Pfade (PROJECT_ROOT, Docs/), Modell-Präferenzen, Ollama-Endpoint | Alle Agents | python, config, pfade |
| `<PROJECT_ROOT>/src/agents/base.py` | Basis-Agenten-Klasse: run(), report() | Implementation Agent | python, agents, basis |
| `<PROJECT_ROOT>/src/agents/implementation.py` | Implementation Agent: Python-Code schreiben/ändern | Implementation Agent | python, agents, implementation |
| `<PROJECT_ROOT>/src/agents/documentation.py` | Documentation Agent: Docs/ erstellen/verbessern | Documentation Agent | python, agents, dokumentation |
| `<PROJECT_ROOT>/src/agents/validation.py` | Validation Agent: Syntax-Check, Tests | Validation Agent | python, agents, validation |
| `<PROJECT_ROOT>/src/agents/librarian.py` | Librarian Agent: Wissensbasis-Lookups | Librarian Agent | python, agents, librarian |
| `<PROJECT_ROOT>/MEMORY.md` | Cross-Session-Gedächtnis: stabile Findings, User-Präferenzen | Alle Agents | memory, kontext, stable |
| `<PROJECT_ROOT>/Docs/TASKS.md` | Trigger-Referenz Übersicht | Team Lead | trigger, workflow |

---

## Themen → Dateien Mapping

### "Ollama-Client / Freeze-Protokoll"

Primäre Quellen:
- `<PROJECT_ROOT>/src/ollama_client.py` — HTTP-Client, OllamaUnavailableError, task_types
- `.claude/governance/ollama_integration.md` — Modelle, Hardware-Routing, Freeze-Protokoll

### "Orchestrator / Task-Klassifikation"

Primäre Quellen:
- `<PROJECT_ROOT>/src/orchestrator.py` — Classify, route, coordinate
- `.claude/governance/escalation_matrix.md` — L0–L5 Schwellen
- `.claude/governance/decision_policy.md` — Wann welches Level
- `.claude/knowledge/routing.md` — Agent+Modell-Mapping

### "Workflow-Trigger / Dok-Naming / Archivierung"

Primäre Quellen:
- `<PROJECT_ROOT>/src/workflow.py` — Trigger-Erkennung und Dispatch
- `.claude/governance/workflow_triggers.md` — Stichwörter, Ablauf, Formate (inkl. Archive:)
- `.claude/governance/task_archival.md` — BP-005 Archivierung nach Task-Abschluss
- `.claude/governance/document_placement.md` — BP-006 Korrektur falscher Ablage
- `<PROJECT_ROOT>/Docs/TASKS.md` (falls im Projekt vorhanden) — Trigger-Kurzreferenz

### "Python-Module / Architektur"

Primäre Quellen:
- `<PROJECT_ROOT>/src/config.py` — Pfade und Konstanten

### "Agent-Rollen / Governance"

Primäre Quellen:
- `.claude/SYSTEM.md` — Überblick aller Rollen und Unterordner
- `.claude/agents/team_lead.md` — Team Lead Rolle
- `.claude/agents/designer.md` — Designer Rolle
- `.claude/agents/specialists.md` — Alle Specialists
- `.claude/agents/research.md` — Research Agent
- `.claude/agents/critics/technical.md` — Technical Critic
- `.claude/agents/critics/systemic.md` — Systemic Critic

Prozesse:
- `.claude/governance/execution_protocol.md` — Vollständiger Flow
- `.claude/governance/escalation_matrix.md` — L0–L5
- `.claude/governance/decision_policy.md` — Wann wer entscheidet

### "Python-Patterns / Best Practices"

Primäre Quellen:

Learning Logs mit Beispielen:
- `.claude/agents/learning/implementation_agent.md` — Python-Implementierungs-Patterns
- `.claude/agents/learning/architecture_agent.md` — Architektur-Entscheide

### "Routing / Modell-Auswahl"

Primäre Quellen:
- `.claude/knowledge/routing.md` — Task → Agent + Modell Mapping
- `.claude/collaboration.md` — Szenarien: neue Python-Funktion, Architektur-Entscheid, etc.
- `.claude/governance/ollama_integration.md` — Modelle: qwen2.5-coder:32b (CPU), phi4:14b (GPU), qwen2.5-coder:14b (GPU)

Regeln:
- `.claude/governance/execution_protocol.md` — Phase 0a Ollama Pre-Briefing
- `.claude/agents/specialists.md` — Ollama-First-Pflicht

### "Spawn-Prompt / Claude-CLI"

Primäre Quellen:
- `<PROJECT_ROOT>/src/claude_client.py` — Subprocess-Spawning
- `.claude/governance/file_ownership.md` — Spawn-Prompt Pflichtinhalt

### "Performance Tracking / Self-Improvement"

Primäre Quellen:
- `.claude/performance/tracking.md` — Metriken-Definitionen
- `.claude/performance/log_template.md` — Log-Template
- `.claude/governance/self_improvement.md` — Post-Task-Zyklus

### "Review / Validation"

Primäre Quellen:
- `.claude/governance/review_process.md` — Standard Review-Schritte
- `.claude/agents/learning/validation_agent.md` — Edge-Cases, Extremwerte
- `.claude/agents/learning/collector_agent.md` — Akzeptanzkriterien-Prüfung

### "Git / Branch-Workflow"

Primäre Quellen:
- `.claude/governance/git_workflow.md` — Commit-Regeln, verbotene Aktionen

---

## Wartungshinweise

**Wann dieser Index aktualisiert werden muss:**
- Neue `.md`-Datei in `.claude/` oder `<PROJECT_ROOT>/Docs/References/` / `<PROJECT_ROOT>/Docs/Plans/` angelegt
- Neue `<PROJECT_ROOT>/src/`-Datei hinzugefügt
- Bestehende Datei inhaltlich grundlegend geändert (neues Thema, neue Zuständigkeit)
- Neuer Agent-Typ hinzugefügt

**Wer aktualisiert:**
- Librarian Agent — nach Abschluss jeder Task, die Knowledge-relevante Dateien erstellt oder ändert

**Format-Regel:**
- Tabellen-Spalten nicht kürzen — vollständige Pfade in Spalte 1
- Themen-Tags in Spalte 4: Englisch oder Deutsch konsistent, lowercase, Bindestriche statt Leerzeichen

---

## Contracts & Schemas

| Datei | Zweck | Typische Requester | Themen-Tags |
|---|---|---|---|
| `.claude/contracts/SPEC_SHEET.md` | Kurzliste zentraler Specs, Trust Modes, Pipeline | Team Lead, alle Agents | contracts, specs |
| `.claude/contracts/schemas/*.json` | Vollständige JSON-Schemas (~95 Dateien) | Implementation, Skill Runner | contracts, schemas |

---

## Ops / Observability

| Datei | Zweck | Typische Requester | Themen-Tags |
|---|---|---|---|
| `.claude/agents/qualitysignal_aggregator.md` | QualitySignal-Aggregation | Team Lead, Personaler | ops, quality |
| `.claude/agents/escalation_controller.md` | Eskalations-Steuerung | Team Lead | ops, escalation |
| `.claude/agents/operations/department_lead_ops_ledger.md` | Ops Ledger (Department Lead) | Ops Agents | ops, ledger |
| `.claude/agents/operations/skill_scout.md` | Skill Discovery | Team Lead, Meta Agent | skills, discovery |
| `.claude/governance/routing_matrix.md` | Routing-Matrix | Team Lead | routing, ops |
| `.claude/governance/skill_scout_triggers.md` | Skill-Scout-Trigger | Team Lead | skills, triggers |
| `.claude/governance/planning_policy.md` | Planning-Policy | Team Lead, Planning | planning, governance |
| `.claude/governance/experiment_budget.md` | Experiment-Budget | Team Lead | ops, experiment |
| `.claude/governance/prompt_debt_policy.md` | Prompt-Debt-Policy | Documentation Agent | docs, prompt-debt |
| `.claude/governance/deep_oodle_mode.md` | Deep-Oodle-Modus | Team Lead | ollama, routing |
| `.claude/governance/feedback_policy.md` | Feedback-Policy | Team Lead, Report Worker | feedback, ops |
| `.claude/governance/no_llm_mode.md` | No-LLM-Modus | Team Lead | governance, fallback |
| `.claude/governance/policy_gatekeeper.md` | Policy-Gatekeeper | Team Lead | governance, policy |
| `.claude/governance/paths_and_placeholders.md` | Pfade und Platzhalter | Alle Agents | paths, config |
| `.claude/governance/naming_canon.md` | Namenskonventionen | Alle Agents | governance, naming |
| `.claude/governance/artifacts_and_paths.md` | Artefakte und Pfade | Implementation Agent | artifacts, paths |
| `.claude/governance/message_triad_protocol.md` | Message-Triad-Protokoll | Team Lead, Input Tasks | input, triad |
| `.claude/governance/path_semantics.md` | Pfad-Semantik | Alle Agents | paths, governance |
| `.claude/skills/registry.md` | Skill-Registry (Katalog aller Skills) | Skill Scout, Team Lead | skills, registry |
| `.claude/skills/playbooks/` | Playbooks (z. B. qa_campaign, documentation_pipeline) | Team Lead, Agents | skills, playbooks |
| `.claude/skills.md` | Pointer auf Registry + Playbooks | Alle Agents | skills, pointer |
| `.claude/tools/menus/planning_policy_menu.py` | Planning-Policy-Menü | Team Lead | planning, tools |
| `.claude/tools/menus/feedback_policy_menu.py` | Feedback-Policy-Menü | Team Lead | feedback, tools |
| `.claude/tools/skills/edge_case_selector.py` | Edge-Case-Selector Skill | TestOps, Tester | skills, testing |
| `.claude/tools/skills/decision_feedback.py` | Decision-Feedback Skill | Team Lead | skills, feedback |
| `.claude/tools/skills/deliberation_pack_build.py` | Deliberation-Pack-Builder | Team Lead | skills, deliberation |
| `.claude/tools/skills/outcome_event_generate.py` | Outcome-Event-Generator | Ops, Report Worker | skills, outcome |
| `.claude/contracts/schemas/idea_set_spec.schema.json` | IdeaSetSpec Schema | Ideation Tasks | contracts, ideation |
| `.claude/contracts/schemas/plan_diff_spec.schema.json` | PlanDiffSpec Schema | Planning | contracts, planning |
| `.claude/contracts/schemas/deliberation_pack_spec.schema.json` | DeliberationPackSpec Schema | Team Lead | contracts, deliberation |
| `.claude/contracts/schemas/message_triad_spec.schema.json` | MessageTriadSpec Schema | Input Tasks | contracts, triad |
| `.claude/tasks/ideation/` | Ideation-Tasks | Team Lead | tasks, ideation |
| `.claude/tasks/deep/` | Deep-Tasks | Team Lead | tasks, deep |
| `.claude/tasks/ops/080_AUTOTUNE_POSTRUN.md` | Autotune Post-Run | Ops | tasks, autotune |
| `.claude/tasks/ops/090_CONTRACT_DRIFT_SENTINEL.md` | Contract-Drift-Sentinel | Ops, QA | tasks, drift |
| `.claude/tasks/ops/100_COMMAND_DRYRUN.md` | Command Dry-Run | Ops | tasks, dryrun |
| `.claude/tasks/governance/010_POLICY_GATE_CHECK.md` | Policy-Gate-Check | Team Lead | tasks, governance |
| `.claude/tasks/evidence/000_EVIDENCE_ROUTER.md` | Evidence-Router | Research, Evidence | tasks, evidence |
| `.claude/tasks/routing/090_AUTOTUNE_PATCH_PACK.md` | Autotune-Patch-Pack | Ops, Routing | tasks, routing |
| `.claude/tasks/runbook/000_ONE_BUTTON_RUNBOOK.md` | One-Button-Runbook | Ops | tasks, runbook |
| `.claude/tasks/input/` | Input-/Triad-Tasks | Team Lead | tasks, input |
| `.claude/tasks/input/030_TRIAD_LINT.md` | Triad-Lint | Input Pipeline | tasks, triad |
| `.claude/knowledge/localAIs.md` | Lokale AI-Inventur (Ollama-Modelle etc.) | Team Lead, Routing | knowledge, ollama |
