from __future__ import annotations


class PermissionManager:
    def __init__(self, allowed: set[str] | None = None, blocked: set[str] | None = None) -> None:
        self.allowed = allowed or set()
        self.blocked = blocked or set()

    def is_allowed(self, permission: str) -> bool:
        """Return True if *permission* is permitted under current policy.

        Rules:
        - Always False if *permission* is in ``blocked``.
        - If ``allowed`` is non-empty, only True if *permission* is in ``allowed``.
        - If ``allowed`` is empty (no restrictions), True for everything not blocked.
        """
        if permission in self.blocked:
            return False
        if self.allowed and permission not in self.allowed:
            return False
        return True

    def validate(self, requested: list[str]) -> tuple[bool, str | None]:
        for permission in requested:
            if permission in self.blocked:
                return False, f"Blocked permission: {permission}"
            if self.allowed and permission not in self.allowed:
                return False, f"Permission not granted: {permission}"
        return True, None
