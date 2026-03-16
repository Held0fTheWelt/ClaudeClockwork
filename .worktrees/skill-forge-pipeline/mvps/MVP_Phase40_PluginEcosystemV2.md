# MVP Phase 40 — Plugin Ecosystem v2 (Signing, Compatibility Matrix, Test Harness)

**Goal:** Make plugins safe to adopt: compatibility checks, signing/hash allowlists, mandatory test harness, and a compatibility matrix tied to Clockwork versions.

**Why now:** Plugin API exists (Phase 29), but without strict safety + compatibility controls, the ecosystem will become fragile and risky.

---

## Definition of Done

- [x] Plugin signing or hash allowlist mechanism exists (deterministic, repo-local)
- [x] Compatibility matrix exists (Clockwork version ↔ plugin versions)
- [x] Plugin validation requires a minimal test harness (smoke + policy compliance)
- [x] Plugin loader rejects:
  - incompatible versions
  - unsigned/unallowlisted plugins (in strict mode)
  - missing tests
- [x] Documentation exists for publishing and validating plugins
- [x] All existing tests pass

---

## P40.1 — Plugin Signature/Hash Allowlist

**Files:**
- `Docs/plugin_signing.md` (new)
- `claudeclockwork/plugins/signing.py` (new)
- `tests/test_plugin_signing.py`

**Change:**
- Start with hash allowlists:
  - allowlist file under repo root or workspace config
  - plugin manifest includes declared hash
- Optional: introduce real signatures later.

**Acceptance:**
- Modified plugin content changes hash and is rejected in strict mode.

---

## P40.2 — Compatibility Matrix

**Files:**
- `Docs/plugin_compatibility.md` (new)
- `claudeclockwork/plugins/compat.py`
- `tests/test_plugin_compat.py`

**Change:**
- Enforce semantic version constraints declared in plugin manifest.
- Maintain a generated compatibility report.

**Acceptance:**
- Incompatible plugin is rejected with a clear error.

---

## P40.3 — Plugin Test Harness Requirement

**Files:**
- `Docs/plugin_tests.md` (new)
- `claudeclockwork/plugins/test_harness.py`
- `tests/test_plugin_test_harness.py`

**Change:**
- Require plugins to ship:
  - smoke test definition (manifest-declared)
  - policy compliance check
- Provide a runner to execute these deterministically.

**Acceptance:**
- Plugin without tests is rejected (or warned) according to policy.

---

## P40.4 — Registry / Index (Local)

**Files:**
- `Docs/plugin_registry.md` (new)
- `claudeclockwork/plugins/registry_index.py` (new)

**Change:**
- Provide a local “registry index” file listing available plugins and their status:
  - allowed/blocked
  - compatibility result
  - last test run result

**Acceptance:**
- Index output is stable and deterministic.

---
