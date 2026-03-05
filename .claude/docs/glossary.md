# Glossary — OllamaCode Clockwork

_Last updated: 2026-03-02 (CCW-MVP04)_
_Clockwork-internal terms. For project-facing terms see `docs/glossary.md`._

---

**Agent**
An autonomous process that performs a defined role (Planner, Executor, Docs, etc.).
Agents communicate via a message bus and are organised in a four-level hierarchy.
Agent definitions live in `.claude/agents/` (clockwork) or `llamacode/agents/` (runtime registry).

**Boot Check**
A pre-flight environment verification script run before agent work begins.
Invoked via `python3 .claude/tools/boot_check.py`. Checks Python version, Ollama
availability, and workspace integrity.

**CBL (Context Budget Limit)**
The maximum token allowance assigned to an agent for a single session, defined in
`AgentEntry.context_budget`. Enforced by the `BudgetMonitor`.

**Clockwork**
The methodology and deterministic tooling that governs the development workflow.
Lives in `.claude/` (Claude branch) or `.llama/` (Llama/main branch). Read-only
during normal project work — never write runtime state into clockwork.

**Contract**
A schema + example pair under `.claude/contracts/` that defines the typed interface
(input/output) of a skill. Validated by `spec_validate` and `contract_drift_sentinel`.

**Escalation Level**
A tier (L1–L5) defining how expensive or privileged an action is. Higher levels
require explicit user opt-in. Defined in `.claude/governance/escalation_matrix.md`.

**Evidence Bundle**
A reproducible, archivable set of validation artifacts (manifests, test results,
quality reports) produced by the `evidence_bundle_build` skill. Used to prove a
release is deterministic and auditable.

**Genome**
The full set of clockwork files (agents, skills, governance, tools) that define
agent behaviour in this repo. Analogous to a DNA blueprint for the system.

**Shadow Run**
A dry-run or parallel execution of a skill/agent that does not commit side effects.
Used to evaluate quality or detect drift without mutating state.

**Skill**
A deterministic, tool-first micro-workflow. Skills accept a typed JSON input
(`SkillRequestSpec`) and return a typed JSON output (`SkillResultSpec`). No LLM
calls unless explicitly delegated. Invoked via `.claude/tools/skills/skill_runner.py`.

**TeamLead**
The top-level coordination agent that decomposes goals, assigns workers, and
aggregates results. Defined in `.claude/agents/team_lead.md`.

**Telemetry**
Token-budget and quality-signal events written to `.claude-performance/` during
agent runs. Used by `budget_analyze` and `efficiency_review` skills.
