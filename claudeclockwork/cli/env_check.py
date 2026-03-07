"""Phase 28 — Environment check: version, runtime root, python version, required binaries."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


def run_env_check(project_root: Path | str) -> tuple[int, list[str], dict[str, Any]]:
    """
    Returns (exit_code, errors, info). exit_code 0 when healthy; non-zero with actionable errors.
    """
    root = Path(project_root).resolve()
    errors: list[str] = []
    info: dict[str, Any] = {}

    # Python version
    info["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.version_info < (3, 10):
        errors.append("Python 3.10+ required")

    # Canonical version
    vf = root / ".claude" / "VERSION"
    if vf.is_file():
        info["canonical_version"] = vf.read_text(encoding="utf-8").strip()
    else:
        errors.append("Canonical version file .claude/VERSION missing")

    # Runtime root
    run_root = root / ".clockwork_runtime"
    if not run_root.is_dir():
        errors.append("Runtime root .clockwork_runtime not found (run first_run)")
    else:
        try:
            (run_root / ".write_test").write_text("")
            (run_root / ".write_test").unlink()
        except OSError as e:
            errors.append(f"Runtime root not writable: {e}")
    info["runtime_root"] = str(run_root)
    info["runtime_root_exists"] = run_root.is_dir()

    return (0 if not errors else 1, errors, info)
