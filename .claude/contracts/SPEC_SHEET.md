# Contracts & Specs — Overview (v1)

Diese Datei definiert die **verbindlichen Contracts** zwischen Orchestrator, SpecialAgents und Workern.
Ziel: **kleiner Context**, **deterministisches Routing**, **reproduzierbare QA/Eskalation**.

**Hinweis:** Dies ist eine **kuratierte Shortlist** der zentralen Pipeline-Specs. Die vollständige Menge aller Specs liegt in `.claude/contracts/schemas/` (derzeit ~95 JSON-Schema-Dateien). Für die komplette Liste siehe dieses Verzeichnis; SPEC_SHEET dient als Einstieg und Pipeline-Überblick.

## Grundregeln
- Jeder Agent arbeitet primär auf **Pack + Spec**, nicht auf der vollen Original-Nachricht.
- Freitext ist erlaubt, aber nur in `notes` / `rationale`. Kernfelder bleiben maschinenlesbar.
- Eskalation: **erst Oodle Tier erhöhen**, **danach Claude Tier erhöhen** (Opus 4.6 default OFF).

## Spezifikationen (Shortlist)
1. TasklistSpec — Output vom Task Compactor
2. RoutingSpec — Output vom Personaler/Team_Lead
3. PackManifest — Output vom Content Packer
4. FixPlanSpec — Output vom TestRunner / Debug Worker
5. TestReportSpec — Output vom Runner/TestOps
6. ReportSpec — Output vom Report Worker
7. QualitySignal — kompaktes Signal vom Report Worker
8. CriticReport — Output vom Kritiker
9. OpsLedgerEvent / OpsLedgerSummary — Output vom Ops Ledger (Department Lead)

> JSON Schemas: **alle** in `.claude/contracts/schemas/` (~95 Dateien). Diese Shortlist deckt die Kern-Pipeline ab; weitere Schemas (Skills, Ops, Ideation, etc.) siehe Verzeichnis.

## Tier-Notation
- Oodle: `O0|O1|O2|O3`
- Claude: `C0|C1|C2|C3|C4`

## Trust Modes
- `inherit`: vertraut TasklistSpec + Pack
- `verify`: zusätzlich kleiner Goal/Constraints Snapshot
- `rebuild`: liest Originalmessage (teuer)

## Minimaler Pipeline-Fluss
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
