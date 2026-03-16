# Budgeting Policy (v17.6)

## Goal
Keep costs predictable by selecting tiers deterministically.

## Tool
Use `budget_router` with:
- complexity (0–5)
- risk (0–5)
- urgency (0–5)
- mode: cheap | balanced | deep

## Output
A recommendation containing:
- Oodle tier
- Claude tier
- allow_deep / allow_external
- max_context_kb

## Rule of thumb
- Default: balanced
- Use deep only with Policy Gate approval when needed
