#!/usr/bin/env python3
"""
Eval Runner — CCW-MVP11 Golden Tests

Standalone script. No external dependencies; stdlib only.

Usage:
    python3 .claude/eval/eval_runner.py
    python3 .claude/eval/eval_runner.py --golden-dir .claude/eval/golden --results-dir .llama_runtime/eval/results

Exit codes:
    0 — all tests pass, no regressions
    1 — one or more tests failed or a regression detected
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_nested(obj: Any, dotted_key: str) -> Any:
    """
    Resolve a dotted key path against a nested dict.
    E.g. _get_nested({"outputs": {"status": "ok"}}, "outputs.status") -> "ok"
    Returns a sentinel _MISSING if any step is absent.
    """
    parts = dotted_key.split(".")
    cur = obj
    for part in parts:
        if not isinstance(cur, dict) or part not in cur:
            return _MISSING
        cur = cur[part]
    return cur


class _MissingSentinel:
    def __repr__(self) -> str:
        return "<MISSING>"


_MISSING = _MissingSentinel()


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def load_golden_tests(golden_dir: Path) -> list[dict]:
    """
    Load all golden test fixtures from *.json files in golden_dir.

    Returns list of test dicts. Logs and skips malformed files.
    """
    tests: list[dict] = []
    if not golden_dir.exists():
        print(f"[WARN] golden_dir does not exist: {golden_dir}", file=sys.stderr)
        return tests

    for fixture_path in sorted(golden_dir.glob("*.json")):
        try:
            with fixture_path.open("r", encoding="utf-8") as fh:
                test = json.load(fh)
            # Basic validation
            required_keys = {"test_id", "skill_id", "input", "expected", "match_fields"}
            missing = required_keys - set(test.keys())
            if missing:
                print(
                    f"[WARN] Skipping {fixture_path.name}: missing keys {missing}",
                    file=sys.stderr,
                )
                continue
            tests.append(test)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[WARN] Skipping {fixture_path.name}: {exc}", file=sys.stderr)

    return tests


def _load_skill_module(skill_id: str, skills_dir: Path):
    """
    Dynamically import a skill module from skills_dir/<skill_id>.py.
    Returns the module or raises ImportError.
    """
    skill_path = skills_dir / f"{skill_id}.py"
    if not skill_path.exists():
        raise ImportError(f"Skill file not found: {skill_path}")

    spec = importlib.util.spec_from_file_location(f"_skill_{skill_id}", skill_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create module spec for {skill_path}")

    # Temporarily insert skills_dir into sys.path so relative imports within skills work
    skills_dir_str = str(skills_dir)
    inserted = skills_dir_str not in sys.path
    if inserted:
        sys.path.insert(0, skills_dir_str)

    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    finally:
        if inserted:
            sys.path.remove(skills_dir_str)

    return module


def run_test(test: dict, skills_dir: Path) -> dict:
    """
    Execute a single golden test.

    Returns a result dict:
        {
            "test_id": str,
            "status": "pass" | "fail" | "error",
            "actual": dict | None,
            "expected": dict,
            "match_fields": list[str],
            "matched": list[str],   # fields that matched
            "mismatched": list[str],  # fields that did not match
            "error": str | None,
        }
    """
    test_id: str = test["test_id"]
    skill_id: str = test["skill_id"]
    input_req: dict = test["input"]
    expected: dict = test["expected"]
    match_fields: list[str] = test["match_fields"]

    # Ensure the request has the required wrapper fields
    if "type" not in input_req:
        input_req = dict(input_req)
        input_req["type"] = "skill_request_spec"

    actual: dict | None = None
    error_msg: str | None = None

    try:
        module = _load_skill_module(skill_id, skills_dir)
    except ImportError as exc:
        error_msg = str(exc)
        return {
            "test_id": test_id,
            "status": "error",
            "actual": None,
            "expected": expected,
            "match_fields": match_fields,
            "matched": [],
            "mismatched": match_fields,
            "error": error_msg,
        }

    try:
        actual = module.run(input_req)
    except Exception as exc:
        error_msg = f"skill raised exception: {type(exc).__name__}: {exc}"
        return {
            "test_id": test_id,
            "status": "error",
            "actual": None,
            "expected": expected,
            "match_fields": match_fields,
            "matched": [],
            "mismatched": match_fields,
            "error": error_msg,
        }

    # Compare match_fields
    matched: list[str] = []
    mismatched: list[str] = []

    for field in match_fields:
        actual_val = _get_nested(actual, field)
        expected_val = _get_nested(expected, field)
        if actual_val is _MISSING and expected_val is _MISSING:
            matched.append(field)
        elif actual_val is _MISSING or expected_val is _MISSING:
            mismatched.append(field)
        elif actual_val == expected_val:
            matched.append(field)
        else:
            mismatched.append(field)

    status = "pass" if not mismatched else "fail"

    return {
        "test_id": test_id,
        "status": status,
        "actual": actual,
        "expected": expected,
        "match_fields": match_fields,
        "matched": matched,
        "mismatched": mismatched,
        "error": None,
    }


def compare_runs(current: list[dict], previous: list[dict]) -> list[dict]:
    """
    Compare current run results against a previous run to detect regressions.

    A regression is: a test that was "pass" in previous run but is "fail" or "error" now.

    Returns list of regression entries:
        {
            "test_id": str,
            "regression": bool,
            "prev_status": str,
            "curr_status": str,
        }
    """
    prev_by_id: dict[str, str] = {r["test_id"]: r["status"] for r in previous}
    curr_by_id: dict[str, str] = {r["test_id"]: r["status"] for r in current}

    regressions: list[dict] = []
    for test_id, curr_status in curr_by_id.items():
        prev_status = prev_by_id.get(test_id)
        if prev_status is None:
            # New test — not a regression
            continue
        is_regression = (prev_status == "pass") and (curr_status in ("fail", "error"))
        regressions.append(
            {
                "test_id": test_id,
                "regression": is_regression,
                "prev_status": prev_status,
                "curr_status": curr_status,
            }
        )

    return regressions


def _find_previous_run(results_dir: Path, current_filename: str) -> Path | None:
    """Return the most recent run file that is NOT the current run."""
    candidates = sorted(
        [
            p
            for p in results_dir.glob("run_*.json")
            if p.name != current_filename
        ]
    )
    return candidates[-1] if candidates else None


def _load_run_results(run_file: Path) -> list[dict]:
    """Load result list from a saved run file."""
    try:
        with run_file.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data.get("results", [])
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[WARN] Cannot read previous run {run_file.name}: {exc}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Eval Runner — golden tests with regression detection (CCW-MVP11)"
    )
    parser.add_argument(
        "--golden-dir",
        default=".claude/eval/golden",
        help="Directory containing golden test JSON fixtures (default: .claude/eval/golden)",
    )
    parser.add_argument(
        "--results-dir",
        default=".llama_runtime/eval/results",
        help="Directory to write run result files (default: .llama_runtime/eval/results)",
    )
    parser.add_argument(
        "--skills-dir",
        default=".claude/tools/skills",
        help="Directory containing skill .py files (default: .claude/tools/skills)",
    )
    parser.add_argument(
        "--no-compare",
        action="store_true",
        default=False,
        help="Skip comparison against previous run (no regression check)",
    )
    args = parser.parse_args()

    # Resolve paths relative to cwd or repo root
    # Try to find repo root (directory containing .claude/)
    repo_root = Path.cwd()
    if not (repo_root / ".claude").exists():
        for parent in repo_root.parents:
            if (parent / ".claude").exists():
                repo_root = parent
                break

    golden_dir = (repo_root / args.golden_dir).resolve()
    results_dir = (repo_root / args.results_dir).resolve()
    skills_dir = (repo_root / args.skills_dir).resolve()

    results_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load golden tests
    tests = load_golden_tests(golden_dir)
    if not tests:
        print("[ERROR] No golden tests found. Exiting.", file=sys.stderr)
        return 1

    print(f"Loaded {len(tests)} golden test(s) from {golden_dir}")

    # 2. Run each test
    run_results: list[dict] = []
    for test in tests:
        result = run_test(test, skills_dir)
        run_results.append(result)

        label = result["status"].upper()
        marker = "[PASS]" if label == "PASS" else ("[FAIL]" if label == "FAIL" else "[ERROR]")
        msg = f"  {marker} {result['test_id']}"
        if result["status"] == "fail":
            msg += f" — mismatched: {result['mismatched']}"
        elif result["status"] == "error":
            msg += f" — {result['error']}"
        print(msg)

    # 3. Save results to timestamped file
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_filename = f"run_{ts}.json"
    run_file = results_dir / run_filename

    run_payload = {
        "run_id": run_filename,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tests_run": len(run_results),
        "pass_count": sum(1 for r in run_results if r["status"] == "pass"),
        "fail_count": sum(1 for r in run_results if r["status"] == "fail"),
        "error_count": sum(1 for r in run_results if r["status"] == "error"),
        "results": run_results,
    }

    with run_file.open("w", encoding="utf-8") as fh:
        json.dump(run_payload, fh, indent=2, ensure_ascii=False, default=str)

    print(f"\nResults saved: {run_file}")

    # 4. Compare against previous run (regression detection)
    regression_count = 0
    if not args.no_compare:
        prev_file = _find_previous_run(results_dir, run_filename)
        if prev_file is None:
            print("No previous run found — skipping regression check (first run).")
        else:
            print(f"Comparing against previous run: {prev_file.name}")
            prev_results = _load_run_results(prev_file)
            comparisons = compare_runs(run_results, prev_results)
            regressions = [c for c in comparisons if c["regression"]]
            regression_count = len(regressions)

            for comp in comparisons:
                if comp["regression"]:
                    print(
                        f"  [REGRESSION] {comp['test_id']} "
                        f"({comp['prev_status']} -> {comp['curr_status']})"
                    )

            if regression_count == 0:
                print("No regressions detected.")

    # 5. Summary
    pass_count = run_payload["pass_count"]
    fail_count = run_payload["fail_count"]
    error_count = run_payload["error_count"]
    total = run_payload["tests_run"]

    print(
        f"\nSummary: {total} tests — "
        f"{pass_count} pass / {fail_count} fail / {error_count} error / "
        f"{regression_count} regression(s)"
    )

    # Exit 1 if any failures/errors or regressions
    if fail_count > 0 or error_count > 0 or regression_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
