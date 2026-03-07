"""
Phase 44 — Compatibility tests for stable CLI contract.

Asserts stable commands return documented JSON shape and exit codes.
Deterministic and CI-safe (no external services).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "claudeclockwork.cli", "--project-root", str(ROOT), *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


def test_env_check_returns_stable_json_shape() -> None:
    """Stable command env-check: JSON with ok, errors, info; exit 0 or 1."""
    r = _cli("env-check")
    assert r.returncode in (0, 1)
    data = json.loads(r.stdout)
    assert "ok" in data
    assert isinstance(data["ok"], bool)
    assert "errors" in data
    assert isinstance(data["errors"], list)
    assert "info" in data


def test_first_run_returns_stable_json_shape() -> None:
    """Stable command first-run: JSON with ok, errors, info."""
    r = _cli("first-run")
    assert r.returncode in (0, 1)
    data = json.loads(r.stdout)
    assert "ok" in data
    assert "errors" in data
    assert "info" in data


def test_skill_id_success_returns_status_ok() -> None:
    """Stable skill invocation: status ok and exit 0."""
    r = _cli("--skill-id", "skill_registry_search", "--inputs", '{"query":"qa"}')
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data.get("status") == "ok"


def test_skill_id_unknown_returns_status_fail_and_exit_one() -> None:
    """Stable skill invocation: status fail, errors list, exit 1."""
    r = _cli("--skill-id", "nonexistent_skill_xyz_contract_test")
    assert r.returncode == 1
    data = json.loads(r.stdout)
    assert data.get("status") == "fail"
    assert "errors" in data
    assert isinstance(data["errors"], list)
