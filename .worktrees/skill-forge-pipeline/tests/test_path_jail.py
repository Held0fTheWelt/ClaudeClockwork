"""Phase 34 — Path jail tests."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.core.path_jail import check_read_allowed, check_write_allowed
from claudeclockwork.core.errors import POLICY_DENIED


def test_write_deny_outside() -> None:
    with tempfile.TemporaryDirectory() as d:
        project = Path(d) / "proj"
        project.mkdir()
        runtime = project / ".clockwork_runtime"
        runtime.mkdir()
        outside = Path(d) / "other" / "file.txt"
        allowed, code = check_write_allowed(outside, project, runtime)
        assert not allowed
        assert code == POLICY_DENIED


def test_write_allow_under_runtime() -> None:
    with tempfile.TemporaryDirectory() as d:
        project = Path(d) / "proj"
        project.mkdir()
        runtime = project / ".clockwork_runtime"
        runtime.mkdir()
        allowed, _ = check_write_allowed(runtime / "out" / "f.txt", project, runtime)
        assert allowed


def test_read_deny_outside() -> None:
    with tempfile.TemporaryDirectory() as d:
        project = Path(d) / "proj"
        project.mkdir()
        runtime = project / ".clockwork_runtime"
        runtime.mkdir()
        outside = Path(d) / "etc" / "passwd"
        allowed, code = check_read_allowed(outside, project, runtime)
        assert not allowed
        assert code == POLICY_DENIED
