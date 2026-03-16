# Skill Task: code_clean_scan (Code Cleaning)

## Intent
Find code that is likely obsolete, unregistered, or drifted from policies.

## Non-goals
- No automatic refactors
- No delete without human review

## Inputs
- root: repo root
- code_roots: list of directories to scan for code (default: [".claude/tools/skills"])
- entrypoints: list of entry files to compute reachability (default: skill_runner.py)
- write_reports + report_dir

## Outputs
- code_clean_report (JSON + optional MD)

## Acceptance Criteria
- Deterministic scan, stable ordering
- Conservative heuristics + clear limitations section
