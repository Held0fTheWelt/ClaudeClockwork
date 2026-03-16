# Skill Task: repo_clean_scan (Repository Cleaning)

## Intent
Detect obsolete/stale files and documents and propose a safe cleanup plan.

## Non-goals
- Do not delete files automatically.
- Do not rewrite content.

## Inputs (SkillRequestSpec.inputs)
- root: repo root (default ".")
- entry_docs: list of entry documents used for reachability
- convention_roots: directories considered in-use by convention (agents/contracts/tools/skills)
- exclude_dirs: directories to skip
- junk_dir_names: directory names considered junk
- junk_file_globs: file patterns considered junk
- large_file_bytes: threshold (default 5MB)
- write_reports: bool
- report_dir: where to write reports

## Outputs
- report (JSON + optional MD)
- suggested cleanup_plan (JSON) using "move_to_archive" operations

## Acceptance Criteria
- Deterministic output given same input tree
- No filesystem modification unless explicitly implemented in a separate apply-skill
- Produces actionable list with confidence levels
