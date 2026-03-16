# MVP Phase 23 — Evidence & Redaction Pipeline (Shareable Exports)

**Goal:** Create a deterministic evidence pipeline that can export runtime artifacts safely (redacted) for sharing/debugging without leaking secrets or machine-specific paths.

**Why now:** With LocalAI, routing, telemetry, and evals, artifacts will grow quickly. We need a stable export mechanism and a policy that keeps sensitive data out of exports.

---

## Definition of Done

- [x] A canonical evidence layout exists under the runtime root (Phase 19)
- [x] A deterministic exporter creates a redacted bundle (zip) under `redacted_exports/`
- [x] Redaction rules exist and are tested (paths, secrets, tokens, PII-like patterns)
- [x] Export bundles include a manifest describing contents + hashes
- [x] A gate prevents “unredacted export” in CI (or marks it as unsafe)
- [x] All existing tests pass

---

## E23.1 — Evidence Bundle Spec

**Files:**
- `Docs/evidence_bundle_spec.md` (new)
- Runtime root README (Phase 19)

**Change:**
- Define what goes into evidence bundles:
  - telemetry (jsonl)
  - eval summaries
  - routing decisions
  - selected artifacts (images/audio snippets) OR hashes/references
- Define required metadata:
  - timestamp, version, host fingerprint (redacted), schema versions

**Acceptance:**
- Spec is stable and referenced by tooling.

---

## E23.2 — Redaction Rules + Engine

**Files:**
- `claudeclockwork/core/redaction/rules.py` (new)
- `claudeclockwork/core/redaction/engine.py` (new)
- `tests/test_redaction.py`

**Change:**
- Implement redaction engine:
  - pattern-based replacement (tokens, API keys, emails)
  - path normalization (replace absolute paths with placeholders)
  - optional allowlist for safe values

**Acceptance:**
- Tests prove secrets/paths are removed.
- Output remains valid JSON/text.

---

## E23.3 — Deterministic Exporter

**Files:**
- `claudeclockwork/cli/export_evidence.py` (or CLI module)
- `tests/test_export_evidence.py`

**Change:**
- Exporter collects allowed files, redacts, writes:
  - `bundle_manifest.json` (hashes, sizes, sources)
  - `bundle.zip` (stable ordering, stable metadata)

**Acceptance:**
- Same inputs produce identical bundle hashes (where feasible).

---

## E23.4 — Policy & Gate Integration

**Files:**
- `Docs/security_export_policy.md` (new)
- `release_check` / `qa_gate` integration

**Change:**
- Add a rule: exports must be redacted unless explicitly running in “unsafe local mode”.
- CI enforces redacted-only exports.

**Acceptance:**
- Gate fails if an unredacted bundle is produced in CI context.

---
