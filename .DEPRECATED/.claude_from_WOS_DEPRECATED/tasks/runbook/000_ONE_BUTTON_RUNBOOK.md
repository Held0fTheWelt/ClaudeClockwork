# One-Button Runbook (tool-first)

## Goal
Run a complete health + feedback pass with minimal token spend.
This is the default "press once" workflow.

## Modes
- Normal mode: tools + optional relay
- No-LLM mode: tools only (see `governance/no_llm_mode.md`)


## STOP CONDITIONS (hard)
- If `contract_drift_sentinel` returns FAIL => STOP the run. Fix drift first.
- If `repo_validate` reports invalid JSON => STOP.
- If PolicyGate blocks an action => do not perform it.

## Steps (recommended order)
1) evidence_init (create `validation_runs/YYYY-MM-DD/`)
2) repo_validate (links/json/secrets optional)
3) contract_drift_sentinel (schemas/examples/task refs)
4) economics_regression (if routing evidence exists)
5) decision_feedback (per role defaults in `governance/feedback_policy.md`)
6) policy_gatekeeper (check deep_oodle / creative_feedback / experiment / rebuild)
6.1) deliberation_pack_build (only if PolicyGate allows deep_oodle OR explicit deep review)

## After-run recording
7) outcome_ledger_append (write an OutcomeLedgerEvent)
8) route_autotune_suggest (generate up to 3 suggestions)
9) route_profile_patch_pack (optional; only if suggestions exist and you want proposals)

## Outputs (minimum)
### Recommended report paths
- DecisionFeedbackSpec: `reports/decision_feedback.json`
- PolicyGateDecision: `reports/policy_gate_decision.json`
- RouteAutotuneSuggestion: `reports/autotune_suggestion.json`
- Drift Sentinel: `reports/drift_sentinel.json`
- DeliberationPackSpec: `reports/deliberation_pack.json`

- QA reports from tools (stdout or saved)
- DecisionFeedbackSpec
- Outcome ledger event appended
- Autotune suggestion (if any)
- Optional patch pack files

## Token discipline
- Tools first.
- Cheap Claude only for a short memo if requested.
- Deep Oodle only with a DeliberationPack and only when allowed.

## Cross-links
- Canonical sources: `<PROJECT_ROOT>/CANONICAL_SOURCES.md`
- Policy gate: `tasks/governance/010_POLICY_GATE_CHECK.md`
- Drift sentinel: `tasks/ops/090_CONTRACT_DRIFT_SENTINEL.md`
- Deliberation pack: `tasks/deep/000_BUILD_DELIBERATION_PACK.md`

