"""Phase 29 — Plugin discovery, loader, compatibility and validation."""
from __future__ import annotations

from claudeclockwork.plugins.loader import PluginLoader as ExtensionLoader
from claudeclockwork.plugins.registry import PluginRegistry as ExtensionRegistry

__all__ = ["ExtensionLoader", "ExtensionRegistry"]
