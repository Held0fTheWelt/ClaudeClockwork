# Feedback Policy (Decision Feedback Loop)

This policy defines default feedback modes per role to keep costs low and feedback useful.

## Modes
- strict: only clear rule violations + 1 fix
- balanced: up to 3 concrete improvements (default)
- creative: 3 alternatives + 1 bold option (still capped)

## Budget
- tool_only: deterministic (default)
- tool_then_deep_oodle: allow local deep reasoning if triggers fire

## Default per role
- personaler: balanced
- content_packer: strict
- testops_orchestrator: balanced
- critic_dispatcher: strict
- team_lead: balanced

## Deep Oodle triggers
Deep Oodle stage is allowed only if:
- repeat_failures >= 3, OR
- drift_events >= 2, OR
- over_escalations >= 2, OR
- explicit_deep_review=true


## Local overrides
You can override modes/budgets per role locally via:
- `tools/menus/feedback_policy_menu.py`
- `.claude/settings.local.json` (feedback.overrides)
