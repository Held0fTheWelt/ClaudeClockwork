# Eval Trend Report

| Run | Date | Tests | Pass | Fail | Regressions |
|-----|------|-------|------|------|-------------|
| run_001 | 2026-03-02 | 3 | 3 | 0 | 0 |

## How to run
```bash
python3 .claude/eval/eval_runner.py
```

## Notes

- Each run produces a `results/run_<YYYYMMDD_HHMMSS>.json` file.
- The runner compares the current run against the most recent previous run.
- Update this table manually (or via automation) after each named release run.
