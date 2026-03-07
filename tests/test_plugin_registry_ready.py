"""Phase 47 — CI: validate plugin submission bundles deterministically."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from claudeclockwork.plugins.bundle_validator import validate_bundle
from claudeclockwork.plugins.publish import run_publish_workflow

ROOT = Path(__file__).resolve().parents[1]


def test_bundle_validator_accepts_valid_bundle(tmp_path: Path) -> None:
    (tmp_path / "plugin.json").write_text(json.dumps({"id": "test_plugin", "version": "1.0"}), encoding="utf-8")
    ok, errors = validate_bundle(tmp_path)
    assert ok, errors
    assert not errors


def test_bundle_validator_rejects_missing_manifest(tmp_path: Path) -> None:
    ok, errors = validate_bundle(tmp_path)
    assert not ok
    assert any("plugin.json" in e for e in errors)


def test_bundle_validator_rejects_manifest_without_id(tmp_path: Path) -> None:
    (tmp_path / "plugin.json").write_text(json.dumps({"version": "1.0"}), encoding="utf-8")
    ok, errors = validate_bundle(tmp_path)
    assert not ok
    assert any("id" in e for e in errors)


def test_publish_workflow_valid_bundle(tmp_path: Path) -> None:
    (tmp_path / "plugin.json").write_text(json.dumps({"id": "ci_plugin", "version": "1.0"}), encoding="utf-8")
    project = tmp_path / "project"
    project.mkdir()
    (project / ".clockwork_runtime").mkdir(parents=True, exist_ok=True)
    result = run_publish_workflow(tmp_path, project, update_allowlist=True)
    assert result["ok"] is True, result.get("errors")
    assert result.get("hash")
    assert result.get("index_updated") is True
