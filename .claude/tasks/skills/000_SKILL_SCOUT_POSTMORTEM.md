# Task: Skill Scout Postmortem (project-agnostic)

## When to run
- End of a run, or when repeat_failures >= 2, or when OpsLedger flags waste/drift.

## Inputs
Provide compact evidence only:
- OpsLedgerSummary
- ReportSpec + QualitySignal
- TasklistSpec (optional)
- CriticReport (optional)

## Output
- SkillOpportunityReport (max 3 candidates)
- If a candidate is marked `build_skill`, ask for explicit confirmation before forwarding to Skill Planning Agent.
