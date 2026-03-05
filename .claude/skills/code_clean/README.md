# code_clean (Code Cleaning Skill)

This skill detects **code drift** and probable **obsolete code** using conservative static heuristics.

## Skill IDs
- `code_clean_scan` — scan code roots, build a lightweight import graph, find orphans + markers

## Outputs
- `code_clean_report.json` + `code_clean_report.md` (optional)

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in .claude/contracts/examples/code_clean_scan.skill_request.example.json --out out.json
```

## What it detects (heuristic)
- `.py` modules not reachable from configured entrypoints (import graph)
- modules not registered in `skill_runner.py` (for the skills folder)
- markers: DEPRECATED / TODO remove / placeholder / legacy path references
- suspicious path drift (e.g. `.claude/` leftovers)

## Important
Static analysis cannot see dynamic imports or runtime reflection; treat this as a **candidate list**, not proof.
