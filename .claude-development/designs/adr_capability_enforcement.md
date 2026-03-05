# ADR: Capability Policy Enforcement Mechanism

**Status:** Accepted (Design)  
**Date:** 2026-03-02  
**Context:** MVP23-D — Capability Policy Design  
**Deciders:** Team Lead, M2 Design Sprint

---

## Context

Report 04 (Security & Safety Review) specifies per-agent capability manifests (`capabilities.yaml`), command allowlist (`command_allowlist.yaml`), and path allowlist (`path_allowlist.yaml`) to mitigate T-003 (arbitrary command execution) and T-004 (file system traversal). These were never created or wired. Before implementation we need a single enforcement model.

## Decision

1. **Single source of truth:** `.claude/policies/capabilities.yaml` defines per-agent capabilities (file_read, file_write, commands, network, git_write). `.claude/policies/command_allowlist.yaml` defines allowed/denied shell commands and escalation requirements. `.claude/policies/path_allowlist.yaml` defines scopes (project_read, project_write, runtime_write, clockwork_read) used by FileGateway. Capabilities reference path scopes where useful (e.g. file_write: "project_write").
2. **Enforcement points:**
   - **FileGateway** (oodle/llamacode): Before `import_file` / overwrite, resolve `agent_id` from caller context (thread-local or explicit parameter). Load agent's file_read/file_write from capabilities; resolve path against path_allowlist scopes; deny if path not allowed. Log violation with audit_log.schema.json shape.
   - **SandboxRunner**: Before executing a command, resolve agent_id; load command_allowlist; check command pattern and args_allowlist/args_denylist; if command in requires_escalation, check context escalation_level (e.g. L4+ allows). Deny and audit on violation.
3. **Default-deny:** If agent_id is missing or not in capabilities.yaml, treat as most restrictive (no file_write, no commands).
4. **Violation audit format:** Use the audit log entry format from Report 04 §3 (event_type, agent, action, target, result: "denied", policy_ref). No cryptographic chaining in MVP24; add in MVP26 (Security Hardening).

## Consequences

- **Positive:** Clear contract; one place to add new agents or tighten commands; audit trail for every denial.
- **Negative:** All callers of FileGateway and SandboxRunner must pass agent context; legacy code paths may need a "system" or "gate" agent for non-agent invocations.
- **Follow-up:** MVP24 implements capability_enforcer.py and wires file_gateway + sandbox_runner; MVP26 adds audit chaining and budget circuit breaker.
