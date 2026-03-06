"""
Phase 7 — Wrapper Wave 4 tests.

Verifies that all 52 newly-wrapped legacy skills are discoverable and
return a well-formed result dict via run_manifest_skill.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.runtime import build_registry

ROOT = Path(__file__).resolve().parents[1]

# All 52 skills wrapped in Wave 4 (excludes _event_logger and _report_publish)
_WAVE4_SKILLS = [
    # routing
    "bandit_router_select", "budget_router", "budget_analyze", "escalation_router",
    "model_routing_select", "model_routing_record_outcome", "route_autotune_suggest",
    "route_profile_update", "route_profile_patch_pack",
    # planning
    "create_mvp", "creativity_burst", "decision_feedback", "deliberation_pack_build",
    "economics_regression", "edge_case_selector", "hypothesis_builder", "idea_dedupe",
    "idea_scoring", "plan_diff_apply", "plan_lint", "plan_mutate", "triad_build",
    "triad_ref_lint", "work_scope_assess",
    # analysis
    "code_assimilate", "limitation_harvest_scan", "mechanic_explain", "mutation_detect",
    "pattern_detect", "system_map",
    # docs
    "autodocs_generate", "copyright_standardize", "doc_review", "doc_ssot_resolver",
    "doc_write", "pdf_export", "screencast_script", "tutorial_write", "log_standardize",
    # performance
    "token_event_log", "prompt_debt_capture", "efficiency_review",
    "shadow_prompt", "shadow_prompt_minify",
    # archive
    "last_train", "last_train_merge",
    # misc
    "critics_board_review", "exec_dryrun", "review_panel",
    # demo
    "report", "scan", "hello",
]


def test_wave4_total_manifest_skills() -> None:
    """Registry must report ≥ 97 manifest skills after Wave 4."""
    registry = build_registry(ROOT)
    count = len(registry.list_skills(enabled_only=False))
    assert count >= 97, f"Expected ≥ 97 manifest skills, got {count}"


def test_internal_helpers_not_wrapped() -> None:
    """_event_logger and _report_publish must NOT be in the manifest registry."""
    registry = build_registry(ROOT)
    names = {m.name for m in registry.list_skills(enabled_only=False)}
    assert "_event_logger" not in names
    assert "_report_publish" not in names


@pytest.mark.parametrize("skill_id", _WAVE4_SKILLS)
def test_wave4_skill_in_registry(skill_id: str) -> None:
    """Every Wave 4 skill must have a manifest in the registry."""
    registry = build_registry(ROOT)
    manifest = registry.get_manifest(skill_id)
    assert manifest is not None, f"{skill_id} not found in registry"
    assert manifest.metadata.get("legacy_bridge") == skill_id


@pytest.mark.parametrize("skill_id", _WAVE4_SKILLS)
def test_wave4_skill_executes(skill_id: str) -> None:
    """Every Wave 4 skill must return a well-formed result dict (any status)."""
    result = run_manifest_skill(
        {"request_id": "wave4", "skill_id": skill_id, "inputs": {}},
        ROOT,
    )
    assert result is not None, f"{skill_id}: run_manifest_skill returned None"
    assert result.get("status") in ("ok", "fail"), (
        f"{skill_id}: unexpected status {result.get('status')!r}"
    )
    assert "errors" in result, f"{skill_id}: result missing 'errors' key"


def test_wave4_manifests_pass_validate() -> None:
    """All Wave 4 manifests must pass the manifest lint gate (strict mode)."""
    registry = build_registry(ROOT, strict=True)
    wave4_errors = [
        e for e in registry.validation_errors
        if e.get("skill") in set(_WAVE4_SKILLS)
    ]
    assert not wave4_errors, (
        f"Wave 4 manifest validation errors:\n"
        + "\n".join(str(e) for e in wave4_errors)
    )


def test_budget_router_oodle_renamed() -> None:
    """budget_router output must use 'local_model_tier', not 'oodle_tier'."""
    result = run_manifest_skill(
        {"request_id": "wave4", "skill_id": "budget_router",
         "inputs": {"complexity": 2, "risk": 2, "urgency": 2, "mode": "balanced"}},
        ROOT,
    )
    assert result is not None
    if result.get("status") == "ok":
        decision = result.get("outputs", {}).get("decision", {})
        assert "local_model_tier" in decision, (
            f"Expected 'local_model_tier' in decision, got keys: {list(decision.keys())}"
        )
        assert "oodle_tier" not in decision, "Stale 'oodle_tier' key still present"
