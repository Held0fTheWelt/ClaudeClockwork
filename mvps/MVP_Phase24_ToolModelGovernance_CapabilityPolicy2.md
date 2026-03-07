# MVP Phase 24 — Tool/Model Governance (Capability Policy 2.0)

**Goal:** Extend capability enforcement so LocalAI and external runners are safe-by-default: strict allowlists, parameter schemas, resource limits, and complete audit logs.

**Why now:** Once LocalAI (Phase 20) is integrated, you need governance: who can run what, with which parameters, on which files, under which resource limits.

---

## Definition of Done

- [ ] A Capability Policy extension exists for LocalAI tool invocations
- [ ] All LocalAI capabilities have parameter schemas and validation
- [ ] Strict allowlists for external command execution exist (no arbitrary shell)
- [ ] Resource limits enforced (timeouts, max file size, concurrency)
- [ ] Complete audit log for tool invocations exists (runtime root)
- [ ] All existing tests pass

---

## G24.1 — Capability Policy Extensions

**Files:**
- Capability policy file(s) in `.claude/` (existing system)
- `Docs/capability_policy_localai.md` (new)

**Change:**
- Add capability namespace rules:
  - `localai.embed.text`, `localai.audio.asr`, etc. (or `embed.text`, `audio.asr` mapped to localai)
- Define which agents/roles may call which capabilities.

**Acceptance:**
- Unauthorized calls are blocked deterministically with a typed error.

---

## G24.2 — Parameter Schemas + Validation

**Files:**
- `.claude/contracts/schemas/*` (LocalAI params)
- `claudeclockwork/localai/validation.py`

**Change:**
- JSON Schema for each capability parameters (including defaults).
- Validate input media types and sizes.

**Acceptance:**
- Invalid params fail fast with actionable errors.

---

## G24.3 — External Runner Allowlist + Sandbox

**Files:**
- `claudeclockwork/localai/runners/external.py`
- `Docs/external_runner_policy.md`

**Change:**
- Allowlist binaries + args templates.
- No raw shell strings; only structured argv.
- Optional sandbox mode (working dir restrictions).

**Acceptance:**
- Attempts to run non-allowlisted commands are blocked.

---

## G24.4 — Resource Limits + Audit Logging

**Files:**
- `claudeclockwork/localai/runtime.py`
- `claudeclockwork/core/audit/localai_audit.py`
- `tests/test_localai_limits.py`

**Change:**
- Timeouts per capability
- Max input sizes
- Concurrency limits
- Write audit record for every invocation (including blocked attempts)

**Acceptance:**
- Limits trigger deterministic typed errors.
- Audit log records include capability, params hash, duration, status.

---
