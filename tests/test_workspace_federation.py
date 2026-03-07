"""Phase 43 — Federation: selection stable and persists."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.workspace.federation import load_federation_config, set_active


def test_federation_selection_persists() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        set_active(root, workspace_id="ws1", project_id="p1")
        cfg = load_federation_config(root)
        assert cfg.get("active_workspace") == "ws1"
        assert cfg.get("active_project") == "p1"