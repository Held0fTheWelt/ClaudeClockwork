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

## Grenzen / Nicht-Ziele
- Deterministisch: keine semantische "Wahrheitsprüfung" über Inhalte.
- Kann Kandidatenlisten liefern, aber nicht beweisen, dass etwas obsolet ist.
- Wenn LLM-Verfeinerung nötig ist: nutze das passende Playbook (Explore/Write/Critic/DecideGap).
