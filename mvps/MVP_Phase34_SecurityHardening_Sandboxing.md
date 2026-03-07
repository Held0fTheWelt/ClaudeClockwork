# MVP Phase 34 — Security Hardening & Sandboxing (Real Isolation)

**Goal:** Introduce real isolation for execution paths (external runners, plugins, local tools) beyond policy checks: path jails, process sandboxing, stricter secret handling, and CI-verifiable escape prevention.

**Why now:** With Plugins (Phase 29), Work Graphs (Phase 30), LocalAI (Phase 20/24), and Workspaces (Phase 33), policy-only enforcement becomes brittle. This phase adds OS-adjacent guardrails.

---

## Definition of Done

- [x] Path jail enforcement exists for runtime writes/reads (deny-by-default outside allowed roots)
- [x] External runner invocations are sandboxed (structured argv only, no shell; optional OS sandbox)
- [x] Secret handling is centralized (redaction + allowlist; no accidental logging)
- [x] “Unsafe mode” exists only as an explicit local override (clearly logged; blocked in CI)
- [x] Escape attempts are detected and fail deterministic gates
- [x] Tests cover sandbox policy, path jail, and unsafe-mode blocking in CI
- [x] All existing tests pass

---

## S34.1 — Path Jail (Read/Write Boundaries)

**Files:**
- `claudeclockwork/workspace/boundary.py` (Phase 33) or new `claudeclockwork/core/path_jail.py`
- `tests/test_path_jail.py`

**Change:**
- Enforce that all file operations are within:
  - project root (read)
  - runtime root (read/write)
  - explicit allowlisted paths (read-only)
- Deny and log any attempt to access outside.

**Acceptance:**
- Attempting to write to `../` or absolute paths fails with `policy_denied`.

---

## S34.2 — External Runner Sandboxing

**Files:**
- `claudeclockwork/localai/runners/external.py` (Phase 24)
- `Docs/external_runner_sandbox.md` (new)
- `tests/test_external_runner_sandbox.py`

**Change:**
- Enforce:
  - structured argv (no shell strings)
  - allowlisted binaries and args templates
  - working directory restrictions (runtime root)
  - timeout and memory hints (best-effort)
- Optional: OS-specific sandbox wrappers (disabled by default).

**Acceptance:**
- Non-allowlisted binary or argument pattern is blocked deterministically.

---

## S34.3 — Secrets + Redaction Hardening

**Files:**
- Redaction engine (Phase 23)
- `claudeclockwork/core/secrets/store.py` (new)
- `tests/test_secrets_redaction.py`

**Change:**
- Provide a single secrets interface:
  - load from env or config
  - never print raw values
  - redact by default in logs/telemetry
- Add a “secret leak detector” test that scans telemetry outputs for patterns.

**Acceptance:**
- Known secret patterns are never present in runtime logs or exports.

---

## S34.4 — Unsafe Mode Policy

**Files:**
- `Docs/unsafe_mode.md` (new)
- Gate integration (`release_check` / `qa_gate`)

**Change:**
- Unsafe mode requires explicit flag + local environment confirmation.
- CI forbids unsafe mode entirely.

**Acceptance:**
- Gate fails if unsafe mode is enabled in CI context.

---

## S34.5 — Escape Attempt Gate

**Files:**
- `claudeclockwork/core/gates/security_escape_gate.py` (new)
- `tests/test_security_escape_gate.py`

**Change:**
- Gate checks for:
  - forbidden path accesses
  - forbidden binaries
  - unredacted secrets in logs
  - writes outside runtime root

**Acceptance:**
- Synthetic escape attempts fail the gate with precise reason codes.

---
