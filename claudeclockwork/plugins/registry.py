"""Phase 29 — Plugin registry with validation and unsafe rejection."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from claudeclockwork.plugins.loader import PluginLoader


class PluginRegistry:
    """Registry of loaded plugins; rejects unsafe (capability not in allowlist)."""

    def __init__(
        self,
        project_root: Path | str,
        capability_allowlist: set[str] | None = None,
        clockwork_version: str = "17.0",
    ) -> None:
        self._root = Path(project_root).resolve()
        self._allowlist = capability_allowlist or set()
        self._loader = PluginLoader(self._root, clockwork_version)
        self._plugins: list[dict[str, Any]] = []
        self._rejected: list[tuple[str, str]] = []  # (id, reason)

    def load(self) -> None:
        """Discover and validate; reject unsafe."""
        self._plugins = []
        self._rejected = []
        for data in self._loader.discover():
            caps = set(data.get("capabilities", []))
            if self._allowlist and caps and not caps.issubset(self._allowlist):
                self._rejected.append((data.get("id", "?"), "unsafe_capability"))
                continue
            self._plugins.append(data)

    def list_plugins(self) -> list[dict[str, Any]]:
        """Return loaded plugin manifests (deterministic order)."""
        if not self._plugins:
            self.load()
        return sorted(self._plugins, key=lambda p: p.get("id", ""))

    def get_plugin(self, plugin_id: str) -> dict[str, Any] | None:
        for p in self.list_plugins():
            if p.get("id") == plugin_id:
                return p
        return None

    def rejections(self) -> list[tuple[str, str]]:
        return list(self._rejected)
