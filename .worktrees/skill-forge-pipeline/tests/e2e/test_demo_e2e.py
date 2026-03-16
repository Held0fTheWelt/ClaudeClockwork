"""E2E: run smoke demo (full CLI)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.e2e
def test_smoke_demo_e2e() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "claudeclockwork.cli.run_graph", str(ROOT / "demos" / "smoke" / "graph.json"), "--project-root", str(ROOT)],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert proc.returncode == 0
    assert json.loads(proc.stdout).get("status") == "ok"
