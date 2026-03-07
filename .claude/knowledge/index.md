# Knowledge Base Index — Python Orchestrator

> Central knowledge base for the Librarian Agent.
> Agents query the Librarian — this index is the foundation for targeted delivery.
> Last updated: 2026-02-27

---

## Thematic Index

### Agent System & Governance

Files describing the `.claude/` system, roles, processes, and governance rules.

- `.claude/SYSTEM.md` — Entry point, system architecture, subfolder reference
- `.claude/collaboration.md` — Team composition per scenario, workload balancing
- `.claude/governance/execution_protocol.md` — Complete execution flow (Phase 0–5)
- `.claude/governance/escalation_matrix.md` — L0–L5 escalation thresholds
- `.claude/governance/decision_policy.md` — Decision hierarchy with examples
- `.claude/governance/review_process.md` — Standard review steps (Collector, Validation)
- `.claude/governance/git_workflow.md` — Commit rules, forbidden actions, branch strategy
- `.claude/governance/ollama_integration.md` — Ollama workload system, models, task types
- `.claude/governance/rule_discovery.md` — When/how new rules are recognized and documented
- `.claude/governance/self_improvement.md` — Post-task cycle, self-improvement mechanism
- `.claude/governance/workflow_triggers.md` — Keywords (Task:, Review:, Implement:, Archive:, Critics:)
- `.claude/governance/task_archival.md` — Task archival (BP-005): Ref + Documentation + Index
- `.claude/governance/document_placement.md` — Document placement correction (BP-006)

### Agent Roles (Definitions)

- `.claude/agents/team_lead.md` — Role, responsibilities, Task Brief format
- `.claude/agents/designer.md` — Framework guardian, architecture consistency
- `.claude/agents/specialists.md` — All Specialist agents, Ollama-First obligation
- `.claude/agents/research.md` — Research Agent, archival workflow
- `.claude/agents/critics/technical.md` — Technical Critic, L3 activation threshold
- `.claude/agents/critics/systemic.md` — Systemic Critic, L4 activation threshold

### Agent Roles (Learning Logs)

- `.claude/agents/learning/team_lead.md` — Best practices, routing decisions
- `.claude/agents/learning/implementation_agent.md` — Python patterns, OllamaUnavailableError, imports
- `.claude/agents/learning/architecture_agent.md` — Module hierarchy, dependency directions, split rules
- `.claude/agents/learning/documentation_agent.md` — Source-first principle, structure
- `.claude/agents/learning/librarian_agent.md` — Deduplication, cross-references
- `.claude/agents/learning/collector_agent.md` — Acceptance criteria checking
- `.claude/agents/learning/validation_agent.md` — Edge case tests, extreme values
- `.claude/agents/learning/pattern_recognition_agent.md` — Pattern extraction (min. 2 instances)
- `.claude/agents/learning/skill_agent.md` — Meta-observer, routing weaknesses
- `.claude/agents/learning/critics/technical_critic.md` — Severity system, critique philosophy
- `.claude/agents/learning/critics/systemic_critic.md` — Long-term risks, complexity drift

### Python Project Patterns & Standards

- `.claude/python/architecture.md` — Python architecture pointer, module standards
- `.claude/python/README.md` — Python subsystem overview
- `.claude/agents/learning/implementation_agent.md` — Python implementation patterns
- `.claude/agents/learning/architecture_agent.md` — Module hierarchy, split rules

### Knowledge Infrastructure

- `.claude/knowledge/architecture.md` — Knowledge taxonomy (Task/Reference/System Knowledge)
- `.claude/knowledge/routing.md` — Agent+model mapping per task type, composition principle
- `.claude/knowledge/decisions.md` — Append-only decision log (architecture & policy decisions)
- `.claude/knowledge/research_archive_template.md` — Template for research archive entries
- `.claude/knowledge/index.md` — This index (Librarian Agent primary reference)

### Performance & Tracking

- `.claude/performance/tracking.md` — Per-agent metrics, system metrics
- `.claude/performance/log_template.md` — Template for post-task performance logs

### Python Subsystems (Deployment Target)

> **Note:** These files don't exist in the Clockwork repo. They are created in the target project under `src/` when Clockwork is deployed there.

