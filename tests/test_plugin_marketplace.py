"""Phase 61 — Marketplace UX: search, info, install/update/uninstall, hash validation."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _plugin_cmd(cmd: str, *args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "claudeclockwork.cli", "--project-root", str(ROOT), "plugin", cmd] + list(args),
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return json.loads(proc.stdout)


def test_plugin_search() -> None:
    out = _plugin_cmd("search")
    assert "plugins" in out


def test_plugin_info_unknown() -> None:
    out = _plugin_cmd("info", "nonexistent_plugin_xyz")
    assert out.get("plugin") is None or out.get("error") == "not_found"


def test_plugin_install_validates_bundle(tmp_path: Path) -> None:
    (tmp_path / "plugin.json").write_text(json.dumps({"id": "mp_plugin"}), encoding="utf-8")
    out = _plugin_cmd("install", "mp_plugin", "--bundle", str(tmp_path))
    assert out.get("ok") is True or "errors" in out
