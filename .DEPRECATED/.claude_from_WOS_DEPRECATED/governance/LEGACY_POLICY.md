# Legacy Policy

## `.oodle` is obsolete
- `.oodle` is not deprecated; it is **removed**.
- This repo must not reference `.oodle/` paths.

## How we enforce this
- `hardening_scan_fix` scenario `scan_inconsistencies` flags any `.oodle` reference.
- `hardening_scan_fix` scenario `purge_oodle_refs` can remove such references.

## Removing truly dead content
- Use `repo_clean_scan` to detect junk and unreachable docs.
- Use `cleanup_plan_apply` to archive/remove safely.
