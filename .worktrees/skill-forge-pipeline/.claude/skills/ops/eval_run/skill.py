from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


def _load_yaml_simple(text: str) -> dict:
    """Minimal YAML loader for flat key: value pairs (no external dep)."""
    result: dict = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip().strip('"').strip("'")
    return result


def _run_test(test_def: dict, repo_root: Path) -> dict:
    """Run a single eval test definition. Returns {name, status, detail, ms}."""
    name = test_def.get("name", "unnamed")
    check = test_def.get("check", "")
    target = test_def.get("target", "")
    t0 = time.monotonic()

    if check == "file_exists":
        path = (repo_root / target).resolve()
        ok = path.exists()
        status = "pass" if ok else "fail"
        detail = str(path)

    elif check == "file_contains":
        path = (repo_root / target).resolve()
        needle = test_def.get("contains", "")
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            ok = needle in text
            status = "pass" if ok else "fail"
            detail = f"'{needle}' in {target}"
        except Exception as exc:
            status = "error"
            detail = str(exc)

    elif check == "json_valid":
        path = (repo_root / target).resolve()
        try:
            json.loads(path.read_text(encoding="utf-8"))
            status = "pass"
            detail = str(path)
        except Exception as exc:
            status = "fail"
            detail = str(exc)

    else:
        status = "skip"
        detail = f"unknown check type: {check!r}"

    ms = round((time.monotonic() - t0) * 1000, 1)
    return {"name": name, "status": status, "detail": detail, "ms": ms}


class EvalRunSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        results_dir = (repo_root / ".clockwork_runtime" / "eval" / "results").resolve()
        results_dir.mkdir(parents=True, exist_ok=True)

        suite = kwargs.get("suite", "default")
        eval_dir = repo_root / ".claude" / "eval"

        # Collect test definitions from YAML files
        tests: list[dict] = []
        if eval_dir.exists():
            for yaml_file in sorted(eval_dir.rglob("*.yaml")):
                if suite != "default" and suite not in yaml_file.name:
                    continue
                try:
                    text = yaml_file.read_text(encoding="utf-8")
                    parsed = _load_yaml_simple(text)
                    if parsed.get("type") == "eval_test":
                        tests.append({
                            "name": parsed.get("name", yaml_file.stem),
                            "check": parsed.get("check", "file_exists"),
                            "target": parsed.get("target", ""),
                            "contains": parsed.get("contains", ""),
                        })
                except Exception:
                    continue

        # Run tests with timing
        t_suite_start = time.monotonic()
        test_results = [_run_test(t, repo_root) for t in tests]
        duration_ms = round((time.monotonic() - t_suite_start) * 1000, 1)

        pass_count = sum(1 for r in test_results if r["status"] == "pass")
        fail_count = sum(1 for r in test_results if r["status"] == "fail")
        error_count = sum(1 for r in test_results if r["status"] == "error")

        # D6.7 — Write structured snapshot with run_id, suite, tests[]
        run_id = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        snapshot = {
            "run_id": run_id,
            "suite": suite,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "error_count": error_count,
            "duration_ms": duration_ms,
            "tests": [
                {"name": r["name"], "status": r["status"], "ms": r["ms"]}
                for r in test_results
            ],
        }
        results_file = results_dir / f"eval_{ts}.json"
        results_file.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

        # Trend check: if last 5 runs exist, alert if any had failures
        warnings: list[str] = []
        all_runs = sorted(results_dir.glob("eval_*.json"))
        if len(all_runs) >= 2:
            recent = all_runs[-5:]
            degraded = []
            for run_path in recent[:-1]:  # exclude current
                try:
                    prev = json.loads(run_path.read_text(encoding="utf-8"))
                    if prev.get("fail_count", 0) > 0 or prev.get("error_count", 0) > 0:
                        degraded.append(run_path.name)
                except Exception:
                    pass
            if degraded:
                warnings.append(f"Recent runs with failures: {degraded}")

        return SkillResult(
            fail_count == 0 and error_count == 0,
            "eval_run",
            data={
                "run_id": run_id,
                "suite": suite,
                "tests_run": len(test_results),
                "pass_count": pass_count,
                "fail_count": fail_count,
                "error_count": error_count,
                "duration_ms": duration_ms,
                "results_path": str(results_file),
            },
            warnings=warnings,
        )
