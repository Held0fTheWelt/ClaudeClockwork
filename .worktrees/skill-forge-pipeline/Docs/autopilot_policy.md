# SLO Autopilot Policy Contract (Phase 51)

When an SLO gate fails, the autopilot may apply deterministic mitigations per policy.

## Policy shape

- **trigger:** `slo_fail` (failure rate or p95 latency breach)
- **actions:** Ordered list of action types with optional params. Supported: `budget_switch`, `reroute`, `disable_plugin`, `rollback`, `incident_export`
- **guardrails:** Max actions per run; no destructive actions without explicit policy

## Action types

| Action | Params | Effect |
|--------|--------|--------|
| budget_switch | profile: string | Switch to a different budget profile (e.g. fast) |
| reroute | capability: string | Reroute capability to another runner |
| disable_plugin | plugin_id: string | Disable plugin until next review |
| rollback | target: string | Rollback to last known good (if available) |
| incident_export | path: string | Export incident bundle to path |

All actions are logged to telemetry. Execution is best-effort and ordered.