- `src/main.py` — Entry point, REPL, CLI args, stdin pipe
- `src/orchestrator.py` — Team Lead logic: classify, route, coordinate
- `src/workflow.py` — Trigger recognition, doc naming
- `src/ollama_client.py` — HTTP client against localhost:11434
- `src/claude_client.py` — Spawns claude-CLI subprocesses
- `src/config.py` — Paths, model preferences, Ollama endpoint
- `src/agents/base.py` — Base agent class
- `src/agents/implementation.py` — Implementation Agent
- `src/agents/documentation.py` — Documentation Agent
- `src/agents/validation.py` — Validation Agent
- `src/agents/librarian.py` — Librarian Agent

### Cross-Session Memory

- `.project/MEMORY.md` — Stable findings, architecture decisions, user preferences (current SSoT)

### Active Plans & Tasks

- `.project/Docs/Plans/` — Active task descriptions and plans

---

## Complete File Map

| File | Purpose | Typical Requesters | Topic Tags |
|---|---|---|---|
| `.claude/SYSTEM.md` | System entry point, subfolder reference, governance principles | All agents | agent-system, governance, entry |
| `.claude/collaboration.md` | Team composition per scenario, Ollama model selection | Team Lead, Skill Agent | routing, team-composition, ollama |
| `.claude/governance/execution_protocol.md` | Phase 0-to-5 flow, handoff protocols, parallelization | Team Lead | governance, execution, flow |
| `.claude/governance/escalation_matrix.md` | L0–L5 escalation thresholds, quick decision matrix | Team Lead, all agents | governance, escalation, decision |
| `.claude/governance/decision_policy.md` | Decision hierarchy with concrete examples per level | Team Lead, Designer | governance, decision, policy |
| `.claude/governance/review_process.md` | Standard review steps: correctness, imports, integration | Collector, Validation Agent | governance, review, quality |
| `.claude/governance/git_workflow.md` | Commit rules, forbidden actions, branch strategy | All agents | governance, git, version-control |
| `.claude/governance/ollama_integration.md` | Models, task types, hardware setup, freeze protocol | Team Lead, all agents | ollama, models, workflow |
| `.claude/governance/rule_discovery.md` | When new rules are recognized, how documented | Pattern Recognition Agent, Team Lead | governance, rules, patterns |
| `.claude/governance/self_improvement.md` | Post-task analysis, improvement cycle | Team Lead | governance, self-improvement, performance |
| `.claude/governance/workflow_triggers.md` | Keywords: Task:, Review:, Implement:, Archive:, Critics:, Document: | Team Lead | governance, workflow, trigger |
| `.claude/governance/task_archival.md` | BP-005: Task archival, Ref/Documentation/Index | Team Lead, Librarian, Documentation Agent | governance, archive, tasks |
| `.claude/governance/document_placement.md` | BP-006: Document placement correction, owner consultation | Team Lead, all agents | governance, document-placement, ownership |
| `.claude/governance/file_ownership.md` | File ownership rules, spawn prompt required content | All agents | governance, ownership, spawn |
| `.claude/governance/model_escalation_policy.md` | Small-first routing, Oodle→Claude escalation ladder, trust modes, QualitySignal | Team Lead, Personaler | governance, routing, escalation |
| `.claude/agents/team_lead.md` | Role, responsibilities, Task Brief format | Team Lead | agent-roles, team-lead |
| `.claude/agents/designer.md` | Framework guardian, L2 review obligation, Python module hierarchy | Designer, Team Lead | agent-roles, designer, architecture |
| `.claude/agents/specialists.md` | All Specialist agents, Ollama-First obligation | Specialist Agents | agent-roles, specialists, ollama |
| `.claude/agents/task_compactor.md` | Low-effort intake → TasklistSpec (Departments + Pack Hints) | Team Lead, Personaler | agent-roles, intake, compact |
| `.claude/agents/testops/testops_orchestrator.md` | TestOps dispatch (light/medium/heavy) + auto-delegation | Team Lead, Tester | quality, testops, dispatch |
| `.claude/agents/testops/testrunner_light.md` | Light triage → FixPlanSpec | TestOps | quality, testops, triage |
| `.claude/agents/testops/testrunner_medium.md` | Medium triage → FixPlanSpec+Patch Strategy | TestOps | quality, testops, triage |
| `.claude/agents/testops/testrunner_heavy.md` | Heavy triage → Root Cause + Risk Notes | TestOps | quality, testops, reasoning |
| `.claude/agents/workers/implementation_worker.md` | Standard worker for implementation (Pack+Acceptance) | Team Lead | engineering, worker, implementation |
| `.claude/agents/workers/report_worker.md` | Report+QualitySignal for routing corrections | Team Lead, Personaler | docs, reporting, quality |
| `.claude/agents/research.md` | Research Agent workflow, archival obligation | Research Agent | agent-roles, research, archive |
| `.claude/agents/critics/technical.md` | Technical Critic role, L3 activation | Technical Critic, Team Lead | critics, technical, performance |
| `.claude/agents/critics/systemic.md` | Systemic Critic role, L4 activation | Systemic Critic, Team Lead | critics, systemic, governance |
| `.claude/agents/learning/team_lead.md` | Team Lead best practices, routing lessons | Team Lead | learning, team-lead |
| `.claude/agents/learning/implementation_agent.md` | Python patterns, OllamaUnavailableError, import errors | Implementation Agent | learning, python, implementation |
| `.claude/agents/learning/architecture_agent.md` | Module hierarchy, dependency directions, split threshold | Architecture Agent, Designer | learning, architecture, module |
| `.claude/agents/learning/documentation_agent.md` | Source-first, no assumptions, cross-references | Documentation Agent | learning, documentation |
| `.claude/agents/learning/librarian_agent.md` | Deduplication, retrieval optimization, merge-before-new | Librarian Agent | learning, librarian, knowledge |
| `.claude/agents/learning/collector_agent.md` | Acceptance criteria checking, consistency check | Collector Agent | learning, collector, validation |
| `.claude/agents/learning/validation_agent.md` | Extreme values, edge cases, report format | Validation Agent | learning, validation, testing |
| `.claude/agents/learning/pattern_recognition_agent.md` | 2-instance rule, abstraction candidates | Pattern Recognition Agent | learning, patterns, abstraction |
| `.claude/agents/learning/skill_agent.md` | Silent observation, only intervene on pattern | Skill Agent | learning, skills, meta |
| `.claude/agents/learning/critics/technical_critic.md` | Severity system, critique philosophy | Technical Critic | learning, critics, technical |
| `.claude/agents/learning/critics/systemic_critic.md` | Months horizon, complexity drift, dependency creep | Systemic Critic | learning, critics, systemic |
| `.claude/knowledge/architecture.md` | Knowledge taxonomy (3 types), indexing rules | Librarian Agent | knowledge, taxonomy |
| `.claude/knowledge/routing.md` | Agent+model mapping, L0–L2+ composition principle | Team Lead, Skill Agent | routing, models, agent-selection |
| `.claude/knowledge/decisions.md` | Append-only decision log: architecture & policy decisions | Team Lead | decisions, architecture, policy |
| `.claude/knowledge/research_archive_template.md` | Template for research archive entries (RES-YYYY-NNN) | Research Agent, Librarian Agent | research, archive, template |
| `.claude/knowledge/index.md` | This index — complete file map | Librarian Agent | index, knowledge, librarian |
| `.claude/performance/tracking.md` | Per-agent and system metrics, good/bad thresholds | Team Lead, Skill Agent | performance, metrics |
| `.claude/performance/log_template.md` | Performance log template for completed major tasks | Team Lead | performance, log, template |
| `src/main.py` | Entry point: REPL, --task CLI, stdin pipe | Implementation Agent | python, entry-point, repl |
| `src/orchestrator.py` | Task classification L0–L5, agent routing, Ollama guard | Implementation Agent, Architecture Agent | python, orchestration, routing |
| `src/workflow.py` | Trigger recognition (Task:/Review:/ etc.), doc naming, Docs/ scaffold | Implementation Agent | python, workflow, trigger |
| `src/ollama_client.py` | HTTP client localhost:11434, 5 task_types, OllamaUnavailableError | Implementation Agent | python, ollama, client |
| `src/claude_client.py` | Spawns claude-CLI subprocesses, self-contained prompts | Implementation Agent | python, claude, subprocess |
| `src/config.py` | Paths (PROJECT_ROOT, Docs/), model preferences, Ollama endpoint | All agents | python, config, paths |
| `src/agents/base.py` | Base agent class: run(), report() | Implementation Agent | python, agents, base |
| `src/agents/implementation.py` | Implementation Agent: write/modify Python code | Implementation Agent | python, agents, implementation |
| `src/agents/documentation.py` | Documentation Agent: create/improve Docs/ | Documentation Agent | python, agents, documentation |
| `src/agents/validation.py` | Validation Agent: syntax check, tests | Validation Agent | python, agents, validation |
| `src/agents/librarian.py` | Librarian Agent: knowledge base lookups | Librarian Agent | python, agents, librarian |
| `.project/MEMORY.md` | Cross-session memory: stable findings, user preferences | All agents | memory, context, stable |
| `.project/Docs/TASKS.md` | Trigger reference overview | Team Lead | trigger, workflow |

