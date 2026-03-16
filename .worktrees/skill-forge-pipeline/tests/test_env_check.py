"""Phase 28 — env_check command tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.cli.env_check import run_env_check


def test_env_check_returns_tuple() -> None:
    code, errors, info = run_env_check(Path.cwd())
    assert isinstance(code, int)
    assert isinstance(errors, list)
    assert isinstance(info, dict)


def test_env_check_info_has_python_version() -> None:
    _, _, info = run_env_check(Path.cwd())
    assert "python_version" in info


def test_env_check_exit_zero_when_healthy() -> None:
    root = Path(__file__).resolve().parents[1]
    code, errors, _ = run_env_check(root)
    # In repo with .claude/VERSION and possibly .clockwork_runtime, may pass or fail
    if not errors:
        assert code == 0
    else:
        assert code == 1
