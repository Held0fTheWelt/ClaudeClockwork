"""Phase 37 — Workspace guardrails: non-active project modification blocked."""
from __future__ import annotations

import pytest

from claudeclockwork.workspace.guards import check_destructive_action


def test_modify_non_active_blocked_by_default() -> None:
    allowed, msg = check_destructive_action("active", "other", explicit_flag=False)
    assert not allowed
    assert msg == "modify_non_active_blocked"


def test_same_project_allowed() -> None:
    allowed, _ = check_destructive_action("proj", "proj", explicit_flag=False)
    assert allowed