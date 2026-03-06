# Contracts & Specs — Overview (v1)

This file defines the **binding contracts** between Orchestrator, SpecialAgents, and Workers.
Goal: **small context**, **deterministic routing**, **reproducible QA/escalation**.

**Note:** This is a **curated shortlist** of the central pipeline specs. The complete set of all specs is in `.claude/contracts/schemas/` (currently ~95 JSON schema files). For the complete list, see that directory; SPEC_SHEET serves as entry point and pipeline overview.

## Core Rules
- Every agent works primarily on **Pack + Spec**, not on the full original message.
- Free text is allowed, but only in `notes` / `rationale`. Core fields remain machine-readable.
- Escalation: **first increase Oodle tier**, **then increase Claude tier** (Opus 4.6 default OFF).

## Specifications (Shortlist)
1. TasklistSpec — Output from Task Compactor
2. RoutingSpec — Output from Personaler/Team_Lead
3. PackManifest — Output from Content Packer
4. FixPlanSpec — Output from TestRunner / Debug Worker
5. TestReportSpec — Output from Runner/TestOps
6. ReportSpec — Output from Report Worker
7. QualitySignal — Compact signal from Report Worker
8. CriticReport — Output from Critic
9. OpsLedgerEvent / OpsLedgerSummary — Output from Ops Ledger (Department Lead)

> JSON Schemas: **all** in `.claude/contracts/schemas/` (~95 files). This shortlist covers the core pipeline; additional schemas (Skills, Ops, Ideation, etc.) see directory.

## Tier Notation
- Oodle: `O0|O1|O2|O3`
- Claude: `C0|C1|C2|C3|C4`

## Trust Modes
- `inherit`: trusts TasklistSpec + Pack
- `verify`: additionally small Goal/Constraints snapshot
- `rebuild`: reads original message (expensive)

## Minimal Pipeline Flow
`Message -> TasklistSpec -> RoutingSpec -> PackManifest (+Pack) -> WorkerResult -> ReportSpec/QualitySignal -> CriticReport (optional) -> OpsLedgerSummary`

## Additional specs (v17.6)
10. EvidenceBundleManifest — output of `evidence_bundle_build`
11. RedactionReport — output of `security_redactor`
12. CapabilityMap — output of `capability_map_build`

## Additional specs (v17.7)
13. DocWriteSpec — inputs for `doc_write` (persist docs + diff)
14. TutorialWriteSpec — inputs for `tutorial_write` (spec-first tutorial)
15. DocReviewReport — outputs from `doc_review` (lint findings)
16. RepoCompareReport — outputs from `repo_compare` (added/removed/changed)
17. ScreencastScriptSpec — inputs for `screencast_script` (chapters + shot list)
