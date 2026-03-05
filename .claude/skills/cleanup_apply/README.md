# cleanup_plan_apply (Apply Cleanup Plan)

Apply a `cleanup_plan.json` produced by `repo_clean_scan` (or manually authored).

## Skill ID
- `cleanup_plan_apply`

## Safety defaults
- `dry_run: true` by default
- `allow_delete: false` by default (archive-first)

## Inputs
- plan_path: path or glob pattern (newest match is used), OR `plan` object inline
- root: repo root (default ".")
- dry_run: bool
- allow_delete: bool
- on_conflict: skip | overwrite | rename
- write_report: bool
- report_dir: where to write `cleanup_apply_report_*.json`

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in .claude/contracts/examples/cleanup_plan_apply.skill_request.example.json --out out.json
```

## Limitations
- It cannot infer the correct plan; it only applies the given operations.
- Always review medium/low confidence items before applying.
