# Skill Task: hardening_scan_fix

## Intent
Provide a deterministic hardening pass that finds inconsistencies and can apply safe fixes.

## Safety requirements
- Default: scan-only (apply_fixes=false)
- Apply mode must be explicit and logged in hardening report
- Must maintain a brain store (decisions + log) to keep policy decisions stable

## Outputs
- hardening report under `.llama_runtime/knowledge/writes/hardening/`
