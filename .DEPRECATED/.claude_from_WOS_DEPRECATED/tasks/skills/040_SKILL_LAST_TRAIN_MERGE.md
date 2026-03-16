# Skill Task: last_train_merge (Last-Train Skill)

## Intent
Given multiple zip archives, produce:
1) a combined archive (union of all content)
2) a timeline report indicating evolution vs loss per step

## Inputs
- zip_paths: ordered list of zip archives (oldest -> newest)
- root_out_dir: output directory for reports/combined zip
- combined_zip_name: name of merged zip
- ignore_globs: patterns to ignore (pycache, build artifacts)
- critical_paths: paths/dirs that must not disappear (policy + core folders)

## Outputs
- last_train_report.json (+ optional md)
- combined zip path

## Acceptance criteria
- Deterministic output
- Never includes ignored artifacts in combined archive
- Flags critical removals explicitly
