# MVP Phase 42 — Operational UX v2 (Incidents, Dashboards, Drilldowns)

**Goal:** Make operations and debugging fast: incident views, drilldowns by node/worker/tool, dashboards for regressions, cache hit rates, and cost burn.

**Why now:** After Reliability (39) and Optimization (41), you need visibility. Without UX, you cannot maintain SLOs or trust optimization outcomes.

---

## Definition of Done

- [x] Incident view exists: “why did this run fail?”
- [x] Drilldowns exist: node timeline, worker timeline, tool timeline
- [x] Dashboards exist (CLI-first):
  - last N runs
  - top failures
  - regressions since last release
  - cache hit rate
  - cost burn by budget profile
- [x] Incident bundle export integrates (Phase 23/32)
- [x] Output is deterministic and stable-ordered
- [x] All existing tests pass

---

## U42.1 — Incident View Command

**Files:**
- `claudeclockwork/cli/incidents.py` (new)
- `tests/test_incidents_cli.py`

**Change:**
- Parse telemetry and workgraph metadata to summarize:
  - failed node
  - error codes
  - recovery actions taken
  - suggested next step (link to docs)

**Acceptance:**
- Same telemetry yields identical incident summary output.

---

## U42.2 — Drilldown Views

**Files:**
- `claudeclockwork/cli/drilldown.py` (new)
- `Docs/drilldowns.md` (new)

**Change:**
- Provide subcommands:
  - `drilldown node <id>`
  - `drilldown worker <id>`
  - `drilldown tool <id>`
- Show timeline + key artifacts (paths).

**Acceptance:**
- Drilldown output is deterministic and references repo-local paths.

---

## U42.3 — Dashboards (CLI)

**Files:**
- `claudeclockwork/cli/dashboard.py` (new)
- `Docs/dashboards.md` (new)
- `tests/test_dashboard_output.py`

**Change:**
- Generate stable tables for key metrics.

**Acceptance:**
- Ordering is stable (sort by timestamp, then id).

---

## U42.4 — Integrate Incident Bundle Export

**Files:**
- Export pipeline (Phase 23/32)
- `claudeclockwork/cli/export_incident.py` (existing if present)

**Change:**
- Ensure dashboards and incident views can export a targeted redacted incident bundle.

**Acceptance:**
- Export command produces a redacted bundle with a manifest.

---
