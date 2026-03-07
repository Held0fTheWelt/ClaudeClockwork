"""Phase 33 — Boundary enforcement: deny writes outside project root (except runtime root)."""
from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.errors import POLICY_DENIED


def check_write_allowed(resolved_path: Path, project_root: Path, runtime_root: Path) -> tuple[bool, str]:
    """Return (allowed, error_code). Deny writes outside project root except under runtime_root."""
    project_root = project_root.resolve()
    runtime_root = runtime_root.resolve()
    try:
        resolved_path = resolved_path.resolve()
    except OSError:
        return False, POLICY_DENIED
    try:
        if resolved_path == runtime_root or (resolved_path.is_relative_to(runtime_root) if hasattr(resolved_path, "is_relative_to") else str(resolved_path).startswith(str(runtime_root))):
            return True, ""
    except (ValueError, AttributeError):
        pass
    if resolved_path == project_root:
        return True, ""
    for parent in resolved_path.parents:
        if parent == runtime_root or parent == project_root:
            return True, ""
    return False, POLICY_DENIED
