#!/usr/bin/env python3
"""
eval_run — CCW-MVP11 Eval Harness skill wrapper.

Runs golden tests via eval_runner logic and returns a SkillResultSpec.

Usage (via skill_runner):
    req["inputs"]["golden_dir"]       — path to golden test fixtures (default: .claude/eval/golden)
    req["inputs"]["output_dir"]       — path to write results (default: .clockwork_runtime/eval/results)
    req["inputs"]["skills_dir"]       — path to skill .py files (default: .claude/tools/skills)
    req["inputs"]["compare_previous"] — bool, compare against previous run (default: true)

Usage (standalone):
    python3 eval_run.py '{"skill_id":"eval_run","inputs":{"golden_dir":".claude/eval/golden","compare_previous":true}}'

Output (SkillResultSpec):
    {
        "type": "skill_result_spec",
        "skill_id": "eval_run",
        "status": "ok" | "fail",
        "outputs": {
            "tests_run": int,
            "pass_count": int,
            "fail_count": int,
            "error_count": int,
            "regression_count": int,
            "results_file": str
        }
    }
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_eval_runner(eval_runner_path: Path):
    """Dynamically load eval_runner module from its path."""
    spec = importlib.util.spec_from_file_location("_eval_runner", eval_runner_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create module spec for {eval_runner_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _find_repo_root() -> Path:
    """Find repo root by walking up to find .claude/."""
    cwd = Path.cwd()
    if (cwd / ".claude").exists():
        return cwd
    for parent in cwd.parents:
        if (parent / ".claude").exists():
            return parent
    return cwd


def run(req: dict) -> dict:
    """
    Called by skill_runner.py with a full SkillRequestSpec.

    Inputs:
        golden_dir       (str)  — path to golden fixtures dir
        output_dir       (str)  — path to results output dir
        skills_dir       (str)  — path to skills dir
        compare_previous (bool) — whether to compare against previous run

    Returns SkillResultSpec.
    """
    inputs = req.get("inputs") or req.get("input") or {}

    repo_root = _find_repo_root()

    golden_dir_raw = inputs.get("golden_dir", ".claude/eval/golden")
    output_dir_raw = inputs.get("output_dir", ".clockwork_runtime/eval/results")
    skills_dir_raw = inputs.get("skills_dir", ".claude/tools/skills")
    compare_previous: bool = bool(inputs.get("compare_previous", True))

    golden_dir = (repo_root / golden_dir_raw).resolve()
    results_dir = (repo_root / output_dir_raw).resolve()
    skills_dir = (repo_root / skills_dir_raw).resolve()
    results_dir.mkdir(parents=True, exist_ok=True)

    # Load eval_runner module (located next to this file's .claude/eval/)
    # Canonical location: .claude/eval/eval_runner.py
    eval_runner_path = repo_root / ".claude" / "eval" / "eval_runner.py"

    errors: list[str] = []

    try:
        er = _load_eval_runner(eval_runner_path)
    except ImportError as exc:
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": "eval_run",
            "status": "fail",
            "outputs": {
                "tests_run": 0,
                "pass_count": 0,
                "fail_count": 0,
                "error_count": 0,
                "regression_count": 0,
                "results_file": "",
            },
            "errors": [f"Cannot load eval_runner: {exc}"],
            "warnings": [],
            "metrics": {},
        }

    # Load and run tests
    try:
        tests = er.load_golden_tests(golden_dir)
    except Exception as exc:
        errors.append(f"load_golden_tests error: {exc}")
        tests = []

    run_results: list[dict] = []
    for test in tests:
        result = er.run_test(test, skills_dir)
        run_results.append(result)

    # Save results
    import datetime as _dt
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_filename = f"run_{ts}.json"
    run_file = results_dir / run_filename

    pass_count = sum(1 for r in run_results if r["status"] == "pass")
    fail_count = sum(1 for r in run_results if r["status"] == "fail")
    error_count = sum(1 for r in run_results if r["status"] == "error")

    run_payload = {
        "run_id": run_filename,
        "timestamp": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "tests_run": len(run_results),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "error_count": error_count,
        "results": run_results,
    }

    try:
        with run_file.open("w", encoding="utf-8") as fh:
            json.dump(run_payload, fh, indent=2, ensure_ascii=False, default=str)
    except OSError as exc:
        errors.append(f"Cannot write results file: {exc}")

    # Regression detection
    regression_count = 0
    if compare_previous:
        try:
            prev_file = er._find_previous_run(results_dir, run_filename)
            if prev_file is not None:
                prev_results = er._load_run_results(prev_file)
                comparisons = er.compare_runs(run_results, prev_results)
                regression_count = sum(1 for c in comparisons if c["regression"])
        except Exception as exc:
            errors.append(f"Regression comparison error: {exc}")

    overall_status = "ok" if (fail_count == 0 and error_count == 0 and regression_count == 0) else "fail"
    if errors:
        overall_status = "fail"

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "eval_run",
        "status": overall_status,
        "outputs": {
            "tests_run": len(run_results),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "error_count": error_count,
            "regression_count": regression_count,
            "results_file": str(run_file),
        },
        "errors": errors,
        "warnings": [],
        "metrics": {
            "tests_run": len(run_results),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "regression_count": regression_count,
        },
    }


# ---------------------------------------------------------------------------
# Standalone entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) >= 2:
        raw = sys.argv[1]
    else:
        raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Invalid JSON input: {exc}\n")
        return 1

    # Accept both bare inputs dict and wrapped SkillRequestSpec
    if "skill_id" in data and "inputs" in data:
        req = data
    else:
        req = {"type": "skill_request_spec", "skill_id": "eval_run", "inputs": data}

    result = run(req)
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
