# Task: Autotune Post-Run (tool-first)

## Goal
Suggest small routing improvements based on historical outcomes.

## How
1) Append an OutcomeLedgerEvent using `outcome_ledger_append`.
2) Run `route_autotune_suggest` to get up to 3 suggestions.
3) If approved, turn them into RouteProfileSpec updates (manual or via existing route_profile_update skill).

## Output
- RouteAutotuneSuggestion (JSON in skill output)
