# Policy Violation Report — Template

_Template version: 1.0 (CCW-MVP05)_

Use this template whenever a policy violation is detected, blocked, or remediated.
File completed reports under `.report/violations/` using the naming convention:
`YYYY-MM-DD_<policy_id>_<severity>.md`

---

## Violation Report Template

```markdown
# Policy Violation Report

**Timestamp:** YYYY-MM-DDTHH:MM:SSZ
**Report ID:** VIO-YYYY-MM-DD-NNN  (sequential within the day)
**Policy ID:** [policy identifier — e.g. NO_RUNTIME_IN_CLAUDE, DESTRUCTIVE_ACTION_GUARD]
**Policy source:** [file path — e.g. governance/execution_protocol.md]

## Violating Action

**Action attempted:** [exact command, file write path, or agent operation]
**Initiated by:** [agent name / role / tool]
**Context:** [what task or workflow triggered this action]

## Severity

**Severity:** P0 / P1 / P2
- P0 — Critical: data loss, security breach, or irreversible system state change
- P1 — High: policy bypass attempted; blocked by gate; no data loss
- P2 — Low: policy drift detected; no gate triggered; informational

## Blocked

**Blocked:** yes / no
**Blocked by:** [gate name, hardline rule, or manual review — if blocked]
**Blocking mechanism:** [e.g. hardlines.yaml deny rule, L5 gate, pre-commit hook]

## Impact Assessment

**Files affected:** [list of files that were or would have been modified]
**Reversible:** yes / no
**State at time of report:** [clean / dirty — describe actual system state]

## Remediation

**Action taken:** [what was done to resolve the violation or prevent recurrence]
**Fix verified by:** [test name, gate re-run, or manual check]
**Follow-up required:** yes / no
**Follow-up task:** [if yes: describe or link to task]

## Notes

[Any additional context, root cause analysis, or links to related reports]
```

---

## Severity Reference

| Severity | Meaning | Example |
|----------|---------|---------|
| P0 | Critical — irreversible action taken or imminent | `rm -rf src/` executed; secrets committed to repo |
| P1 | High — violation attempted and blocked | Agent tried to write to `.claude/`; hardline deny triggered |
| P2 | Low — drift detected, no immediate harm | File placed in wrong directory; no gate triggered |

---

## Example Completed Report

# Policy Violation Report

**Timestamp:** 2026-03-02T14:32:00Z
**Report ID:** VIO-2026-03-02-001
**Policy ID:** NO_RUNTIME_IN_CLAUDE
**Policy source:** `governance/execution_protocol.md`, `policies/hardlines.yaml`

## Violating Action

**Action attempted:** Write `cache/ollama_response.json` to `.claude/cache/`
**Initiated by:** Implementation Agent (draft task for `src/ollama_client.py`)
**Context:** Agent attempted to cache an Ollama API response for reuse within the same session.

## Severity

**Severity:** P1

## Blocked

**Blocked:** yes
**Blocked by:** `hardlines.yaml` denied_write_roots rule (`.claude/` is denied)
**Blocking mechanism:** Skill runner pre-flight write-root check

## Impact Assessment

**Files affected:** None (write was blocked before execution)
**Reversible:** yes (no change occurred)
**State at time of report:** clean

## Remediation

**Action taken:** Agent redirected cache write to `.clockwork_runtime/cache/ollama_response.json` (allowed write root). No functional change to output.
**Fix verified by:** `qa_tests/test_no_claude_dependency.py` — PASS
**Follow-up required:** no

## Notes

Root cause: Agent prompt did not include explicit allowed write root list. Agent spawn prompt updated to include the write-root table from `hardlines.yaml`. No governance file changes required.

---

## Filing Instructions

1. Complete all fields. Do not leave fields blank — use "N/A" only when genuinely not applicable.
2. Save to `.report/violations/YYYY-MM-DD_<policy_id>_<severity>.md`.
3. For P0 violations: immediately escalate to Team Lead and halt the triggering workflow.
4. For P1 violations: log and continue; review in next self-improvement cycle.
5. For P2 violations: log; include in periodic review (every 10 major tasks).
