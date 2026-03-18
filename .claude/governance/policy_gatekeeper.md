# Policy Gatekeeper (Tool-first)

Purpose: central, deterministic enforcement of key policies to prevent drift.

## What it gates
- Deep Reasoning Mode
- Creative feedback
- Rebuild trust_mode
- Experiment Budget
- No-LLM Mode compliance

## Inputs (compact)
- settings.local.json (optional)
- signals: repeat_failures, drift_events, over_escalations, risk, explicit flags
- requested_action: deep_reasoning / creative_feedback / rebuild / experiment / no_llm

## Output
- allowed: true/false
- reason (short)
- suggested alternative (short)

## Rule priority (highest first)
1) No-LLM mode enabled => only tool-only actions allowed (except explicit relay).
2) Safety gates: rebuild and deep_reasoning require triggers.
3) Budget gates: experiment count and feedback creativity capped.
4) Default allow: strict/balanced tool-first actions.
