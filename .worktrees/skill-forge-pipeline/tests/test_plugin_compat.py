"""Phase 40 — Plugin compatibility."""
from __future__ import annotations

import pytest

from claudeclockwork.plugins.compat import is_compatible, parse_version


def test_compatible_range() -> None:
    ok, _ = is_compatible(">=17,<19", "17.0")
    assert ok
    ok2, _ = is_compatible(">=17", "18.0")
    assert ok2
    fail, msg = is_compatible(">=19", "17.0")
    assert not fail
    assert "below" in msg