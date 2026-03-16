# Workflow Triggers & Document Naming


# Workflow Triggers

Use the smallest sufficient model size and minimal effort.

**L5 escalation to user** required for:
- External providers / API keys
- Requested tool autonomy (automated bash execution)
- Destructive operations or large refactors
- Persistent disagreement after critic review
- Core orchestrator redesign or LLM backend switch

For complex coding tasks → `qwen2.5-coder:32b` (CPU); for architecture → `phi4:14b` (GPU).


## Trigger Keywords

The user triggers workflows through these keywords:

| Keyword | Workflow | Creates document in |
|---|---|---|
| **Task:** | Plan creation | `.project/Docs/Plans/Plan_<Name>.md` |
| **Review:** | Review creation | `.project/Docs/Review/Review_<Name>.md` |
| **Critics:** | Fundamental critique | `.project/Docs/Critics/Critics_<Severity>_<Name>.md` |
| **Document:** | Create/improve documentation | `.project/Docs/Documentation/` or `.project/Docs/References/` |
| **Implement:** | Implement plan | Code changes |
| **Archive:** | Trigger task archival (BP-005) | Ref + Documentation + Index (after plan completion) |
| **test ollama** | Ollama health check | (no document) |

## Task: Workflow (Plan Creation)

**Planning required when:** Architecture impact exists:
- New or modified components, plugins, interfaces
- Changes to data flow, dependencies, or system behavior
- Impact on more than one isolated location

**No plan needed for:** Single-line fixes, typos, pure config changes without architecture impact.

**Process:**
1. Capture requirement as `Task_<Name>.md` in `.project/Docs/Plans/`
2. Rule check via .claude/SYSTEM.md — consult all relevant documents
3. Rule Discovery — actively search for undocumented rules
4. Create plan document
5. Obtain user approval

**Plan Document Format:**
```
# Plan: <Title>
## Goal
## Checked Rules
## Affected Files
## Implementation Steps
## Newly Discovered Rules
## Open Questions
```

Plan iteration: Update document until implementation (no new document per iteration).

## Review: Workflow

**Review subjects:**
- Plan (before implementation) — is the plan rule-compliant, complete, feasible?
- Implementation (after task execution) — does the implementation match the plan and rules?
- Component/system state — current state of a subsystem

**Process:**
1. Determine subject (Plan / Implementation / Component)
2. Load reference plan from `.project/Docs/Plans/` (if available)
3. Rule check via .claude/SYSTEM.md
4. Rule Discovery
5. Save review document in `.project/Docs/Review/`

**Review Document Format:**
```
# Review: <Title>
## Review Subject
## Findings
### Rule Compliance
### Plan Deviations
### Critique
## Assessment
- [ ] Rule-compliant
- [ ] Plan-compliant (if applicable)
- [ ] No open defects
## Newly Discovered Rules
## Recommendation
```

**Rework cycle:** Specific points → revise plan → new review → until approved.

## Critics: Workflow

**Distinction from Review:**
- Review: "Does this comply with the rules?" → `.project/Docs/Review/`
- Critics: "Is the approach fundamentally wrong?" → `.project/Docs/Critics/`

**Severity levels:**
- `Critics_Minor_` — Plan level: design decision questionable, no structural problem
- `Critics_Normal_` — Review level: concrete problem identified in implementation/review
- `Critics_Major_` — System level: fundamentally flawed, realignment needed

**Critic Document Format:**
```
# Critic: <Question>
## Subject of Investigation
## Current State
## Fundamental Critique
## Impact
## Solution Direction
## Newly Discovered Rules
```

Critic documents are long-term references. A critic can trigger a new task or rule change — but only by user decision.

## Document: Workflow

Documentation from three sources:
1. .claude/ System (SSoT)
2. Existing `.project/Docs/`
3. Source Code

Storage locations:
- Functionality documentation → `.project/Docs/Documentation/`
- Technical definitions → `.project/Docs/Documentation/`
- Reference documents → `.project/Docs/References/`

## Implement: Workflow

**Prerequisites:**
- Plan document exists in `Docs/Plans/Plan_<Name>.md`
- Plan approved by review OR user explicitly confirms

**Process:**
1. Load plan
2. Obtain confirmation — briefly summarize plan + explicitly ask whether to implement
3. Rule check
4. Rule Discovery during implementation
5. Execute implementation
6. Update plan status

Document deviations from plan during implementation immediately and notify user.

**After completion:** Archival (BP-005) — mark task as done, store results in `.project/Docs/References/`, `.project/Docs/Documentation/` and `.claude/knowledge/index.md`. See `governance/task_archival.md`.

## Archive: Workflow (BP-005)

**Trigger:** Explicit keyword **Archive:** or automatically after Implement completion (Plan `IMPLEMENTED`/`CLOSED`).

**Purpose:** Transfer completed task results to reference and feature documents, update knowledge index, remove task from active list.

**Process:**
1. Identify completed task/plan
2. Team Lead coordinates Librarian + Documentation Agent (via Domain Handoff)
3. Librarian: Ref documents to `.project/Docs/References/`, update Index `.claude/knowledge/index.md`
4. Documentation Agent: Create/update feature/tech docs in `.project/Docs/Documentation/`
5. Mark task as done in task overview

Full protocol: `governance/task_archival.md`.

## test ollama — Workflow

Performs a hello-world health check for the local Ollama system.

**Trigger:** User enters `test ollama` — typically at start of work session or after Ollama restart.

**Process:**
1. Execute: `python3 src/main.py --task "test ollama"`
   (alternatively direct: `python3 .claude/tools/test_ollama.py`)
2. Script checks: Reachability → Model availability → Inference → Python output quality
3. On PASS: Agent confirms "Ollama operational — ready for tasks"
4. On FAIL: Agent outputs FREEZE report (see ollama_integration.md § Freeze Protocol)

**No document is created.** The test is a pure status check.

---

## Document Naming Convention

```
<Prefix>_<TopicPascalCase>.md
```

| Document Type | Prefix | Storage Location |
|---|---|---|
| Task description | `Task_` | `.project/Docs/Plans/` |
| Plan | `Plan_` | `.project/Docs/Plans/` |
| Review | `Review_` | `.project/Docs/Review/` |
| Critique (Minor) | `Critics_Minor_` | `.project/Docs/Critics/` |
| Critique (Normal) | `Critics_Normal_` | `.project/Docs/Critics/` |
| Critique (Major) | `Critics_Major_` | `.project/Docs/Critics/` |
| Reference | `Ref_` | `.project/Docs/References/` |

**Document chain:** Related docs share the same topic part:
```
Task_OllamaClient.md
Plan_OllamaClient.md
Review_OllamaClient.md
Critics_Normal_OllamaClient.md
```

Topic part in PascalCase. Multiple reviews/critics for same topic: add suffix (e.g., `_PostImpl`).
Existing documents without convention: rename on next edit.
