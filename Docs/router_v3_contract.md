# Router v3 Contract (Phase 26)

Router output is contract-compliant and explainable.

## Output shape

- **chosen_option:** id of the selected model/tool/variant
- **alternatives_considered:** list of option ids that were candidates
- **reason_codes:** list of strings (e.g. `budget`, `latency`, `quality`, `safety`)
- **confidence:** float in [0,1] or null
- **expected_cost:** optional cost/latency estimate
- **budget_level:** applied budget (`fast` | `balanced` | `strong`)

## Rationale

Every decision includes a rationale payload so that:
- CI and eval can attribute outcomes to router choices
- Safety constraints are auditable (reason_codes include `safety` when a block applied)

## Compatibility

Used by bandit policy (Phase 26), eval harness (Phase 25), and capability policy (Phase 24).
