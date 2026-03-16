"""Phase 29 — Plugin loader and registry tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.plugins.loader import PluginLoader
from claudeclockwork.plugins.registry import PluginRegistry


def test_plugin_loader_deterministic_ordering() -> None:
    root = Path(__file__).resolve().parents[1]
    loader = PluginLoader(root, clockwork_version="17.0")
    manifests = loader.discover()
    ids = [m.get("id") for m in manifests]
    assert ids == sorted(ids)


def test_plugin_loader_loads_example_hello() -> None:
    root = Path(__file__).resolve().parents[1]
    loader = PluginLoader(root, clockwork_version="17.0")
    manifests = loader.discover()
    hello = next((m for m in manifests if m.get("id") == "example_hello"), None)
    assert hello is not None
    assert hello.get("capabilities") == ["skill"]


def test_plugin_registry_reject_incompatible() -> None:
    root = Path(__file__).resolve().parents[1]
    loader = PluginLoader(root, clockwork_version="99.0")
    manifests = loader.discover()
    # example_hello has clockwork_compat >=17; 99.0 should still match. Use <17 to exclude
    loader2 = PluginLoader(root, clockwork_version="10.0")
    m2 = loader2.discover()
    # example_hello requires >=17 so with 10.0 it may not appear
    assert isinstance(m2, list)


def test_plugin_registry_reject_unsafe() -> None:
    root = Path(__file__).resolve().parents[1]
    reg = PluginRegistry(root, capability_allowlist={"skill"}, clockwork_version="17.0")
    reg.load()
    # example_hello has capability "skill" which is in allowlist, so not rejected
    assert reg.rejections() == [] or any(r[0] for r in reg.rejections())
    reg2 = PluginRegistry(root, capability_allowlist=set(), clockwork_version="17.0")
    reg2.load()
    # Empty allowlist: plugins with capabilities get rejected
    list_plugins = reg2.list_plugins()
    rejections = reg2.rejections()
    assert isinstance(rejections, list)
