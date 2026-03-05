# Playbook: QA Campaign (skill-first)

## Default sequence (PR-blocking)
1) evidence_init
2) qa_gate (runs: repo_validate + contract drift + topology + SSoT + semantic drift)
3) determinism_proof or determinism_harness (if determinism targets exist)
4) economics_regression (if evidence includes routing/ledger signals)

## Extended QA (nightly or pre-release)
- schema_batch_validate across all schemas/examples
- capability_map_build (publish current capability snapshot)
- security_redactor (for shareable evidence bundles)
- evidence_bundle_build (zip + manifest)

## When to involve agents
- Use **Local Verifier O3** only when a skill reports FAIL and you need a human-level diagnosis.
- Use **Result Relay Worker** to produce a short decision memo for Team_Lead/Personaler.

## Skill Scout triggers
Only run Skill Scout if triggers fire (see `governance/skill_scout_triggers.md`).
