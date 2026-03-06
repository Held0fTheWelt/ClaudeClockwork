from __future__ import annotations

import json
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
    """Run a single eval test definition. Returns {name, status, detail}."""
    name = test_def.get("name", "unnamed")
    check = test_def.get("check", "")
    target = test_def.get("target", "")

    if check == "file_exists":
        path = (repo_root / target).resolve()
        ok = path.exists()
        return {"name": name, "status": "pass" if ok else "fail", "detail": str(path)}

    if check == "file_contains":
        path = (repo_root / target).resolve()
        needle = test_def.get("contains", "")
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            ok = needle in text
        except Exception as e:
            return {"name": name, "status": "error", "detail": str(e)}
        return {"name": name, "status": "pass" if ok else "fail", "detail": f"'{needle}' in {target}"}

    if check == "json_valid":
        path = (repo_root / target).resolve()
        try:
            json.loads(path.read_text(encoding="utf-8"))
            return {"name": name, "status": "pass", "detail": str(path)}
        except Exception as e:
            return {"name": name, "status": "fail", "detail": str(e)}

    return {"name": name, "status": "skip", "detail": f"unknown check type: {check!r}"}


class EvalRunSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        results_dir = (repo_root / ".llama_runtime" / "eval" / "results").resolve()
        results_dir.mkdir(parents=True, exist_ok=True)

        suite_filter = kwargs.get("suite")
        eval_dir = repo_root / ".claude" / "eval"

        # Collect test definitions from YAML files
        tests: list[dict] = []
        if eval_dir.exists():
            for yaml_file in sorted(eval_dir.rglob("*.yaml")):
                if suite_filter and suite_filter not in yaml_file.name:
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

        # Run tests
        results = [_run_test(t, repo_root) for t in tests]

        pass_count = sum(1 for r in results if r["status"] == "pass")
        fail_count = sum(1 for r in results if r["status"] == "fail")
        error_count = sum(1 for r in results if r["status"] == "error")

        # Write results snapshot
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"eval_{ts}.json"
        results_file.write_text(
            json.dumps({"timestamp": ts, "results": results, "summary": {"pass": pass_count, "fail": fail_count}}, indent=2),
            encoding="utf-8",
        )

        return SkillResult(
            fail_count == 0 and error_count == 0,
            "eval_run",
            data={
                "tests_run": len(results),
                "pass_count": pass_count,
                "fail_count": fail_count,
                "error_count": error_count,
                "results_path": str(results_file),
            },
        )
