from __future__ import annotations


class PermissionManager:
    def __init__(self, allowed: set[str] | None = None, blocked: set[str] | None = None) -> None:
        self.allowed = allowed or set()
        self.blocked = blocked or set()

    def validate(self, requested: list[str]) -> tuple[bool, str | None]:
        for permission in requested:
            if permission in self.blocked:
                return False, f"Blocked permission: {permission}"
            if self.allowed and permission not in self.allowed:
                return False, f"Permission not granted: {permission}"
        return True, None
