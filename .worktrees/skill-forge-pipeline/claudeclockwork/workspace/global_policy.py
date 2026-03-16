"""Phase 43 — Global policy: cross-repo writes denied; cross-project via bundle ids only."""
from __future__ import annotations

from claudeclockwork.core.errors import POLICY_DENIED


def check_cross_repo_write(allowed_project_ids: set[str], target_project_id: str) -> tuple[bool, str]:
    """Deny writes targeting another project. Cross-project only via bundle import."""
    if target_project_id in allowed_project_ids:
        return True, ""
    return False, POLICY_DENIED