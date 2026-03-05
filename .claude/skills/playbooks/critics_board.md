# Critics Board Playbook

Goal: turn the critic system into a valuable, multi-angle review.

## Roles
- Systemic: architecture, system-level consistency
- Technical: correctness, maintainability, testability
- Legal: GDPR/privacy, licensing, compliance
- Security: threat model, secrets, auth, supply chain
- Moral: harm/misuse, safety guardrails
- Creative: missing ideas to flesh out the concept
- Methodical: better work methods, cheaper/faster process

## Output format
Each critic outputs a JSON snippet into:
`.claude-performance/reviews/<run_id>_critics.json`

Recommended keys:
- `risk_0_10`
- `confidence_0_10`
- `notes`
- `recommendations` (list)

## Consolidation
Run `critics_board_review` to:
- merge all critic notes
- compute overall risk and top priorities
- export a report + chart
