# Deep Oodle Mode (Slow but Strong)

This mode prioritizes **quality and reasoning depth** over speed.
It is designed for setups like RTX 3080 + 7950X3D where 70B/72B may be slow but valuable.

## Intent
- Use extreme local reasoning models for:
  - hard design decisions
  - systemic debugging
  - architecture trade-offs
  - final review gates
- Keep cheap Claude for execution/relay; do not burn cloud tokens.

## When Deep Oodle Mode is allowed
Deep Oodle Mode is allowed only if one of the following is true:
- risk >= high
- repeat_failures >= 3
- drift_events >= 2
- over_escalations >= 2
- Team_Lead sets `deep_oodle=true`

## Inputs (must be compact)
Deep Oodle must only receive compact evidence:
- PlanSpec (or PlanDiffSpec)
- TasklistSpec (short)
- OpsLedgerSummary
- QualitySignal
- small log snippets (<= 200 lines)

Never pass full chats or entire repos.

## Output
Deep Oodle returns:
- decision (1–3 bullets)
- reasoning summary (<= 12 bullets)
- suggested plan changes (PlanDiffSpec optional)
- verification steps (deterministic, tool-first)


## Recommended input format
Prefer using `DeliberationPackSpec` built via skill `deliberation_pack_build`.

## Cross-links
- Deliberation pack builder: `tools/skills/deliberation_pack_build.py`
- Evidence router: `tools/skills/evidence_router.py`
- Policy gatekeeper: `policy_gatekeeper.md`