---

## Topic → File Mapping

### "Ollama Client / Freeze Protocol"

Primary sources:
- `src/ollama_client.py` — HTTP client, OllamaUnavailableError, task_types
- `.claude/governance/ollama_integration.md` — Models, hardware routing, freeze protocol

### "Orchestrator / Task Classification"

Primary sources:
- `src/orchestrator.py` — Classify, route, coordinate
- `.claude/governance/escalation_matrix.md` — L0–L5 thresholds
- `.claude/governance/decision_policy.md` — When which level
- `.claude/knowledge/routing.md` — Agent+model mapping

### "Workflow Trigger / Doc Naming / Archival"

Primary sources:
- `src/workflow.py` — Trigger recognition and dispatch
- `.claude/governance/workflow_triggers.md` — Keywords, process, formats (incl. Archive:)
- `.claude/governance/task_archival.md` — BP-005 archival after task completion
- `.claude/governance/document_placement.md` — BP-006 correction of wrong placement
- `.project/Docs/TASKS.md` (if present in project) — Trigger quick reference

### "Python Modules / Architecture"

Primary sources:
- `src/config.py` — Paths and constants

### "Agent Roles / Governance"

Primary sources:
- `.claude/SYSTEM.md` — Overview of all roles and subfolders
- `.claude/agents/team_lead.md` — Team Lead role
- `.claude/agents/designer.md` — Designer role
- `.claude/agents/specialists.md` — All Specialists
- `.claude/agents/research.md` — Research Agent
- `.claude/agents/critics/technical.md` — Technical Critic
- `.claude/agents/critics/systemic.md` — Systemic Critic

