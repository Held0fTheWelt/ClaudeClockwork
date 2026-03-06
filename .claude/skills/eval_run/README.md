# eval_run

**Pack:** `unclassified`

## Purpose
Eval harness runner — executes golden tests and detects regressions (CCW-MVP11).
- Input: `{"golden_dir": str, "output_dir": str, "skills_dir": str, "compare_previous": bool}`
- Output: `{"tests_run": int, "pass_count": int, "fail_count": int, "error_count": int, "regression_count": int, "results_file": str}`
- Loads all `*.json` fixtures from `golden_dir`, runs each via the skill's `run(req)` interface, saves timestamped results, compares against previous run for regressions
- Exit status `ok`…

## Implementation
- Tool: `.claude/tools/skills/eval_run.py`
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
