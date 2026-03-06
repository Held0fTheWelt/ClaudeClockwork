# Routing Matrix (v1)

This matrix is **default standard routing**. Changes occur via the process:
`Report/QualitySignal -> CriticReport -> Team_Lead -> (Agent Coaching | Personaler Matrix Patch | Edge-Case Route)`.

## Escalation
1) **Increase Oodle Tier** (O0→O1→O2/O3)
2) Only then **increase Claude Tier** (C0→C1→C2→C3)
- **Opus 4.6 (C4) default OFF**, manual only.

## Trust Modes
- inherit / verify / rebuild (see `.claude/contracts/SPEC_SHEET.md`)

## Departments (Brief)
- management.routing (Personaler)
- operations.packing (Content Packer)
- operations.observability (Ops Ledger)
- engineering.implementation (Implementation Worker)
- quality.testops (TestOps + TestRunner)
- docs.reporting (Report Worker)
- quality.review (Critic/Governance)

## Quick Rules
- Admin/Servant: C0 or O0, Verifier O1
- Coding: O2, Verifier O1 (or O3 for high risk)
- Hard reasoning: O3, Verifier C2 (or C3 for "decisive")
- Tests: deterministic runner + TestRunner(O0/O1/O3) + parallel Report Worker

## operations.observability (Ops Ledger)
- Primary: O1 (Event Logging)
- Aggregation: O3 (Summary)
- Claude: C0 default, C2 only on explicit request
- Summary Trigger: run_end OR repeat_failures>=2 OR drift_events>=1 OR over_escalations>=1

> For details: use the contracts in `.claude/contracts/`.

## Bulk work pattern (cheap doer + local verifier)
- Use cheap Claude (C0/C1) as Doer/Relay for repetitive jobs.
- Use deterministic skills/tools for validation.
- Use Local Verifier O3 only on compact evidence bundles.
