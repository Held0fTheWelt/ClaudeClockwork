"""Phase 16 — test_run: run pytest and return structured results."""
from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult

_SUMMARY_RE = re.compile(
    r'(\d+) passed'
    r'(?:,\s*(\d+) failed)?'
    r'(?:,\s*(\d+) error)?'
)
_COVERAGE_RE = re.compile(r'TOTAL\s+\d+\s+\d+\s+(\d+)%')
_FAILED_RE = re.compile(r'^FAILED (.+?) - (.+)$', re.MULTILINE)


class TestRunSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        # Safety gate: do not run inside another pytest process
        if os.environ.get("CLOCKWORK_CI"):
            return SkillResult(True, "test_run", data={
                "passed": 0, "failed": 0, "errors": 0,
                "duration_ms": 0.0, "failures": [], "exit_code": 0,
                "skipped_reason": "CLOCKWORK_CI is set",
            })

        root = Path(context.working_directory).resolve()
        test_path = kwargs.get("test_path", "tests/")
        marker = kwargs.get("marker", "")
        coverage = bool(kwargs.get("coverage", False))

        cmd = ["python3", "-m", "pytest", str(test_path), "--tb=short", "-q"]
        if marker:
            cmd += ["-m", marker]
        if coverage:
            cmd += ["--cov=claudeclockwork", "--cov-report=term-missing"]

        t0 = time.monotonic()
        result = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
        duration_ms = (time.monotonic() - t0) * 1000

        output = result.stdout + result.stderr

        # Parse summary line
        passed = failed = errors = 0
        m = _SUMMARY_RE.search(output)
        if m:
            passed = int(m.group(1) or 0)
            failed = int(m.group(2) or 0)
            errors = int(m.group(3) or 0)

        # Parse individual failures
        failures = [
            {"test": fm.group(1), "message": fm.group(2)}
            for fm in _FAILED_RE.finditer(output)
        ]

        data: dict = {
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "duration_ms": round(duration_ms, 1),
            "failures": failures,
            "exit_code": result.returncode,
        }

        if coverage:
            cm = _COVERAGE_RE.search(output)
            if cm:
                data["coverage_pct"] = float(cm.group(1))

        ok = result.returncode == 0
        return SkillResult(
            ok, "test_run",
            data=data,
            error=(f"{failed} test(s) failed" if not ok else None),
        )
