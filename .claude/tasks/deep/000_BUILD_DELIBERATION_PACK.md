# Task: Build Deliberation Pack (tool-first)

## Goal
Prepare a compact evidence pack for Deep Oodle reasoning (slow but strong models).

## How
Run skill `deliberation_pack_build` with paths to compact evidence:
- PlanSpec
- RoutingSpec
- QualitySignal
- OpsLedgerSummary
- optional CriticReport
- up to 5 log files

## Output
- DeliberationPackSpec JSON (in skill output)
- Use it as the only input for Deep Oodle Mode reasoning.

## Notes
This keeps Deep Oodle inputs small and improves quality even on slow hardware.
