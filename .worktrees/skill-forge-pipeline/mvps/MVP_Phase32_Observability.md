# MVP Phase 32 — Observability (Telemetry, Debug, Forensics)

**Goal:** Provide a clear, deterministic observability layer: standardized telemetry events, failure taxonomy, summaries, and “incident bundles” for debugging (redacted).

**Why now:** With DAG runs (Phase 30) and learning (Phase 31), you need consistent visibility into what happened and why.

---

## Definition of Done

- [x] Telemetry schema is standardized (events/spans)
- [x] Failure taxonomy exists (typed errors with reason codes)
- [x] CLI summaries exist:
  - “top failures last N runs”
  - “regressions since last release”
- [x] Incident bundle exporter exists (redacted, subset of evidence)
- [x] Tests cover telemetry parsing + summary generation
- [x] All existing tests pass

---

## O32.1 — Telemetry Schema + Writer

**Files:**
- `.claude/contracts/schemas/telemetry_event.schema.json` (new)
- `claudeclockwork/telemetry/writer.py`

**Change:**
- Define event structure with stable fields:
  - run_id, node_id, capability, duration, status, error_codes

**Acceptance:**
- Events validate and write to JSONL with stable ordering.

---

## O32.2 — Failure Taxonomy + Error Codes

**Files:**
- `Docs/failure_taxonomy.md` (new)
- `claudeclockwork/core/errors.py` (or similar)

**Change:**
- Standardize error codes:
  - dependency_missing
  - policy_denied
  - timeout
  - validation_failed
  - regression_blocked

**Acceptance:**
- Errors are consistent across skills, runners, router, and workgraph.

---

## O32.3 — CLI Summaries

**Files:**
- `claudeclockwork/cli/telemetry_summary.py`
- `tests/test_telemetry_summary.py`

**Change:**
- Parse telemetry JSONL and output deterministic summaries.

**Acceptance:**
- Same telemetry yields identical summary output.

---

## O32.4 — Incident Bundle Export (Redacted)

**Files:**
- Export pipeline (Phase 23)
- `claudeclockwork/cli/export_incident.py`

**Change:**
- Export a targeted subset around a failed run:
  - last N events
  - failing node artifacts
  - environment check output

**Acceptance:**
- Bundle is redacted and includes a manifest.

---
