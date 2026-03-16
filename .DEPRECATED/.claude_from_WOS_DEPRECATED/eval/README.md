# Eval Harness — CCW-MVP11

## Purpose

Make regressions visible. Each run of the eval harness:
1. Executes all golden tests against live skill implementations.
2. Saves a timestamped result file under `results/`.
3. Compares the current run against the previous run to surface regressions.
4. Exits non-zero if any test fails or a regression is detected.

## Structure

```
.claude/eval/
├── README.md            — this file
├── trend_report.md      — manual trend table (update after release runs)
├── eval_runner.py       — standalone runner (stdlib only)
├── golden/              — golden test fixture files (*.json)
│   ├── hello_golden.json
│   ├── scan_golden.json
│   └── qa_gate_golden.json
```

Results are written to **`.clockwork_runtime/eval/results/`** by default (not under `.claude/`).

## How to run

From the repository root:

```bash
python3 .claude/eval/eval_runner.py
```

With explicit paths:

```bash
python3 .claude/eval/eval_runner.py \
  --golden-dir .claude/eval/golden \
  --results-dir .clockwork_runtime/eval/results \
  --skills-dir .claude/tools/skills
```

Skip regression comparison (useful for the very first run or CI bootstrap):

```bash
python3 .claude/eval/eval_runner.py --no-compare
```

Exit codes: `0` = all pass + no regressions, `1` = any failure or regression.

## How to add a golden test

1. Create a new file in `.claude/eval/golden/` named `<skill_id>_golden_<NNN>.json`.
2. Follow the fixture schema:

```json
{
  "test_id": "golden_<skill_id>_<NNN>",
  "skill_id": "<skill_id>",
  "input": {"skill_id": "<skill_id>", "inputs": {...}},
  "expected": {"status": "ok", "outputs": {...}},
  "match_fields": ["outputs.status"],
  "description": "One-line description"
}
```

3. `match_fields` uses dot-notation to select fields from the actual skill result.
   - `"status"` — top-level status field
   - `"outputs.message"` — nested field inside `outputs`

4. Run the eval harness to verify the new test passes.

## Regression detection

A regression is defined as: a test that was `pass` in the previous run and is `fail` or `error` in the current run.

New tests (not present in the previous run) are not counted as regressions.

## Integration with QA gate

The `eval_run` skill (`.claude/tools/skills/eval_run.py`) wraps this runner
and can be invoked via `skill_runner.py` or the Clockwork skill dispatcher.
