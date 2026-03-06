from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.runtime import build_registry

PROJECT_ROOT = Path(__file__).resolve().parents[1]

WAVE3_SKILLS = [
    "determinism_proof",
    "hardening_scan_fix",
    "drift_semantic_check",
    "team_topology_verify",
    "reference_fix",
    "outcome_event_generate",
    "outcome_ledger_append",
    "clockwork_version_bump",
    "telemetry_summarize",
    "performance_toggle",
    "performance_finalize",
]

# Skills that require specific inputs or optional system deps — tested for execution shape only
_SHAPE_ONLY = {
    # drift_semantic_check reports real repo drift — status varies by repo state
    "drift_semantic_check",
    # outcome_ledger_append requires a structured event object
    "outcome_ledger_append",
    # performance_finalize calls efficiency_review which requires matplotlib
    "performance_finalize",
}


@pytest.mark.parametrize("skill_id", WAVE3_SKILLS)
def test_wave3_skill_in_registry(skill_id: str) -> None:
    """Every Wave 3 skill must be discoverable in the registry."""
    registry = build_registry(PROJECT_ROOT)
    names = {s.name for s in registry.list_skills(enabled_only=False)}
    assert skill_id in names, f"{skill_id} not found in registry"


@pytest.mark.parametrize("skill_id", WAVE3_SKILLS)
def test_wave3_skill_executes(skill_id: str) -> None:
    """Every Wave 3 skill must execute via the manifest bridge and return a valid result dict."""
    inputs: dict = {}
    if skill_id == "outcome_ledger_append":
        inputs = {"event": {"type": "outcome_ledger_event", "skill_id": "test", "status": "ok"}}

    result = run_manifest_skill(
        {"request_id": "test", "skill_id": skill_id, "inputs": inputs},
        PROJECT_ROOT,
    )
    assert result is not None
    assert "status" in result, f"{skill_id}: result has no 'status' key"

    if skill_id not in _SHAPE_ONLY:
        assert result["status"] == "ok", f"{skill_id} failed: {result.get('errors')}"


def test_capability_map_reports_45_skills() -> None:
    """capability_map_build must report at least 45 manifest skills after Wave 3."""
    result = run_manifest_skill(
        {"request_id": "test", "skill_id": "capability_map_build", "inputs": {}},
        PROJECT_ROOT,
    )
    assert result is not None
    assert result["status"] == "ok"
    # legacy skill returns key 'manifest_skills' (int count)
    manifest_count = result["outputs"].get("manifest_skills", 0)
    assert manifest_count >= 45, f"Expected >=45 manifest skills, got {manifest_count}"


def test_wave3_manifests_pass_validate() -> None:
    """manifest_validate must report valid=true with all Wave 3 skills present."""
    result = run_manifest_skill(
        {"request_id": "test", "skill_id": "manifest_validate", "inputs": {}},
        PROJECT_ROOT,
    )
    assert result is not None
    assert result["status"] == "ok"
    assert result["outputs"]["valid"] is True, f"Validation errors: {result['outputs'].get('errors')}"
    assert result["outputs"]["checked"] >= 45
