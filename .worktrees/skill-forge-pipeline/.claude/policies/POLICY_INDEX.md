# Policy Index — OllamaCode Clockwork

_Last updated: 2026-03-02_
_Version: 1.0 (CCW-MVP05)_

This index lists all active governance policies with their source file, testability status,
and the mechanism by which each policy can be verified.

---

## Active Policy Table

| Policy | File | Testable? | How to test |
|--------|------|-----------|-------------|
| No runtime state written into `.claude/` | `governance/execution_protocol.md` | YES | `qa_tests/test_no_claude_dependency.py` — scan for unexpected writes under `.claude/`; confirm all write roots are in allowed list from `hardlines.yaml` |
| All product code originates under `src/` | `policies/SRC_ORIGIN_RULE.md` | YES | `qa_tests/test_src_origin_rule.py` — run `enforce_src_origin_rule` scenario; flag any `.py` product files found outside `src/` |
| Destructive git operations require explicit user confirmation | `governance/git_workflow.md` | YES | `qa_tests/test_git_policy.py` — assert `push --force`, `reset --hard`, `checkout .`, `restore .`, `clean -f`, `branch -D` are never called without user prompt |
| No commits without explicit user request | `governance/git_workflow.md` | YES | `qa_tests/test_git_policy.py` — verify no auto-commit logic exists in agent code; check `src/agents/` for unauthorized `git commit` calls |
| L5 gate: user confirmation required for orchestrator redesign, backend switch, external provider opt-in | `governance/execution_protocol.md` | YES | `qa_tests/test_escalation_levels.py` — assert that any action classified L5 emits a HALT signal and does not proceed autonomously |
| Ollama must be available before L1+ work begins (OllamaFreeze rule) | `governance/ollama_integration.md` | YES | `qa_tests/test_ollama_freeze.py` — mock `OllamaClient.is_available()` returning False; assert `OllamaUnavailableError` is raised and no partial implementation proceeds |
| QA gate must pass before any risky work (refactors, routing changes, schema edits) | `governance/qa_gate_policy.md` | YES | `scripts/gate.sh` — run `python3 -m pytest qa_tests/ -q && python3 -m pytest tests/ -q`; gate is PR-blocking |
| Each file has exactly one owner agent; no silent cross-domain edits | `governance/file_ownership.md` | YES | `qa_tests/test_file_ownership.py` — parse ownership table and assert no agent touches files outside its declared ownership list |
| Security redaction must run before sharing logs/evidence externally | `governance/security_redaction_policy.md` | YES | `qa_tests/test_redaction_policy.py` — assert that any evidence export pipeline calls `security_redactor` before writing to a shareable location |
| Plans must conform to PlanSpec: goal + constraints + tasks + acceptance criteria + risk | `governance/planning_policy.md` | YES | `qa_tests/test_plan_schema.py` — load all `Docs/Plans/*.md` and validate required fields are present using `plan_lint` |
| Model escalation follows small-first: Oodle S → M → L → Claude Haiku → Sonnet → Higher | `governance/model_escalation_policy.md` | YES | `qa_tests/test_model_routing.py` — assert Personaler routing dict never jumps tiers; verify `recommend_escalation` logic matches thresholds in policy |
| All write operations default to dry-run unless `--apply` flag is explicitly passed | `policies/hardlines.yaml` | YES | `qa_tests/test_dry_run_default.py` — verify all skill runner invocations check for `--apply` flag before mutating filesystem state |
| Sensitive files (`.env`, credentials) must never be committed | `governance/git_workflow.md` | YES | `qa_tests/test_secret_scan.py` — run `security_redactor` on staged files; assert no token/key patterns are present |
| Task archival (BP-005) must run after plan reaches IMPLEMENTED or CLOSED | `governance/task_archival.md` | PARTIAL | Manual audit: check that `.claude/knowledge/decisions.md` and `Docs/References/` are updated after each closed plan; automated check pending `test_task_archival.py` |
| Governance changes require L4 Systemic Critic review | `governance/decision_policy.md` | YES | `qa_tests/test_escalation_levels.py` — assert that any PR touching `.claude/governance/*.md` triggers L4 escalation check |

---

## Testability Key

- **YES** — automated test exists or can be created deterministically
- **PARTIAL** — partially automatable; some checks require manual audit
- **NO** — policy is enforced by process/review only; no automated check feasible

---

## Related Files

- `policies/hardlines.yaml` — machine-readable hardlines for tool integrations
- `policies/audit_log_template.md` — decision log entry template
- `policies/VIOLATION_REPORT_TEMPLATE.md` — violation report template
- `governance/qa_gate_policy.md` — gate definition and failure protocol
- `governance/execution_protocol.md` — canonical execution flow including L5 gates
