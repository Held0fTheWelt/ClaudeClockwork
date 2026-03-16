# Decision Policy

## Decision Hierarchy

Every decision falls into one of three categories: autonomous, review-required, or user confirmation required.

---

## Autonomous Decisions (L0)

No review required. Specialist Agent decides independently.

**Examples:**
- Minor refactors within a single file
- Code formatting, comments
- Documentation updates without content changes
- Logging improvements (no API change)
- Bugfixes with clearly isolated cause

**Characteristics:** Change affects max 1 file, no public API, no runtime impact outside the file.

---

## Team Lead Review (L1)

Team Lead reviews and can approve autonomously. No Architecture Agent or User necessary.

**Examples:**
- Multi-file refactors (2–5 files, clearly bounded)
- New private methods / internal helper functions
- Moderate refactors without API change

**Characteristics:** Multiple files affected, but no public interfaces changed.

---

## Architecture Agent Mandatory Review (L2)

Architecture Agent must approve before implementation.

**Examples:**
- New top-level modules in `src/` (new module vs. extension?)
- New Python package as dependency (anything outside stdlib)
- Module boundary changes in `src/`
- Dependency direction changes (e.g., `config` should import `agents`)
- Public API changes to `orchestrator.py` or `ollama_client.py`

**Escalation Format:**
```
Problem:        [What should be changed and why?]
Options:        [At least 2 alternatives]
Trade-offs:     [Pro/Con for each option]
Recommendation: [Which option is recommended + rationale]
```

---

## Technical Critic Mandatory Review (L3)

Technical Critic provides adversarial evaluation. Team Lead decides afterward.

**Examples:**
- Performance-critical paths (Ollama client timeout handling)
- Subprocess pooling or parallelized agent spawns
- External API integration (Claude CLI interface changes)
- Persistent data structure changes (Docs/ schema, config format changes)

---

## Systemic Critic Mandatory Review (L4)

Systemic Critic evaluates long-term complexity. Team Lead decides afterward.

**Examples:**
- Adding new agent types
- Changing governance rules
- Modifying self-improvement cycle
- Adjusting escalation thresholds
- Reorganizing `.claude/` system structure

---

## User Confirmation Required (L5)

No autonomous decision possible. User decides.

**Examples:**
- Orchestrator core redesign
- Switching LLM backend
- Fundamental change to workflow trigger system

---

## Conflict Resolution

When Architecture Agent and Technical/Systemic Critic disagree:

```
1. Team Lead summarizes trade-offs
2. Categorize risk level (Low / Medium / High)
3. For L3+: User makes final decision
4. Decision is documented in performance log
```

---

## Escalation Template

```markdown
## Escalation: [Title]
**Level:** L2 / L3 / L4 / L5
**Date:** YYYY-MM-DD
**Initiated by:** [Agent]

### Problem
[What is the situation? Why is a decision needed?]

### Options
**Option A:** [Description]
**Option B:** [Description]

### Trade-offs
| Criterion | Option A | Option B |
|---|---|---|
| Complexity | | |
| Performance | | |
| Maintainability | | |

### Recommendation
[Clear recommendation with rationale]
```
