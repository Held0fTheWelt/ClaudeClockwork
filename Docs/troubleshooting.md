# Troubleshooting by Error Code

Aligned to [failure_taxonomy.md](failure_taxonomy.md). For each code: cause, check, fix, and when to escalate.

---

## dependency_missing

**Meaning:** Required tool or dependency not installed.

**Checks:**
- Run `clockwork env-check` and inspect `errors` and `info`.
- Confirm Python 3.10+ and required packages (see [install.md](install.md)).

**Fix:**
- Install missing package: `pip install <package>`.
- If Ollama is required: start Ollama and ensure `http://localhost:11434` is reachable.

**Escalate:** If the missing dependency is optional and you need the feature, enable it per [install.md](install.md).

---

## policy_denied

**Meaning:** Capability or path denied by policy.

**Checks:**
- Inspect `.claude/config/permissions.json` and project policy files.
- Check path jail and workspace guards (see [workspace_federation.md](workspace_federation.md)).

**Fix:**
- Adjust policy to allow the capability or path, or run from a project that permits it.
- Do not disable security guards in production without review.

**Escalate:** For org-wide policy changes, follow governance (Designer/Team Lead).

---

## timeout

**Meaning:** Operation exceeded time limit.

**Checks:**
- Check telemetry or logs for which step timed out.
- Confirm resource limits (CPU, network) and external service health.

**Fix:**
- Increase timeout in config if appropriate, or optimize the step.
- For LLM calls: ensure model is loaded and endpoint responsive.

**Escalate:** Recurring timeouts on critical paths → SLO review and capacity.

---

## validation_failed

**Meaning:** Input or output validation failed.

**Checks:**
- Inspect skill/plugin input schema and CLI `--inputs` JSON.
- Check contract schemas under `.claude/contracts/schemas/`.

**Fix:**
- Correct input shape or fix the step output to match the expected schema.
- Run with valid sample payload to confirm.

**Escalate:** Schema bugs → update contract and migration if needed (see [semver_policy.md](semver_policy.md)).

---

## regression_blocked

**Meaning:** Regression gate blocked the change.

**Checks:**
- Review gate output (eval regression, cost/perf, SLO gates).
- See [eval_scoreboards.md](eval_scoreboards.md) and [cost_model.md](cost_model.md).

**Fix:**
- Address the regression (revert or fix) before re-running the gate.
- Do not bypass gates without explicit approval.

**Escalate:** Gate false positive → adjust gate thresholds or scope with Team Lead.

---

## unknown_capability

**Meaning:** Capability not in registry.

**Checks:**
- List capabilities: run skill registry search or check manifest discovery.
- Confirm plugin/skill is installed and manifest valid.

**Fix:**
- Install or enable the plugin/skill; fix manifest path and schema.

**Escalate:** New capability rollout → follow plugin/skill onboarding docs.

---

## runner_unavailable

**Meaning:** No runner for capability.

**Checks:**
- Confirm LocalAI/router config and runner registration.
- Check worker status and dispatcher logs.

**Fix:**
- Start or register the runner; fix config so the capability is bound to a runner.

**Escalate:** Fleet/runner design → see [worker_protocol.md](worker_protocol.md) and [remote_worker_stub.md](remote_worker_stub.md).