Processes:
- `.claude/governance/execution_protocol.md` — Complete flow
- `.claude/governance/escalation_matrix.md` — L0–L5
- `.claude/governance/decision_policy.md` — When who decides

### "Python Patterns / Best Practices"

Primary sources:

Learning logs with examples:
- `.claude/agents/learning/implementation_agent.md` — Python implementation patterns
- `.claude/agents/learning/architecture_agent.md` — Architecture decisions

### "Routing / Model Selection"

Primary sources:
- `.claude/knowledge/routing.md` — Task → Agent + Model mapping
- `.claude/collaboration.md` — Scenarios: new Python function, architecture decision, etc.
- `.claude/governance/ollama_integration.md` — Models: qwen2.5-coder:32b (CPU), phi4:14b (GPU), qwen2.5-coder:14b (GPU)

Rules:
- `.claude/governance/execution_protocol.md` — Phase 0a Ollama pre-briefing
- `.claude/agents/specialists.md` — Ollama-First obligation

### "Spawn Prompt / Claude CLI"

Primary sources:
- `src/claude_client.py` — Subprocess spawning
- `.claude/governance/file_ownership.md` — Spawn prompt required content

### "Performance Tracking / Self-Improvement"

Primary sources:
- `.claude/performance/tracking.md` — Metrics definitions
- `.claude/performance/log_template.md` — Log template
- `.claude/governance/self_improvement.md` — Post-task cycle

