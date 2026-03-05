# Cleaning Suite (Pack)

## Included skills
- `repo_clean_scan` — scan junk/unreferenced docs/duplicates
- `code_clean_scan` — scan likely obsolete code (heuristic)
- `cleanup_plan_apply` — apply cleanup plan (archive-first, dry-run default)

## Where to look
- Playbook: `../skills/playbooks/cleaning.md`
- Packaging hygiene: `../skills/playbooks/packaging_hygiene.md`
- Implementations: `../tools/skills/`

## Boundaries
- This pack is optional. Core should not depend on it to boot.
- See `../BOUNDARIES.md` and `../map.yaml`.
