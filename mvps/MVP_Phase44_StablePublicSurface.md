# MVP Phase 44 — Stable Public Surface (CLI/API Stabilization + SemVer)

**Goal:** Define and enforce a stable public surface for Clockwork: CLI contract, API stability rules, SemVer discipline, and a structured deprecation framework.

**Why now:** After Orchestrator v2 (Phase 43) and Plugin Ecosystem v2 (Phase 40), stability becomes a platform requirement. Uncontrolled interface churn will break plugins, automation, and user workflows.

---

## Definition of Done

- [ ] CLI contract document exists (stable vs experimental commands)
- [ ] Public Python API boundaries are defined (public modules vs internal)
- [ ] SemVer rules are documented and enforced by gates
- [ ] Deprecation framework exists (warn → block → remove)
- [ ] Compatibility tests exist for:
  - CLI flags/outputs
  - config schema versions
- [ ] All existing tests pass

---

## S44.1 — CLI Contract (Stable/Experimental)

**Files:**
- `Docs/cli_contract.md` (new)
- `claudeclockwork/cli/__init__.py` (or existing CLI entry)

**Change:**
- Mark commands as stable vs experimental.
- Define output stability: table headers, JSON keys, exit codes.

**Acceptance:**
- Contract explicitly lists all stable commands and their expected outputs.

---

## S44.2 — Public API Boundary Map

**Files:**
- `Docs/public_api.md` (new)
- `claudeclockwork/__init__.py` (export list)

**Change:**
- Declare which modules are public and versioned.

**Acceptance:**
- A simple “public import” check script can detect accidental public surface expansion.

---

## S44.3 — SemVer + Deprecation Policy

**Files:**
- `Docs/semver_policy.md` (new)
- `Docs/deprecations.md` (new)
- `claudeclockwork/core/gates/public_surface_gate.py` (new)

**Change:**
- Define breaking change rules and deprecation registry.

**Acceptance:**
- Gate fails when stable interfaces change without proper versioning.

---

## S44.4 — Compatibility Tests

**Files:**
- `tests/compat/` (new)

**Change:**
- Snapshot stable CLI output (normalized).
- Validate config migration behavior for at least one old schema version.

**Acceptance:**
- Compatibility tests are deterministic and CI-safe.

---