### "Review / Validation"

Primary sources:
- `.claude/governance/review_process.md` — Standard review steps
- `.claude/agents/learning/validation_agent.md` — Edge cases, extreme values
- `.claude/agents/learning/collector_agent.md` — Acceptance criteria checking

### "Git / Branch Workflow"

Primary sources:
- `.claude/governance/git_workflow.md` — Commit rules, forbidden actions

---

## Contracts & Schemas

| File | Purpose | Typical Requesters | Topic Tags |
|---|---|---|---|
| `.claude/contracts/SPEC_SHEET.md` | Short list of central specs, trust modes, pipeline | Team Lead, all agents | contracts, specs |
| `.claude/contracts/schemas/*.json` | Complete JSON schemas (~95 files) | Implementation, Skill Runner | contracts, schemas |

---

## Ops / Observability

| File | Purpose | Typical Requesters | Topic Tags |
|---|---|---|---|
| `.claude/agents/qualitysignal_aggregator.md` | QualitySignal aggregation | Team Lead, Personaler | ops, quality |
| `.claude/agents/escalation_controller.md` | Escalation control | Team Lead | ops, escalation |
| `.claude/agents/operations/department_lead_ops_ledger.md` | Ops Ledger (Department Lead) | Ops Agents | ops, ledger |
| `.claude/agents/operations/skill_scout.md` | Skill Discovery | Team Lead, Meta Agent | skills, discovery |
| `.claude/governance/routing_matrix.md` | Routing matrix | Team Lead | routing, ops |
| `.claude/governance/skill_scout_triggers.md` | Skill Scout triggers | Team Lead | skills, triggers |
| `.claude/governance/planning_policy.md` | Planning policy | Team Lead, Planning | planning, governance |
| `.claude/governance/experiment_budget.md` | Experiment budget | Team Lead | ops, experiment |
| `.claude/governance/prompt_debt_policy.md` | Prompt debt policy | Documentation Agent | docs, prompt-debt |
| `.claude/governance/deep_oodle_mode.md` | Deep Oodle mode | Team Lead | ollama, routing |
| `.claude/governance/feedback_policy.md` | Feedback policy | Team Lead, Report Worker | feedback, ops |
| `.claude/governance/no_llm_mode.md` | No-LLM mode | Team Lead | governance, fallback |
| `.claude/governance/policy_gatekeeper.md` | Policy gatekeeper | Team Lead | governance, policy |
| `.claude/governance/paths_and_placeholders.md` | Paths and placeholders | All agents | paths, config |
| `.claude/governance/naming_canon.md` | Naming conventions | All agents | governance, naming |
| `.claude/governance/artifacts_and_paths.md` | Artifacts and paths | Implementation Agent | artifacts, paths |
| `.claude/governance/message_triad_protocol.md` | Message triad protocol | Team Lead, Input Tasks | input, triad |
| `.claude/governance/path_semantics.md` | Path semantics | All agents | paths, governance |
| `.claude/skills/registry.md` | Skill registry (catalog of all skills) | Skill Scout, Team Lead | skills, registry |
| `.claude/skills/playbooks/` | Playbooks (e.g., qa_campaign, documentation_pipeline) | Team Lead, Agents | skills, playbooks |
| `.claude/skills.md` | Pointer to registry + playbooks | All agents | skills, pointer |
| `.claude/tools/menus/planning_policy_menu.py` | Planning policy menu | Team Lead | planning, tools |
| `.claude/tools/menus/feedback_policy_menu.py` | Feedback policy menu | Team Lead | feedback, tools |
| `.claude/tools/skills/edge_case_selector.py` | Edge case selector skill | TestOps, Tester | skills, testing |
| `.claude/tools/skills/decision_feedback.py` | Decision feedback skill | Team Lead | skills, feedback |
| `.claude/tools/skills/deliberation_pack_build.py` | Deliberation pack builder | Team Lead | skills, deliberation |
| `.claude/tools/skills/outcome_event_generate.py` | Outcome event generator | Ops, Report Worker | skills, outcome |
| `.claude/contracts/schemas/idea_set_spec.schema.json` | IdeaSetSpec schema | Ideation Tasks | contracts, ideation |
| `.claude/contracts/schemas/plan_diff_spec.schema.json` | PlanDiffSpec schema | Planning | contracts, planning |
| `.claude/contracts/schemas/deliberation_pack_spec.schema.json` | DeliberationPackSpec schema | Team Lead | contracts, deliberation |
| `.claude/contracts/schemas/message_triad_spec.schema.json` | MessageTriadSpec schema | Input Tasks | contracts, triad |
| `.claude/tasks/ideation/` | Ideation tasks | Team Lead | tasks, ideation |
| `.claude/tasks/deep/` | Deep tasks | Team Lead | tasks, deep |
| `.claude/tasks/ops/080_AUTOTUNE_POSTRUN.md` | Autotune post-run | Ops | tasks, autotune |
| `.claude/tasks/ops/090_CONTRACT_DRIFT_SENTINEL.md` | Contract drift sentinel | Ops, QA | tasks, drift |
| `.claude/tasks/ops/100_COMMAND_DRYRUN.md` | Command dry-run | Ops | tasks, dryrun |
| `.claude/tasks/governance/010_POLICY_GATE_CHECK.md` | Policy gate check | Team Lead | tasks, governance |
| `.claude/tasks/evidence/000_EVIDENCE_ROUTER.md` | Evidence router | Research, Evidence | tasks, evidence |
| `.claude/tasks/routing/090_AUTOTUNE_PATCH_PACK.md` | Autotune patch pack | Ops, Routing | tasks, routing |
| `.claude/tasks/runbook/000_ONE_BUTTON_RUNBOOK.md` | One-button runbook | Ops | tasks, runbook |
| `.claude/tasks/input/` | Input/triad tasks | Team Lead | tasks, input |
| `.claude/tasks/input/030_TRIAD_LINT.md` | Triad lint | Input Pipeline | tasks, triad |
| `.claude/knowledge/localAIs.md` | Local AI inventory (Ollama models etc.) | Team Lead, Routing | knowledge, ollama |

