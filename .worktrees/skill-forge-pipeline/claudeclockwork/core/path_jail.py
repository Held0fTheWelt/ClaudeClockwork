"""Phase 34 — Path jail: deny read/write outside project root, runtime root, or allowlist."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from claudeclockwork.core.errors import POLICY_DENIED


def resolve_safe(path: Path, base: Path) -> Path:
    """Resolve path; normalize .. to stay under base if possible."""
    try:
        p = (base / path).resolve()
        return p
    except OSError:
        return Path()


def _under(root: Path, path: Path) -> bool:
    """True if path is root or under root."""
    try:
        return path == root or path.is_relative_to(root)
    except (ValueError, AttributeError):
        return path == root or str(path).startswith(str(root) + "/") or str(path).startswith(str(root) + "\\")


def check_read_allowed(
    resolved_path: Path,
    project_root: Path,
    runtime_root: Path,
    read_only_allowlist: Sequence[Path] = (),
) -> tuple[bool, str]:
    """Allow read only under project_root, runtime_root, or read_only_allowlist."""
    project_root = project_root.resolve()
    runtime_root = runtime_root.resolve()
    try:
        resolved_path = resolved_path.resolve()
    except OSError:
        return False, POLICY_DENIED
    if _under(project_root, resolved_path) or _under(runtime_root, resolved_path):
        return True, ""
    for allowed in read_only_allowlist:
        try:
            a = allowed.resolve()
            if _under(a, resolved_path):
                return True, ""
        except OSError:
            continue
    return False, POLICY_DENIED


def check_write_allowed(
    resolved_path: Path,
    project_root: Path,
    runtime_root: Path,
) -> tuple[bool, str]:
    """Allow write only under project_root or runtime_root. Deny ../ and absolute outside."""
    project_root = project_root.resolve()
    runtime_root = runtime_root.resolve()
    try:
        resolved_path = resolved_path.resolve()
    except OSError:
        return False, POLICY_DENIED
    if _under(runtime_root, resolved_path) or resolved_path == runtime_root:
        return True, ""
    if _under(project_root, resolved_path) or resolved_path == project_root:
        return True, ""
    return False, POLICY_DENIED
