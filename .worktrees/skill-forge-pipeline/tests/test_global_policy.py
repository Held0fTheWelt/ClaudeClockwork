"""Phase 43 — Global policy: cross-repo write denied."""
from __future__ import annotations

import pytest

from claudeclockwork.workspace.global_policy import check_cross_repo_write
from claudeclockwork.core.errors import POLICY_DENIED


def test_cross_repo_write_denied() -> None:
    allowed, _ = check_cross_repo_write({"p1"}, "p2")
    assert not allowed
    _, code = check_cross_repo_write({"p1"}, "p2")
    assert code == POLICY_DENIED