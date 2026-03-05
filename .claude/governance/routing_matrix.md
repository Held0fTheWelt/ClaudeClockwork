# Routing Matrix (v1)

Diese Matrix ist **Default-Standardrouting**. Änderungen erfolgen über den Prozess:
`Report/QualitySignal -> CriticReport -> Team_Lead -> (Agent Coaching | Personaler Matrix Patch | Edge-Case Route)`.

## Eskalation
1) **Oodle Tier erhöhen** (O0→O1→O2/O3)
2) erst danach **Claude Tier erhöhen** (C0→C1→C2→C3)
- **Opus 4.6 (C4) default OFF**, nur manuell.

## Trust Modes
- inherit / verify / rebuild (siehe `.claude/contracts/SPEC_SHEET.md`)

## Departments (Kurz)
- management.routing (Personaler)
- operations.packing (Content Packer)
- operations.observability (Ops Ledger)
- engineering.implementation (Implementation Worker)
- quality.testops (TestOps + TestRunner)
- docs.reporting (Report Worker)
- quality.review (Critic/Governance)

## Schnellregeln
- Admin/Diener: C0 oder O0, Verifier O1
- Coding: O2, Verifier O1 (oder O3 bei risk hoch)
- Hard reasoning: O3, Verifier C2 (oder C3 bei “entscheidend”)
- Tests: deterministic runner + TestRunner(O0/O1/O3) + parallel Report Worker

## operations.observability (Ops Ledger)
- Primary: O1 (Event Logging)
- Aggregation: O3 (Summary)
- Claude: C0 default, C2 nur bei expliziter Anfrage
- Summary Trigger: run_end ODER repeat_failures>=2 ODER drift_events>=1 ODER over_escalations>=1

> Für Details: nutze die Contracts in `.claude/contracts/`.

## Bulk work pattern (cheap doer + local verifier)
- Use cheap Claude (C0/C1) as Doer/Relay for repetitive jobs.
- Use deterministic skills/tools for validation.
- Use Local Verifier O3 only on compact evidence bundles.

