# Task: Policy Gate Check (tool-first)

## Goal
Deterministically decide whether a requested action is allowed:
- deep_oodle
- creative_feedback
- rebuild
- experiment
- no_llm_check

## How
Create a PolicyGateRequest and run skill `policy_gatekeeper`.

## Output
PolicyGateDecision (allowed/blocked + reason + alternative).
