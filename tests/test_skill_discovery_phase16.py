"""
Phase 16 — Skill Discovery Wave tests.

4 tests per skill × 6 skills = 24 tests.
Pattern per skill:
  1. Registry check — skill ID is in the registry
  2. Status check — run_manifest_skill returns ok or fail (never raises)
  3. Output keys — all documented required output keys are present
  4. Empty/default inputs — calling with {} does not raise
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.runtime import build_registry

ROOT = Path(__file__).resolve().parents[1]

_PHASE16_SKILLS = [
    "git_summary",
    "test_run",
    "skill_health",
    "changelog_generate",
    "dependency_graph",
    "config_validate",
]


def _registry():
    return build_registry(ROOT)


def _run(skill_id: str, inputs: dict | None = None) -> dict:
    return run_manifest_skill(
        {"request_id": f"p16-{skill_id}", "skill_id": skill_id, "inputs": inputs or {}},
        ROOT,
    )


# ---------------------------------------------------------------------------
# git_summary
# ---------------------------------------------------------------------------

def test_git_summary_in_registry() -> None:
    assert _registry().get_manifest("git_summary") is not None


def test_git_summary_status() -> None:
    result = _run("git_summary", {"max_commits": 3})
    assert result is not None
    assert result.get("status") in ("ok", "fail"), result


def test_git_summary_output_keys() -> None:
    result = _run("git_summary", {"max_commits": 3})
    outputs = result.get("outputs", {})
    for key in ("commits", "files_changed", "commit_count"):
        assert key in outputs, f"git_summary missing output key: {key}"


def test_git_summary_empty_inputs() -> None:
    result = _run("git_summary", {})
    assert result is not None
    assert result.get("status") in ("ok", "fail")


# ---------------------------------------------------------------------------
# test_run (gate: skip actual pytest via CLOCKWORK_CI env var)
# ---------------------------------------------------------------------------

def test_test_run_in_registry() -> None:
    assert _registry().get_manifest("test_run") is not None


def test_test_run_status() -> None:
    os.environ["CLOCKWORK_CI"] = "1"
    try:
        result = _run("test_run", {"test_path": "tests/"})
    finally:
        del os.environ["CLOCKWORK_CI"]
    assert result is not None
    assert result.get("status") in ("ok", "fail"), result


def test_test_run_output_keys() -> None:
    os.environ["CLOCKWORK_CI"] = "1"
    try:
        result = _run("test_run", {})
    finally:
        del os.environ["CLOCKWORK_CI"]
    outputs = result.get("outputs", {})
    for key in ("passed", "failed", "errors", "duration_ms", "failures", "exit_code"):
        assert key in outputs, f"test_run missing output key: {key}"


def test_test_run_empty_inputs() -> None:
    os.environ["CLOCKWORK_CI"] = "1"
    try:
        result = _run("test_run", {})
    finally:
        del os.environ["CLOCKWORK_CI"]
    assert result is not None
    assert result.get("status") in ("ok", "fail")


# ---------------------------------------------------------------------------
# skill_health
# ---------------------------------------------------------------------------

def test_skill_health_in_registry() -> None:
    assert _registry().get_manifest("skill_health") is not None


def test_skill_health_status() -> None:
    result = _run("skill_health")
    assert result is not None
    assert result.get("status") in ("ok", "fail"), result


def test_skill_health_output_keys() -> None:
    result = _run("skill_health")
    outputs = result.get("outputs", {})
    for key in ("total", "healthy", "unhealthy", "issues"):
        assert key in outputs, f"skill_health missing output key: {key}"
    assert outputs.get("total", 0) >= 97, (
        f"skill_health must see >= 97 manifest skills, got {outputs.get('total')}"
    )


def test_skill_health_empty_inputs() -> None:
    result = _run("skill_health", {})
    assert result is not None
    assert result.get("status") in ("ok", "fail")


# ---------------------------------------------------------------------------
# changelog_generate
# ---------------------------------------------------------------------------

def test_changelog_generate_in_registry() -> None:
    assert _registry().get_manifest("changelog_generate") is not None


def test_changelog_generate_status() -> None:
    result = _run("changelog_generate", {"max_commits": 5})
    assert result is not None
    assert result.get("status") in ("ok", "fail"), result


def test_changelog_generate_output_keys() -> None:
    result = _run("changelog_generate", {"max_commits": 5})
    outputs = result.get("outputs", {})
    for key in ("entries", "changelog_text", "written"):
        assert key in outputs, f"changelog_generate missing output key: {key}"
    assert isinstance(outputs.get("entries"), list)
    assert isinstance(outputs.get("changelog_text"), str)
    assert outputs.get("written") is False  # no output_path provided


def test_changelog_generate_empty_inputs() -> None:
    result = _run("changelog_generate", {})
    assert result is not None
    assert result.get("status") in ("ok", "fail")


# ---------------------------------------------------------------------------
# dependency_graph
# ---------------------------------------------------------------------------

def test_dependency_graph_in_registry() -> None:
    assert _registry().get_manifest("dependency_graph") is not None


def test_dependency_graph_status() -> None:
    result = _run("dependency_graph", {"format": "json"})
    assert result is not None
    assert result.get("status") in ("ok", "fail"), result


def test_dependency_graph_output_keys() -> None:
    result = _run("dependency_graph", {"format": "json"})
    outputs = result.get("outputs", {})
    for key in ("nodes", "edges", "edge_count"):
        assert key in outputs, f"dependency_graph missing output key: {key}"
    assert isinstance(outputs["nodes"], list)
    assert isinstance(outputs["edges"], list)
    assert outputs["edge_count"] == len(outputs["edges"])


def test_dependency_graph_empty_inputs() -> None:
    result = _run("dependency_graph", {})
    assert result is not None
    assert result.get("status") in ("ok", "fail")


# ---------------------------------------------------------------------------
# config_validate
# ---------------------------------------------------------------------------

def test_config_validate_in_registry() -> None:
    assert _registry().get_manifest("config_validate") is not None


def test_config_validate_status() -> None:
    result = _run("config_validate")
    assert result is not None
    assert result.get("status") in ("ok", "fail"), result


def test_config_validate_output_keys() -> None:
    result = _run("config_validate")
    outputs = result.get("outputs", {})
    for key in ("files_checked", "valid", "invalid", "issues"):
        assert key in outputs, f"config_validate missing output key: {key}"
    assert outputs.get("files_checked", 0) > 0, (
        "config_validate must find at least one config file"
    )


def test_config_validate_empty_inputs() -> None:
    result = _run("config_validate", {})
    assert result is not None
    assert result.get("status") in ("ok", "fail")
