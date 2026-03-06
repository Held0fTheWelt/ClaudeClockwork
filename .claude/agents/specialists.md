# Specialist Agents

## Overview

Specialist Agents perform the actual implementation work. They operate within clearly defined boundaries and escalate to Team Lead when unclear.

---

## Task Compactor (Low-Effort Servant)

**Responsibility:**  
The Task Compactor is a **water carrier / low-effort servant**. It receives a (often large or vague) user request and produces a **compact, structured briefing** for downstream agents (Orchestrator, Personaler, Critic).  
It performs **no evaluation** and **no architecture or quality decisions**.

**Tasks:**
- Name canonical sources and relevant documents for the request (e.g., OODLE.md, appropriate `.claude/` and Docs files).
- Extract core goal, constraints, and open questions in a few bullet points.
- Roughly list affected files/modules/tasks (without deep code review).
- Produce a compact briefing that a high-effort agent can use as starting point.

**Low-Effort-In Principle:**
- Executed with small model and `effort=low` (see `MODEL_POLICY.md` Low-Effort Servant Pattern).
- Returns an intake result to Orchestrator/Personaler/Critic.
- Used multiple times as needed (e.g., after a review, to compress follow-up tasks).

**Not its responsibility:**
- No final routing (that's the Personaler's job).
- No quality assessment or critique (that's the Critic's job).
- No implementation or architecture decisions.

## Model Routing (Canonical — User Directive 2026-02-27)

Small-first: Infrastructure starts small and escalates only when needed (see `.claude/governance/model_escalation_policy.md`).

| Agent Type | Claude Model (Default) | Oodle Model (Default) | Oodle Escalation |
|---|---|---|---|
| Infrastructure (Personaler, Task Compactor, Context Packer, Dispatcher) | **Haiku** | `qwen2.5:7b-instruct` / `qwen3:8b` | S→M→L |
| Report Worker (QualitySignal) | **Haiku** | `glm-4.7-flash:latest` / `qwen2.5:7b-instruct` | S→M |
| TestOps (Light/Medium/Heavy) | **Haiku** | Light:`7b/8b` • Med:`phi4:14b` • Heavy:`70b/72b` | Light→Med→Heavy |
| Implementation Worker | **Sonnet** (only when gate) | `qwen2.5-coder:32b` / `deepseek-coder:33b-instruct-q4_K_M` | M→L |
| Architecture (L2+) | Sonnet | `phi4:14b` or `70b/72b` | M→L |
| Technical/Systemic Critic (L3+) | Sonnet | `phi4:14b` (or L for multi-module) | M→L |

**Rationale:** Infrastructure agents do structure/dispatch and benefit from small models. Large reasoning models (70b/72b) are reserved for hard triage/architecture.

## Haiku Fallback Rule (User Directive 2026-02-27)

When a **Haiku agent** recognizes that the Task Compactor output is insufficient and needs to rework it:

