# Per-Agent Capability Matrix (MVP23-D)

Reference for implementation of `capabilities.yaml` and enforcement in `file_gateway.py` / `sandbox_runner.py`.

| Agent | file_read | file_write | commands | network | git_write | Escalation |
|-------|-----------|------------|----------|---------|-----------|------------|
| team_lead | config, .claude, llamacode, tests | — | git read-only | no | no | L1 |
| tester | tests, qa_tests, llamacode, toml/json | tests, qa_tests, eval results | pytest, python | no | no | L0 |
| designer | ** | docs, quellen, .claude-development, *.md | — | no | no | L2 |
| critic_dispatcher | ** | — | — | no | no | L3 |
| implementation | ** | llamacode, oodle, tests, qa_tests, scripts | pytest, python, git add/commit | no | yes | L1 |
| builder | ** | llamacode, tests, dist, .llama_runtime | python, pip list/show | no | no | L1 |
| librarian | .claude, docs, quellen | .claude/knowledge, .llama_runtime/knowledge | — | no | no | L0 |
| context_packer | ** | — | — | no | no | L0 |

** = broad read for context assembly; write still restricted by path_allowlist.

## Enforcement model

1. **FileGateway** (or wrapper): Before any read/write, resolve current `agent_id` from execution context; load `capabilities.agents[agent_id].capabilities.file_read` / `file_write`; check path against allowed globs and path_allowlist scopes; on violation → deny and write violation to audit log.
2. **SandboxRunner**: Before subprocess, resolve `agent_id`; load `command_allowlist.yaml`; check command + args; if command in `requires_escalation`, check context escalation_level; on violation → deny and audit.
3. **Violation audit format**: `{ "timestamp", "agent_id", "action", "target", "policy_ref", "result": "denied" }` — see Report 04 §3 audit_log.schema.json.

## Out of scope (MVP23-D)

- Actual code changes to file_gateway.py / sandbox_runner.py (MVP24).
- path_allowlist.yaml is specified in Report 04; implementation may merge path rules from capabilities + path_allowlist.
