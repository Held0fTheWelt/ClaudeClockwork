from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "claudeclockwork.cli", "--project-root", str(ROOT), *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


def test_cli_known_skill_exits_zero() -> None:
    r = _cli("--skill-id", "skill_registry_search", "--inputs", '{"query":"qa"}')
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data.get("status") == "ok"


def test_cli_unknown_skill_exits_one() -> None:
    r = _cli("--skill-id", "no_such_skill_xyz")
    assert r.returncode == 1
    data = json.loads(r.stdout)
    assert data.get("status") == "fail"
    assert "errors" in data


def test_cli_invalid_json_inputs_exits_nonzero() -> None:
    r = _cli("--skill-id", "capability_map_build", "--inputs", "not-valid-json")
    assert r.returncode != 0


def test_cli_plugin_healthcheck_known_exits_zero() -> None:
    r = _cli("--plugin-healthcheck", "filesystem")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data.get("status") == "ok"


def test_cli_plugin_healthcheck_unknown_exits_one() -> None:
    r = _cli("--plugin-healthcheck", "no_such_plugin_xyz")
    assert r.returncode == 1
    data = json.loads(r.stdout)
    assert data.get("status") == "fail"