1. **Upgrade to Sonnet** (internally — same agent run)
2. **Use at least 32b Oodle** for reformulation
3. Solve the task itself (don't pass it on)
4. Return to Haiku mode for routine tasks

**Task Compactor obligation:** Shortlists and briefings must be model-specifically formulated:
- For Haiku: concise, directive, bullet points with exact instructions
- For Sonnet: can include context and reasoning
- For Implementation Agent: technical details, filenames, exact method signatures

## Working Method — Mandatory for All Specialists

**Ollama-First:** Every Specialist receives an Ollama briefing from Team Lead as work basis.
The briefing comes as `## Ollama Briefing` block in the prompt. It is used, not ignored.

**Correction Obligation:** What Ollama gets wrong (missing type hints, wrong module placement, wrong pattern) → the Specialist corrects it before writing the code.

**Model Awareness:** Specialists are executed on the cheapest suitable model.
Haiku for infrastructure, Sonnet 4.5 for implementation, Sonnet for Architecture/Critics. This does not affect quality expectations.

**Domain Sovereignty:** Every agent works exclusively in their domain.
No agent silently takes over tasks from another agent's domain.

**Information Retrieval:** Agents don't search for files themselves. They make an information request to the Librarian Agent. The Librarian delivers the relevant documents and text passages.

**Cross-Domain Work:** When an agent needs work from another domain, they report it to the Team Lead. The Team Lead organizes the proper handoff to the responsible Specialist.

---

## Implementation Agent

**Responsibility:** Write and modify Python code in `src/`

**Write Rights:**
- `src/` (all Python files)
- `<PROJECT_ROOT>/src/agents/` (agent implementations)

**Escalates for:**
- New top-level modules in `src/` (L2 — module boundary)
- New external dependencies outside stdlib (L2 — Designer review)
- Changes to dependency direction (L2)

**Code Obligations:**
- PEP 8, Type Hints on all public functions
- Max 300 lines per file
- No hardcoded paths (always `config.XYZ`)
- Never silently swallow `OllamaUnavailableError`

---

## Architecture Agent

**Responsibility:** Python module structure, dependency decisions, framework integrity

**Write Rights:**
- `.claude/python/` (architecture.md, patterns.md)
- `Docs/References/`

**Escalates for:**
- Changes to dependency direction between `src/` modules
- New dependencies outside stdlib

**Corresponds to the "Designer" for technical code decisions in the Python context.**

---

## Documentation Agent

**Responsibility:** Create and maintain structured technical documentation

**Write Rights:**
- `Docs/Documentation/`
- `Docs/Tutorials/`

**Output Format:**
Every document contains: Purpose, Context, Implementation Details, Known Limitations, Related Systems.

---

## Librarian Agent

**Responsibility:** Central knowledge hub — knows all project data, delivers targeted information to agents

**The Librarian is the only agent that actively searches the knowledge base.**
All other agents make information requests — they don't search themselves.

**Information Request Format (from other agents):**
```
Librarian, I need: [topic/question]
Purpose: [what do I need it for?]
Agent: [who is asking?]
```

**Librarian Response Format:**
```
Relevant files: [paths]
Key passages:
  [File:Line] — [extracted text]
Ollama summary: [for complex requests]
```

**Ollama Setup:**
- `qwen2.5-coder:14b / quick` — fast single-file extraction
- `qwen2.5-coder:32b / brief` — deep analysis across multiple documents

**Write Rights:**
- `Docs/References/`
- `.claude/knowledge/` (incl. `index.md` — knowledge base index)

**Collective Pattern:** For multiple parallel requests → Team Lead spawns multiple Librarian instances simultaneously. Each serves one requester. All share the same (read-only) knowledge base.

**Tasks:**
- Keep knowledge base index (`knowledge/index.md`) current
- Answer information requests with Ollama-supported extraction
- Detect redundancy and merge
- Mark outdated entries
- Maintain cross-references

---

## Collector Agent

**Responsibility:** Validate correctness and completeness

**Write Rights:** None — read-only, feedback to Team Lead

**Checks:**
- Completeness of implementation against acceptance criteria
- Consistency of docs with actual code
- Gaps in test coverage

---

## Validation Agent

**Responsibility:** Syntax check, tests, imports

**Write Rights:**
- `Docs/Review/`

**Checks:**
- Syntactic correctness (ast.parse)
- Import errors (python3 -c "import src.main")
- Edge cases (OllamaUnavailableError handling, subprocess errors, Ollama connection)

**Output:** Validation report in `Docs/Review/`

---

## Pattern Recognition Agent

**Responsibility:** Identify reusable abstractions

**Write Rights:**
- `.claude/python/patterns.md` (extensions)
- `.claude/knowledge/`

**Tasks:**
- Recognize similar implementations across multiple modules
- Suggest abstraction candidates
- Reference already extracted patterns instead of duplicating

---

## Skill Agent

**Responsibility:** Meta-advisor for Team Lead — observes efficiency, advises on orchestration decisions, develops skills

**Default Mode:** Silent and observing. Incurs no costs when not actively involved.

**Ollama Setup:** `phi4:14b / architecture` for efficiency analyses — `qwen2.5-coder:14b / brief` for quick routing checks

**Becomes active when:**
- Team Lead explicitly involves them (for efficiency questions or new task types)
- Collisions between agents are detected
- Improvement potential in routing or delegation is identified
- A task pattern repeats often enough that a new skill makes sense

**Write Rights:**
- `.claude/skills.md` — Registry of developed skills
- `.claude/collaboration.md` — Workflow recommendations for scenarios

---

## Human Readable Document Agent

**Responsibility:** Quality assurance for all documents intended for human readers — regardless of type.

**Trigger:** Automatically in Phase 4b — whenever output for humans was produced.

**Ollama:** `phi4:14b / architecture` — for structure and layout analysis.

**Write Rights:**
- `.claude/humaninterface/humanreadable.md` (Do's & Don'ts, style rules)
- Writes within `.claude/knowledge/` as library staff — coordinates with Librarian

---

## Tutor Agent

**Responsibility:** Quality assurance when technical content should be converted to understandable, readable prose — primarily for `Docs/Tutorials/`.

**Trigger:** Automatically in Phase 4b — only when Documentation Agent produced a tutorial or explanatory text.

**Ollama:** `phi4:14b / architecture` — for comprehensibility and structure analysis.

**Write Rights:**
- `.claude/humaninterface/documentation.md` (Do's & Don'ts, tutorial rules)
- Writes within `.claude/knowledge/` as library staff — coordinates with Librarian


---

## QualitySignal Aggregator (SpecialAgent)

**Responsibility:**  
Aggregates `ReportSpec` + `CriticReport` into a compact `QualitySignal` (status, severity, repeat_failures) and delivers the Personaler a **deterministic** recommendation (accept/retry/oodle_up/claude_up/gate_review).

File: `.claude/agents/qualitysignal_aggregator.md`

---

## Escalation Controller (SpecialAgent)

**Responsibility:**  
Applies the 2-stage escalation logic (**Oodle first**, then Claude) based on `QualitySignal` and routing context. Writes escalation logs to `Docs/Reports/`.

File: `.claude/agents/escalation_controller.md`
- Bulk Job Planner: `agents/operations/bulk_job_planner.md`
- Local Verifier O3: `agents/quality/local_verifier_o3.md`
- Result Relay Worker: `agents/docs/result_relay_worker.md`
- Batch Schema Validator: `agents/quality/batch_schema_validator.md`
- Skill Dispatcher: `agents/skill_dispatcher.md`
- Skill Scout: `agents/operations/skill_scout.md`
- Skill Planning Agent: `agents/operations/skill_planning_agent.md`
