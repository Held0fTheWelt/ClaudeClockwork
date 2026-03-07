"""Phase 33 — Workspace config and boundary tests."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from claudeclockwork.workspace.config import load_workspace_config, get_project_runtime_root
from claudeclockwork.workspace.boundary import check_write_allowed
from claudeclockwork.core.errors import POLICY_DENIED


def test_workspace_config_deterministic() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "workspace.json").write_text('{"projects":[{"id":"p1","runtime_root":".rt"}],"active_project":"p1"}', encoding="utf-8")
        cfg = load_workspace_config(root)
        assert cfg.get("active_project") == "p1"
        assert len(cfg.get("projects", [])) == 1


def test_boundary_deny_outside_project() -> None:
    with tempfile.TemporaryDirectory() as d:
        project = Path(d) / "proj"
        project.mkdir()
        runtime = project / ".clockwork_runtime"
        runtime.mkdir()
        allowed, code = check_write_allowed(Path(d) / "other" / "file.txt", project, runtime)
        assert not allowed
        assert code == POLICY_DENIED
