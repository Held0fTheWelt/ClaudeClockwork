# File Ownership — Python Orchestrator Agent System

> Every file belongs to exactly one agent. No agent may edit files owned by another.
> Cross-domain changes go through Team Lead → Domain Handoff Protocol.

---

## Ownership Table

| Path / Pattern | Owner Agent | Write Rights |
|---|---|---|
| `.claude/agents/*.md` | Team Lead | Governance definitions |
| `.claude/agents/learning/team_lead.md` | Team Lead | Own learning log |
| `.claude/agents/learning/implementation_agent.md` | Implementation Agent | Own learning log |
| `.claude/agents/learning/documentation_agent.md` | Documentation Agent | Own learning log |
| `.claude/agents/learning/librarian_agent.md` | Librarian Agent | Own learning log |
| `.claude/agents/learning/collector_agent.md` | Collector Agent | Own learning log |
| `.claude/agents/learning/validation_agent.md` | Validation Agent | Own learning log |
| `.claude/agents/learning/pattern_recognition_agent.md` | Pattern Recognition Agent | Own learning log |
| `.claude/agents/learning/skill_agent.md` | Skill Agent | Own learning log |
| `.claude/agents/learning/critics/technical_critic.md` | Technical Critic | Own learning log |
| `.claude/agents/learning/critics/systemic_critic.md` | Systemic Critic | Own learning log |
| `.claude/agents/critics/*.md` | Team Lead / Architecture Agent | Critic definitions |
| `.claude/governance/*.md` | Team Lead | Governance protocols |
| `.claude/python/*.md` | Team Lead / Architecture Agent | Python standards |
| `.claude/knowledge/index.md` | Librarian Agent | Knowledge base index |
| `.claude/knowledge/routing.md` | Skill Agent | Routing intelligence |
| `.claude/knowledge/*.md` (other) | Librarian Agent | Knowledge entries |
| `.claude/skills.md` | Skill Agent | Skills registry |
| `.claude/collaboration.md` | Skill Agent | Collaboration scenarios |
| `.claude/tools/*.py` | Implementation Agent | Tooling |
| `.project/memory/*.md` | Team Lead | Cross-session context |
| `.project/Docs/Documentation/` | Documentation Agent | Technical docs |
| `.project/Docs/Tutorials/` | Documentation Agent | Guides |
| `.project/Docs/References/` | Librarian Agent | Reference documents |
| `.project/Docs/Review/` | Validation Agent | Validation reports |
| `.project/Docs/Critics/` | Technical Critic / Systemic Critic | Critic outputs |
| `.project/Docs/Plans/` | Team Lead | Plans |
| `src/` (deployment target) | Implementation Agent | Python implementation |
| `src/agents/` (deployment target) | Implementation Agent | Agent implementations |

---

## Violation Protocol

When an agent needs to edit a file outside their ownership:

```
1. Agent reports to Team Lead: "I need a change in [foreign file]"
2. Team Lead activates the responsible owner agent via Domain Handoff
3. Owner agent makes the change
4. Owner agent reports completion to Team Lead
```

No silent takeover. No editing foreign files — not even "just quickly".

---

## Document Placement Correction (BP-006)

When a document is in the wrong location (e.g., reference in `Docs/Plans/`, plan in `Docs/Documentation/`):
1. Report finding to Team Lead (current location, suggested target location)
2. Team Lead coordinates consultation with owner (user or responsible agent)
3. Only the owner of the target location (or source location) performs the move
4. No silent moves without approval

Full protocol: `governance/document_placement.md`.

---

## Spawn Prompt Required Content

Every agent spawn via the Task tool must include:

```
## Project Context
Python Orchestrator: Console application for autonomous Ollama/Claude agent orchestration.
Module hierarchy: main -> orchestrator -> agents/* -> ollama_client/claude_client -> config
Dependency direction: main → orchestrator → agents → clients (never reverse)
Patterns: OllamaFreeze, SelfContainedSpawn, StructuredOutput, AvailabilityGuard
PEP 8, Type Hints for all public functions, max 300 lines per file.

## Your Role & Write Rights
Role: [Agent Name]
You may ONLY write to the following files: [explicit list]

## Governance
- Only edit own files (file_ownership.md)
- Read files completely before editing
- Ollama-First for L1+ (if relevant)
- Throw OllamaUnavailableError, never silent swallow

## Task
[Concrete task with acceptance criteria]

## Context Files to Read
[Explicit paths]

## Ollama Briefing (if available)
[Output from ollama_client.py or ollama_brief.py]
```

# File Ownership (mirror)

Primary Oodle ownership is defined in `.claude/governance/file_ownership.md`.  
Claude Code must respect those boundaries and request gates for risky changes.
