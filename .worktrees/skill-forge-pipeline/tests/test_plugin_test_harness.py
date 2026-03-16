"""Phase 40 — Plugin test harness."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.plugins.test_harness import has_smoke_test


def test_has_smoke_when_test_file_exists() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "test_smoke.py").write_text("# smoke")
        assert has_smoke_test({}, root) is True


def test_no_smoke_without_test() -> None:
    with tempfile.TemporaryDirectory() as d:
        assert has_smoke_test({}, d) is False