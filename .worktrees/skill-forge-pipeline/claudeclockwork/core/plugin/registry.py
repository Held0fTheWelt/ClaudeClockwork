from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from claudeclockwork.core.plugin.models import PluginManifest


class PluginRegistry:
    """Tracks plugin manifests and enabled/disabled state persisted to disk."""

    def __init__(
        self,
        manifests: list[PluginManifest],
        state_path: Path,
    ) -> None:
        self._manifests: dict[str, PluginManifest] = {m.id: m for m in manifests}
        self._state_path = Path(state_path)
        self._enabled: dict[str, bool] = {}
        self._load_state()

    # ── State persistence ────────────────────────────────────────────────────

    def _load_state(self) -> None:
        """Load enabled/disabled state from disk. Defaults to enabled_by_default."""
        if self._state_path.exists():
            try:
                data = json.loads(self._state_path.read_text(encoding="utf-8"))
                stored = {entry["id"]: entry.get("enabled", True) for entry in data.get("plugins", []) if "id" in entry}
            except Exception:
                stored = {}
        else:
            stored = {}

        for plugin_id, manifest in self._manifests.items():
            self._enabled[plugin_id] = stored.get(plugin_id, manifest.enabled_by_default)

    def _save_state(self) -> None:
        """Atomically write state to disk."""
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "count": len(self._manifests),
            "plugins": [
                {
                    "id": m.id,
                    "name": m.name,
                    "version": m.version,
                    "description": m.description,
                    "permissions": m.permissions,
                    "capabilities": m.capabilities,
                    "requires_plugins": m.requires_plugins,
                    "enabled": self._enabled.get(m.id, m.enabled_by_default),
                    "path": f"plugins/{m.id}/plugin.json",
                }
                for m in self._manifests.values()
            ],
        }
        # Atomic write: write to temp file then rename
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=str(self._state_path.parent), suffix=".tmp", prefix="plugin_index_"
        )
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            os.replace(tmp_path, str(self._state_path))
        except Exception:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            raise

    # ── Public API ──────────────────────────────────────────────────────────

    def list_plugins(self, enabled_only: bool = True) -> list[PluginManifest]:
        manifests = list(self._manifests.values())
        if enabled_only:
            manifests = [m for m in manifests if self._enabled.get(m.id, m.enabled_by_default)]
        return sorted(manifests, key=lambda m: m.id)

    def is_enabled(self, plugin_id: str) -> bool:
        if plugin_id not in self._manifests:
            return False
        return self._enabled.get(plugin_id, self._manifests[plugin_id].enabled_by_default)

    def enable(self, plugin_id: str) -> None:
        if plugin_id not in self._manifests:
            raise KeyError(f"Unknown plugin: {plugin_id!r}")
        self._enabled[plugin_id] = True
        self._save_state()

    def disable(self, plugin_id: str) -> None:
        if plugin_id not in self._manifests:
            raise KeyError(f"Unknown plugin: {plugin_id!r}")
        self._enabled[plugin_id] = False
        self._save_state()

    def get_capabilities(self, plugin_id: str) -> list[str]:
        m = self._manifests.get(plugin_id)
        return list(m.capabilities) if m else []

    def get_manifest(self, plugin_id: str) -> PluginManifest | None:
        return self._manifests.get(plugin_id)
