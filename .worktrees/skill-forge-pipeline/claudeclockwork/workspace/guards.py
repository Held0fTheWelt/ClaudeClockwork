"""Phase 37 — Guardrails: confirm before modifying non-active project; block in non-interactive unless flag."""
from __future__ import annotations

import os
from typing import Any


def check_destructive_action(
    active_project_id: str | None,
    target_project_id: str | None,
    explicit_flag: bool = False,
    ci: bool | None = None,
) -> tuple[bool, str]:
    """Return (allowed, message). In CI or non-interactive, require explicit_flag to proceed for non-active."""
    if active_project_id is None or target_project_id is None:
        return True, ""
    if active_project_id == target_project_id:
        return True, ""
    is_ci = ci if ci is not None else os.environ.get("CI") == "true"
    if is_ci or not explicit_flag:
        return False, "modify_non_active_blocked"
    return True, ""
