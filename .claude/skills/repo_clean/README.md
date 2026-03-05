# repo_clean (Cleaning Skill)

This skill helps you detect **obsolete / stale / junk** files and documents inside a repo and propose a **safe cleanup plan**.

It is intentionally **dry-run first**:
- It **never deletes** files by default.
- It produces a report + a suggested plan where operations are "move to archive".
- If you want automated changes later, add a separate `repo_clean_apply` step with explicit allowlists.

## Skill IDs
- `repo_clean_scan` — scan + report + suggested `cleanup_plan`

## Outputs
- `repo_clean_report.json` + `repo_clean_report.md` (optional)
- `cleanup_plan.json` (optional)

## Typical usage (SkillRunner)
```bash
python .claude/tools/skills/skill_runner.py --in .claude/contracts/examples/repo_clean_scan.skill_request.example.json --out out.json
```

## What it detects
- build/test caches: `__pycache__`, `.pytest_cache`, `*.pyc`, etc.
- duplicates (sha256)
- large files (accidental binaries)
- markdown docs not reachable from your entry docs (heuristic)
- markers like `DEPRECATED`, `OBSOLETE`, `placeholder`, `TODO remove`

## Safety model
- high confidence junk => recommended action "delete" (still not executed)
- medium/low confidence => recommended action "review/archive"
- **never** edits content
