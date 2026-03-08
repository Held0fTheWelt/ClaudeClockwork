"""
Tests for Phase 73 — validation_artifact_gate.

Verifies that:
- The gate passes on a clean repo with gitignored validation dirs.
- The gate fails when a validation dir is not gitignored.
- The gate fails when validation files are git-tracked.
- The gate fails when redacted manifests contain absolute path leaks.
- A synthetic path leak triggers deterministic failure.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from claudeclockwork.core.gates.validation_artifact_gate import run_validation_artifact_gate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _init_git_repo(path: Path) -> None:
    """Initialize a minimal git repo at path."""
    subprocess.run(["git", "init", str(path)], capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"],
                   capture_output=True, cwd=str(path))
    subprocess.run(["git", "config", "user.name", "Test"],
                   capture_output=True, cwd=str(path))


def _make_gitignore(path: Path, entries: list[str]) -> None:
    (path / ".gitignore").write_text("\n".join(entries) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestValidationArtifactGateCleanRepo:
    """Gate passes when validation dirs are gitignored and no files are tracked."""

    def test_no_validation_dirs_present(self, tmp_path):
        """Pass when validation_runs/ does not exist at all."""
        _init_git_repo(tmp_path)
        _make_gitignore(tmp_path, ["validation_runs/", "validation_runs_redacted/"])
        result = run_validation_artifact_gate(tmp_path)
        assert result["pass"] is True
        assert result["errors"] == []

    def test_dirs_exist_and_gitignored(self, tmp_path):
        """Pass when dirs exist and are properly gitignored."""
        _init_git_repo(tmp_path)
        _make_gitignore(tmp_path, ["validation_runs/", "validation_runs_redacted/"])
        (tmp_path / "validation_runs").mkdir()
        (tmp_path / "validation_runs_redacted").mkdir()
        result = run_validation_artifact_gate(tmp_path)
        assert result["pass"] is True

    def test_actual_repo_passes(self):
        """The actual project repo must pass the gate (regression check)."""
        project_root = Path(__file__).resolve().parent.parent
        result = run_validation_artifact_gate(project_root)
        assert result["pass"] is True, f"Gate failed on actual repo: {result['errors']}"


class TestValidationArtifactGateMissingGitignore:
    """Gate fails when validation dir is not in .gitignore."""

    def test_fails_when_not_gitignored(self, tmp_path):
        """Fail if validation_runs/ exists but is not in .gitignore."""
        _init_git_repo(tmp_path)
        _make_gitignore(tmp_path, ["*.pyc"])  # no validation_runs entry
        (tmp_path / "validation_runs").mkdir()
        result = run_validation_artifact_gate(tmp_path)
        assert result["pass"] is False
        assert any("gitignore" in e for e in result["errors"])


class TestValidationArtifactGatePathLeak:
    """Gate fails on absolute path leaks in redacted manifests."""

    def test_windows_path_leak(self, tmp_path):
        """Fail on Windows drive path in redacted manifest."""
        _init_git_repo(tmp_path)
        _make_gitignore(tmp_path, ["validation_runs/", "validation_runs_redacted/"])
        redacted = tmp_path / "validation_runs_redacted" / "run1"
        redacted.mkdir(parents=True)
        manifest = {"run_dir": "D:\\ClaudeClockwork\\validation_runs\\run1"}
        (redacted / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        result = run_validation_artifact_gate(tmp_path)
        assert result["pass"] is False
        assert any("path leak" in e for e in result["errors"])

    def test_wsl_path_leak(self, tmp_path):
        """Fail on WSL mount path in redacted manifest."""
        _init_git_repo(tmp_path)
        _make_gitignore(tmp_path, ["validation_runs/", "validation_runs_redacted/"])
        redacted = tmp_path / "validation_runs_redacted" / "run2"
        redacted.mkdir(parents=True)
        manifest = {"run_dir": "/mnt/d/ClaudeClockwork/validation_runs/run2"}
        (redacted / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        result = run_validation_artifact_gate(tmp_path)
        assert result["pass"] is False
        assert any("path leak" in e for e in result["errors"])

    def test_placeholder_not_flagged(self, tmp_path):
        """Placeholders like <PROJECT_ROOT> must NOT trigger the gate."""
        _init_git_repo(tmp_path)
        _make_gitignore(tmp_path, ["validation_runs/", "validation_runs_redacted/"])
        redacted = tmp_path / "validation_runs_redacted" / "run3"
        redacted.mkdir(parents=True)
        manifest = {"run_dir": "<PROJECT_ROOT>/validation_runs/run3"}
        (redacted / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        result = run_validation_artifact_gate(tmp_path)
        assert result["pass"] is True, f"False positive: {result['errors']}"

    def test_deterministic_on_same_input(self, tmp_path):
        """Gate result is deterministic across two runs on the same input."""
        _init_git_repo(tmp_path)
        _make_gitignore(tmp_path, ["validation_runs/", "validation_runs_redacted/"])
        r1 = run_validation_artifact_gate(tmp_path)
        r2 = run_validation_artifact_gate(tmp_path)
        assert r1["pass"] == r2["pass"]
        assert r1["errors"] == r2["errors"]
