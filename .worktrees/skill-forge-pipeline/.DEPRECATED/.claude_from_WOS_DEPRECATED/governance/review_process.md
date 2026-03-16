# Review Process

## Purpose

The review process ensures that every implementation is correct, readable, documented, and integration-compatible before it's considered complete.

---

## Standard Review Steps

### 0. Hard QA Gate (PR-blocking)

Run the deterministic gate before human review:
- `qa_gate` (see `governance/qa_gate_policy.md`)

If the gate fails: **stop** and fix drift first.

### 1. Check Correctness (Collector Agent)

```
- Compare implementation against all acceptance criteria in Task Brief
- Completeness: Are all required functions present?
- Correctness: Are the solutions logically correct?
- No regressions (existing functionality untouched)?
```

### 2. Check Readability (Collector Agent)

```
- Naming: PEP 8 followed? (snake_case, PascalCase, UPPER_SNAKE_CASE)
- Structure: File under 300 lines? (if not: check for split)
- Type hints: All public functions annotated?
- Comments: Only where logic is not self-explanatory?
- No copy-paste remnants in logs/comments
```

### 3. Check Documentation (Validation Agent)

```
- Technical docs in Docs/Documentation/ current?
- Relevant references in Docs/References/ present?
- MEMORY.md update needed?
- .claude/python/patterns.md update needed?
```

### 4. Check Integration Impact (Validation Agent)

```
- Syntax: ast.parse() successful?
- Import errors: python3 -c "import src.main" without errors?
- OllamaUnavailableError correctly propagated (not silent)?
- Subprocess errors caught at module boundaries?
- Ollama connection: is_available() guard present for L1+?
```

### 5. Approval or Return

```
APPROVED           → Phase 4 begins (Docs + Librarian)
APPROVED WITH CONDITIONS → Implementation has conditions list to fulfill
REQUIRES REWORK    → Back to Phase 1, new review after rework
BLOCKED            → Escalation to Team Lead
```

---

## Review Output Format

```markdown
## Review: [Task Name / PR Name]
**Date:** YYYY-MM-DD
**Reviewer:** [Agent Role]
**Status:** APPROVED / APPROVED WITH CONDITIONS / REQUIRES REWORK / BLOCKED

### Correctness
[Findings]

### Readability
[Findings — PEP 8, Type Hints, Line Count]

### Documentation
[Findings]

### Integration Impact
[Findings — Syntax Status, Import Status, OllamaUnavailableError Handling]

### Conditions (if APPROVED WITH CONDITIONS)
- [ ] Condition 1
- [ ] Condition 2

### Rework Scope (if REQUIRES REWORK)
[What needs to be changed?]
```

---

## Rework Limit

After **2 rework cycles** on the same task:
- Team Lead is mandatorily involved
- Task is re-evaluated (complexity underestimated?)
- Possibly escalation to Architecture Agent or User
