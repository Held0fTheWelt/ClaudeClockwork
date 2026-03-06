from __future__ import annotations

import json
from pathlib import Path

from claudeclockwork.core.plugin.models import PluginManifest


class PluginLoader:
    def discover(self, plugin_root: Path) -> list[PluginManifest]:
        """Scan plugin_root/*/plugin.json and return parsed manifests."""
        plugin_root = Path(plugin_root).resolve()
        if not plugin_root.exists():
            return []
        manifests: list[PluginManifest] = []
        for plugin_json in sorted(plugin_root.glob("*/plugin.json")):
            try:
                manifests.append(self.load_manifest(plugin_json))
            except Exception:
                pass  # malformed plugin.json — skip silently
        return manifests

    def load_manifest(self, path: Path) -> PluginManifest:
        """Parse a single plugin.json into a PluginManifest."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        # Ensure id defaults to directory name if not set
        if "id" not in data:
            data["id"] = Path(path).parent.name
        if not data.get("name"):
            data["name"] = data["id"]
        return PluginManifest.from_dict(data)
