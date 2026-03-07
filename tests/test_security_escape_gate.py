"""Phase 34 — Security escape gate tests."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from claudeclockwork.core.gates.security_escape_gate import run_security_escape_gate


def test_gate_passes_with_clean_logs() -> None:
    with tempfile.TemporaryDirectory() as d:
        project = Path(d) / "proj"
        project.mkdir()
        runtime = project / ".clockwork_runtime"
        runtime.mkdir()
        out = run_security_escape_gate(project, runtime, recent_log_lines=["hello", "world"])
    assert out.get("passed") is True


def test_gate_fails_unsafe_in_ci() -> None:
    with tempfile.TemporaryDirectory() as d:
        project = Path(d) / "proj"
        project.mkdir()
        runtime = project / ".clockwork_runtime"
        runtime.mkdir()
        prev = os.environ.get("CI"), os.environ.get("CLOCKWORK_UNSAFE_MODE")
        try:
            os.environ["CI"] = "true"
            os.environ["CLOCKWORK_UNSAFE_MODE"] = "1"
            out = run_security_escape_gate(project, runtime, [])
            assert out.get("passed") is False
            assert "unsafe" in out.get("reason", "").lower()
        finally:
            if prev[0] is None:
                os.environ.pop("CI", None)
            else:
                os.environ["CI"] = prev[0]
            if prev[1] is None:
                os.environ.pop("CLOCKWORK_UNSAFE_MODE", None)
            else:
                os.environ["CLOCKWORK_UNSAFE_MODE"] = prev[1]
