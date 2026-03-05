# Audit Log Template — OllamaCode Clockwork

_Template version: 1.0 (CCW-MVP05)_

Use this template to document decisions made during development, governance changes,
escalations, and any action that requires a traceable record.

---

## Decision Log Entry Template

```markdown
## Decision Log Entry

**Date:** YYYY-MM-DD
**Decided by:** [agent/role — e.g. Team Lead, Architecture Agent, User]
**Task:** [brief task description — one line]
**Decision:** [what was decided — concrete outcome, not a summary of discussion]
**Evidence:** [file paths, test results, Ollama briefing references, PR links]
**Escalation level:** L0–L5 (see governance/decision_policy.md)
**Reversible:** yes / no
**Rollback plan:** [if not reversible: exact steps to undo; "N/A" only if truly irreversible by design]
```

---

## Example Entry 1 — Autonomous L0 Decision

## Decision Log Entry

**Date:** 2026-03-02
**Decided by:** Implementation Agent
**Task:** Add type hints to `src/ollama_client.py` public methods
**Decision:** Added `-> str` and `-> bool` return type annotations to `is_available()`, `brief()`, `draft()`, `review()`, and `architecture()`. No API surface changed.
**Evidence:**
- `src/ollama_client.py` — diff confirms only annotation additions, no logic changes
- `qa_tests/` — all 12 tests pass after change (`python3 -m pytest qa_tests/ -q`)
**Escalation level:** L0 (single file, no public API change, no runtime impact outside file)
**Reversible:** yes
**Rollback plan:** `git revert <commit-sha>` restores pre-annotation state in under 30 seconds.

---

## Example Entry 2 — L4 Escalation: Governance Rule Change

## Decision Log Entry

**Date:** 2026-03-02
**Decided by:** Team Lead (after Systemic Critic review)
**Task:** Add `hardlines.yaml` to enforce destructive-action opt-in at policy layer (CCW-MVP05)
**Decision:** Created `.claude/policies/hardlines.yaml` as machine-readable policy file. Hardlines cover: destructive git/shell actions (DENY or L4/L5 gates), write-root restrictions, external provider opt-in, commit guards, and default dry-run mode. Existing governance `.md` files were NOT modified.
**Evidence:**
- `.claude/policies/hardlines.yaml` — created at CCW-MVP05 delivery
- `.claude/policies/POLICY_INDEX.md` — policy indexed with testability status
- `.claude/development/MVP_STATUS.md` — MVP05 marked done
- Systemic Critic: no objections raised; policy adds structure without removing flexibility
**Escalation level:** L4 (governance addition; Systemic Critic mandatory per decision_policy.md)
**Reversible:** yes
**Rollback plan:** Delete `.claude/policies/hardlines.yaml` and `.claude/policies/POLICY_INDEX.md`; revert MVP_STATUS.md entry. Gate re-run confirms clean state.

---

## Usage Notes

1. Entries are append-only. Never edit or delete a past entry.
2. Store decision log entries in `.claude/knowledge/decisions.md`.
3. For L3+ decisions, include the Critic report file path under **Evidence**.
4. **Rollback plan** is mandatory when **Reversible: no**.
5. Reference this template from `.claude/policies/POLICY_INDEX.md` for discoverability.
