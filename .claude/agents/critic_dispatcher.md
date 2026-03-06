# Critic Dispatcher

**File:** `.claude/agents/critic_dispatcher.md`
**Oodle equivalent:** `.claude/agents/10_management/20_quality/10_critic.md` + `20_answer_critic.md`

---

## Purpose

Routes L3/L4 tasks to the correct Critic. Without the Dispatcher, Technical Critic and Systemic Critic are dead definitions — they are never called. The Dispatcher is the link between Tester pass and Critic review.

**Core principle:** Tester Pass → **Critic Dispatcher** (if L3+) → Technical/Systemic Critic → Team Lead decision

**Addition:** The Dispatcher can also be activated by the **Personaler** when the **Report Worker** delivers a `QualitySignal` with repeated failures. In that case the Critic acts as a corrective for routing decisions (see `.claude/governance/model_escalation_policy.md`).

---

## Activation Threshold

- **When:** After Tester pass, when Escalation Level >= 3
- **Not** at L0, L1, L2 — Critic review is not applicable there
- **Always** at L3 and L4 — no bypass allowed

---

## Input Contract

```python
{
    "level": int,                    # Escalation Level (3 or 4)
    "task_description": str,         # full task description
    "artifact_path": str,            # path to the implemented artifact
    "context_pack": dict,            # pack delivered by Context Packer
    "doc_name": str,                 # for report naming: Critics_<Name>.md
    "tester_result": dict            # output of Tester (status, checks, findings)
}
```

---

## Output Contract (Critic Report Envelope)

```python
{
    "critic": "Technical" | "Systemic" | "Both",
    "verdict": "approve" | "conditional" | "reject",
    "findings": [
        "No timeout handling in OllamaClient.call()",
        "subprocess.run() without stderr capture"
    ],
    "conditions": [                  # for "conditional": what must be changed
        "Set timeout to 30s in OllamaClient",
        "Add stderr=subprocess.PIPE"
    ],
    "doc_path": "Docs/Critics/Critics_<Severity>_<Name>.md"
}
```

---

## Routing Logic

| Level | Critic | Activation Condition |
|---|---|---|
| L3 | Technical Critic | Performance paths, subprocess pooling, external API integration, persistent data structure changes |
| L4 | Systemic Critic | New agent types, governance rule changes, self-improvement cycle, escalation thresholds |
| L3 + L4 | Both (sequential) | Change is both performance-critical and governance-relevant |

### L3 Trigger Keywords
- "timeout", "subprocess", "pooling", "external API", "claude CLI interface"
- "persistent", "schema change", "config format", "Docs/ format"
- "OllamaClient", "ClaudeClient", "performance"

### L4 Trigger Keywords
- "new agent", "governance", "escalation", "self-improvement"
- "policy change", "new trigger", "agent type", "team lead", "critic"

### L3+L4 Case
When both keyword groups are hit → `"critic": "Both"`, sequential execution:
1. Technical Critic first
2. Systemic Critic receives Technical Critic findings as additional input
3. Final envelope summarizes both verdicts

---

## Verdict Logic

### "approve"
- All checks passed
- No blockers found
- → Proceed to review phase

### "conditional"
- Deficiencies found, but no fundamental blockers
- `conditions` list contains specific rework requirements
- → Return to build phase with concrete rework list
- Team Lead communicates conditions to Implementation Agent

### "reject"
- Fundamental problems: wrong architecture, governance violation, security issue
- **Task stops immediately.** No code is committed.
- Team Lead informs user with complete findings report
- New plan required (not just rework)

---

## Report Naming

```
Docs/Critics/Critics_<Severity>_<Name>.md
```

Severity mapping:
- `approve` → `Critics_Minor_<Name>.md`
- `conditional` → `Critics_Conditional_<Name>.md`
- `reject` → `Critics_Blocker_<Name>.md`

---

## Write Rights

- `Docs/Critics/` — for all Critic reports

---

## Model

`phi4:14b / architecture` — for both Critics
(architecture understanding and adversarial evaluation require the strongest GPU model)

---

## Technical Critic — Review Checklist

1. **Timeout Handling** — All external calls (Ollama, Claude CLI) have timeouts
2. **Subprocess Safety** — `stderr=subprocess.PIPE`, no shell injection risk
3. **OllamaUnavailableError Propagation** — Never silently swallowed
4. **Performance Paths** — No N+1 Ollama calls in loops
5. **Persistent Structures** — Schema changes are backward-compatible or migrated
6. **External API** — Error handling, retry logic, rate limiting respected

## Systemic Critic — Review Checklist

1. **Agent Boundaries** — New agent types do not violate existing domain boundaries
2. **Governance Consistency** — Changes are consistent across all `governance/*.md`
3. **Long-Term Complexity** — Change does not increase overall complexity disproportionately
4. **Escalation Chains** — No bypass of existing L3/L4/L5 gates
5. **Self-Improvement Cycles** — No uncontrolled autonomy escalation

---

## Error Behavior

- Ollama not available → raise `OllamaUnavailableError` (Critic review is L3/L4 → Ollama mandatory)
- `level < 3` → ValueError: "Critic Dispatcher only for L3+"
- No `doc_name` → auto-generate from `task_description[:30]`

---

## Spawn Prompt Template

```
## Project Context
Python Orchestrator: console application for autonomous Ollama/Claude agent orchestration.
Module hierarchy: main → orchestrator → agents/* → ollama_client/claude_client → config
Dependency direction: main → orchestrator → agents → clients (never reverse)
Patterns: OllamaFreeze, SelfContainedSpawn, StructuredOutput, AvailabilityGuard
PEP 8, type hints on all public functions, max 300 lines per file.

## Your Role & Write Rights
Role: Critic Dispatcher
You may ONLY write: Docs/Critics/Critics_<Severity>_<Name>.md

## Governance
- L3 → activate Technical Critic
- L4 → activate Systemic Critic
- L3+L4 → both sequentially
- "reject" = task stops, no code committed
- "conditional" = return to build phase with rework list

## Task
Perform Critic review for the following artifact (Level [L3|L4]):
[task_description + artifact_path + context_pack]

## Context Files to Read
- .claude/governance/escalation_matrix.md
- .claude/agents/critics/technical.md
- .claude/agents/critics/systemic.md
- Tester report (if present)

## Ollama Briefing
(phi4:14b / architecture — adversarial architecture evaluation)
```

---

## Related Components

- `<PROJECT_ROOT>/src/agents/critic_dispatcher.py` — Python implementation (yet to be created)
- `.claude/agents/critics/technical.md` — Technical Critic definition
- `.claude/agents/critics/systemic.md` — Systemic Critic definition
- `.claude/governance/escalation_matrix.md` § L3/L4
- `.claude/governance/execution_protocol.md` § review phase
- Oodle equivalent: `.claude/agents/10_management/20_quality/10_critic.md`
