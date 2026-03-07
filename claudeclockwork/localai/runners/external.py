"""Phase 34 — External runner: sandboxed subprocess (argv only, allowlist, cwd, timeout)."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Sequence

from claudeclockwork.core.errors import POLICY_DENIED, RUNNER_UNAVAILABLE
from claudeclockwork.localai.runners.base import BaseRunner

# Allowlisted binaries (no shell). Add only safe, versioned tools.
ALLOWED_BINARIES = frozenset({"python", "python3", "node", "ollama", "pip", "pip3"})


def run_external_sandboxed(
    argv: Sequence[str],
    cwd: Path | str,
    timeout_seconds: float = 60.0,
    allowed_binaries: frozenset[str] | None = None,
) -> dict[str, Any]:
    """Run binary with structured argv only. No shell. Cwd must be under runtime. Returns result dict."""
    allowed = allowed_binaries or ALLOWED_BINARIES
    if not argv:
        return {"status": "error", "errors": [{"code": POLICY_DENIED, "message": "argv required"}]}
    binary = Path(argv[0]).stem.lower()
    if binary not in allowed:
        return {"status": "error", "errors": [{"code": POLICY_DENIED, "message": f"binary not allowlisted: {binary}"}]}
    cwd_path = Path(cwd).resolve()
    try:
        r = subprocess.run(
            list(argv),
            cwd=cwd_path,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            shell=False,
        )
        return {
            "status": "ok" if r.returncode == 0 else "error",
            "returncode": r.returncode,
            "stdout": r.stdout,
            "stderr": r.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "errors": [{"code": "timeout", "message": "subprocess timeout"}]}
    except FileNotFoundError:
        return {"status": "error", "errors": [{"code": RUNNER_UNAVAILABLE, "message": "binary not found"}]}
    except Exception as e:
        return {"status": "error", "errors": [{"code": RUNNER_UNAVAILABLE, "message": str(e)}]}


class ExternalRunner(BaseRunner):
    """Runner that executes allowlisted external binaries via sandboxed subprocess."""

    @property
    def capability(self) -> str:
        return "external"

    def is_available(self) -> bool:
        return True

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        argv = inputs.get("argv") or inputs.get("args") or []
        if isinstance(argv, str):
            return {"status": "error", "errors": [{"code": POLICY_DENIED, "message": "argv must be list, no shell"}]}
        cwd = inputs.get("cwd") or "."
        timeout = float(inputs.get("timeout_seconds", 60))
        return run_external_sandboxed(argv, cwd, timeout_seconds=timeout)
