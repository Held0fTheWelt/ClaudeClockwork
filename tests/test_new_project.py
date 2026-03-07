"""Phase 37 — New project from template and workspace guardrails."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.cli.new_project import create_from_template
from claudeclockwork.workspace.guards import check_destructive_action


def test_template_creation_deterministic() -> None:
    with tempfile.TemporaryDirectory() as d:
        dest = Path(d) / "my_lib"
        out = create_from_template("python_lib", dest, project_id="my_lib")
        assert out.get("status") == "ok"
        assert (dest / "README.md").exists()
        assert (dest / ".gitignore").exists()


def test_new_fails_safely_if_dest_exists() -> None:
    with tempfile.TemporaryDirectory() as d:
        dest = Path(d) / "existing"
        dest.mkdir()
        (dest / "file.txt").write_text("x")
        out = create_from_template("python_lib", dest)
        assert out.get("status") == "error"
        assert "destination_not_empty" in out.get("error", "")


def test_workspace_guards_block_non_active() -> None:
    allowed, msg = check_destructive_action("proj_a", "proj_b", explicit_flag=False)
    assert not allowed
    assert "blocked" in msg
    allowed2, _ = check_destructive_action("proj_a", "proj_b", explicit_flag=True)
    assert allowed2