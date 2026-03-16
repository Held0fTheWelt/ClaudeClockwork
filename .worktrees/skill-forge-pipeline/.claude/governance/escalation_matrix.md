# Escalation Matrix

Defines strict governance boundaries between Team Lead, Architecture Agent, and Critics.

---

## Level 0 — Autonomous Execution

**Handled by:** Specialist Agents
**No escalation required.**

Examples:
- Minor feature additions (new private method, new log line)
- Documentation updates
- Non-structural refactors (internal renaming, formatting)
- Bugfixes with clearly isolated cause

---

## Level 1 — Team Lead Review

**Required for:**
- Multi-module changes (2–5 files, clearly bounded)
- Moderate refactors without API change

Team Lead can approve without Architecture Agent.

---

## Level 2 — Architecture Agent Mandatory Review

**Required for:**
- Framework rule changes
- Module boundary changes (what goes in which module)
- Dependency direction changes
- New Python package dependencies (outside stdlib)
- New top-level modules in `src/`
- Public API changes affecting other modules

**Architecture Agent approval required before implementation.**

---

## Level 3 — Technical Critic Mandatory Review

**Required for:**
- Performance-critical paths (Ollama client timeout handling, subprocess pooling)
- External API integration (Claude CLI interface changes)
- Persistent data structure changes (Docs/ schema, config format)

**Critic provides adversarial evaluation → Team Lead decides.**

---

## Level 4 — Systemic Critic Mandatory Review

**Required for:**
- Adding new agent types
- Changing governance rules
- Modifying self-improvement cycle
- Adjusting escalation thresholds

**Systemic Critic evaluates long-term complexity → Team Lead decides.**

---

## Level 5 — User Confirmation Required

**Required for:**
- Orchestrator core redesign (fundamental restructuring of `src/`)
- Switching LLM backend (replacing Ollama with another system)
- Fundamental change to workflow trigger system

**No autonomous decision allowed.**

---

## Conflict Resolution

When Architecture Agent and Critic disagree:

1. Team Lead summarizes trade-offs
2. Categorize risk level (Low / Medium / High)
3. User makes final decision for L3+ conflicts
4. Document decision in performance log

---

## Quick Reference

| Situation | Level | Who decides |
|---|---|---|
| Bugfix in one file | 0 | Specialist |
| Multi-file refactor | 1 | Team Lead |
| New Python package as dependency | 2 | Architecture Agent |
| Ollama client timeout handling | 3 | Technical Critic → Team Lead |
| Change governance rule | 4 | Systemic Critic → Team Lead |
| Core orchestrator redesign | 5 | User |
