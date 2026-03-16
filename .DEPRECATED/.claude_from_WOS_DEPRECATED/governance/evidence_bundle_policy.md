# Evidence Bundle Policy (v17.6)

## Goal
Evidence must be **shareable**, **minimal**, and **reproducible**.

## Standard
- Evidence runs live under `validation_runs/YYYY-MM-DD/`.
- Use `evidence_bundle_build` to create:
  - `artifacts/evidence_bundle_manifest.json`
  - `artifacts/evidence_bundle.zip`

## Determinism
- Prefer stable file names.
- Use `determinism_proof` / `determinism_harness` for hashing targets.

## Sharing
- Always run `security_redactor` before sharing an evidence folder externally.