---

## Maintenance Notes

**When this index must be updated:**
- New `.md` file created in `.claude/` or `.project/Docs/References/` / `.project/Docs/Plans/`
- New `src/` file added in deployment project
- Existing file fundamentally changed in content (new topic, new responsibility)
- New agent type added

**Who updates:**
- Librarian Agent — after completion of every task that creates or changes knowledge-relevant files

**Format rule:**
- Don't shorten table columns — complete paths in column 1
- Topic tags in column 4: English or German consistent, lowercase, hyphens instead of spaces

---

## Legacy Design Records

Historical architecture decision records and spec documents from Clockwork v17 and earlier. These are indexed here for discoverability; all files are read-only in `.claude-development/`. Cross-reference: `mvps/archive/MVP_Chain_Legacy.md`.

| File | Description | Status |
|------|-------------|--------|
| `.claude-development/designs/adr_capability_enforcement.md` | ADR: capability enforcement model for agent permissions | Superseded by `.claude/contracts/schemas/` |
| `.claude-development/designs/adr_runtime_critics_integration.md` | ADR: runtime integration of Technical and Systemic critics | Active reference |
| `.claude-development/designs/B-010_runtime_critics_design.md` | Design: runtime critics pipeline (B-010 chain item) | Legacy |
| `.claude-development/designs/B-013_adaptive_router_v1_design.md` | Design: adaptive model router v1 (B-013 chain item) | Superseded by bandit router |
| `.claude-development/designs/capabilities_spec.yaml` | Spec: capability names and permission scopes | Legacy — see `.claude/contracts/schemas/` |
| `.claude-development/designs/command_allowlist_spec.yaml` | Spec: allowed shell commands per agent role | Legacy |
| `.claude-development/designs/critic_gates_spec.yaml` | Spec: critic gate thresholds and escalation rules | Legacy — see `.claude/governance/` |
| `.claude-development/designs/eval_shadow_ab_cbl_spec.md` | Spec: shadow A/B evaluation and CBL eval design | Active reference for `.claude/eval/` |
| `.claude-development/designs/per_agent_capability_matrix.md` | Matrix: per-agent capability assignments | Legacy — see `.claude/agents/` |
