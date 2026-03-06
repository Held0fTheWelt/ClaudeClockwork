# hardening_scan_fix

Hardening = **find inconsistencies, classify, decide, optionally fix**.

## Skill ID
- `hardening_scan_fix`

## Scenarios (inputs.scenarios)
- `scan_inconsistencies` — drift, registry mismatch, junk artifacts
- `purge_oodle_refs` — remove obsolete `.oodle/` path references (policy: purge all)
- `validate_addon_boundaries` — ensure every skill is core or addon
- `ensure_autodocs` — generate docs for all skills (calls `autodocs_generate` when apply_fixes=true)

## Brain (memory)
- decisions are stored in `.claude/brain/decisions.json`
- append-only log in `.claude/brain/decisions.jsonl`

This prevents flip-flopping on policy decisions between runs.

## Usage
See `.claude/contracts/examples/hardening_scan_fix.skill_request.example.json`.
