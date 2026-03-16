# parity_scan_and_mvp_planner

**Pack:** `unclassified`

## Purpose
Deterministic file-evidence parity scanner (CCW-MVP16).
- Input: `{"run_date": str, "scan_scope": [str], "reference_mvp_chain": str, "output_dir": str, "generate_mvp_plan": bool, "mvp_plan_output_dir": str}`
- Output: `{"parity_matrix": str, "backlog": str, "mvp_plan": str|null, "gap_count": int, "partial_count": int, "full_count": int, "p0_count": int, "p1_count": int, "p2_count": int, "status": "ok"|"error"}`
- Reads MVP chain markdown, classifies each section as FULL/PARTIAL/GAP based on file…

## Implementation
- Tool: `.claude/tools/skills/parity_scan_and_mvp_planner.py`
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
