from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.security.permissions import PermissionManager
from claudeclockwork.runtime import _load_permissions

ROOT = Path(__file__).resolve().parents[1]


def test_permission_manager_allows_declared() -> None:
    mgr = PermissionManager(allowed={"repo:read"}, blocked=set())
    assert mgr.is_allowed("repo:read") is True


def test_permission_manager_blocks_undeclared() -> None:
    mgr = PermissionManager(allowed={"repo:read"}, blocked=set())
    assert mgr.is_allowed("shell:admin") is False


def test_permission_manager_explicit_block_overrides_allowed() -> None:
    # shell:admin is in allowed but also in blocked — blocked wins
    mgr = PermissionManager(allowed={"repo:read", "shell:admin"}, blocked={"shell:admin"})
    assert mgr.is_allowed("shell:admin") is False


def test_permission_manager_default_allows_everything() -> None:
    # Empty allowed set means no allowlist restriction
    mgr = PermissionManager()
    assert mgr.is_allowed("repo:read") is True
    assert mgr.is_allowed("anything:goes") is True


def test_load_permissions_from_config() -> None:
    # configs/permissions.json blocks shell:admin and system:kill
    mgr = _load_permissions(ROOT)
    assert mgr.is_allowed("shell:admin") is False
    assert mgr.is_allowed("system:kill") is False
    # These are in the allowed list
    assert mgr.is_allowed("repo:read") is True
    assert mgr.is_allowed("qa:run") is True
