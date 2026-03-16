# Task: Decision Feedback (Post-Run)

## Goal
Give the Personaler (or other roles) feedback on routing decisions and used resources.

## How (tool-first)
1) Provide compact evidence paths:
   - RoutingSpec
   - OpsLedgerSummary
   - QualitySignal
   - optional CriticReport
2) Create a FeedbackRequestSpec for the recipient role.
3) Run skill `decision_feedback`.

## Output
- DecisionFeedbackSpec (keep/adjust/escalate)
- Max 3 recommendations (mode-aware)

## Defaults
Use the defaults in `governance/feedback_policy.md`.
