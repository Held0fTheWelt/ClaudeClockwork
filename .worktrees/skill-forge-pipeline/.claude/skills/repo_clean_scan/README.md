# repo_clean_scan

**Pack:** `core`

## Purpose
Deterministic repo cleaning scanner:
- finds junk artifacts (caches, temp files)
- detects unreferenced docs (heuristic reachability)
- detects duplicates (sha256) and large files
- outputs a cleanup plan (archive-first)

## Implementation
- Tool: `.claude/tools/skills/repo_clean_scan.py`
- Skill runner: `.claude/tools/skills/skill_runner.py`
- Contracts: `.claude/contracts/`

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in <request.json> --out <result.json>
```

## Outputs
Describe output files and write locations here.

## Constraints / Non-goals
- Deterministic: no semantic "truth verification" over content.
- Can provide candidate lists, but cannot prove that something is obsolete.
- If LLM refinement is needed: use the appropriate playbook (Explore/Write/Critic/DecideGap).
