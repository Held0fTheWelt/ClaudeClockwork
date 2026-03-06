from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.runtime import build_registry

PROJECT_ROOT = Path(__file__).resolve().parents[1]

NATIVE_SKILLS = [
    "skill_registry_search",
    "capability_map_build",
    "skill_scaffold",
    "repo_validate",
    "spec_validate",
    "qa_gate",
    "evidence_bundle_build",
    "security_redactor",
    "parity_scan_and_mvp_planner",
    "eval_run",
    "pdf_quality",
]


def _run(skill_id: str, inputs: dict | None = None) -> dict:
    result = run_manifest_skill(
        {"request_id": "test", "skill_id": skill_id, "inputs": inputs or {}},
        PROJECT_ROOT,
    )
    assert result is not None, f"{skill_id}: no result returned"
    return result


# ── Unit-level assertions per native skill ────────────────────────────────────


def test_skill_registry_search_returns_matches() -> None:
    result = _run("skill_registry_search", {"query": "qa"})
    assert result["status"] == "ok"
    assert result["outputs"]["summary"]["manifest_matches"] > 0


def test_skill_registry_search_requires_query() -> None:
    result = _run("skill_registry_search", {})
    assert result["status"] == "fail"
    assert any("query" in e for e in result["errors"])


def test_capability_map_build_counts_skills() -> None:
    result = _run("capability_map_build")
    assert result["status"] == "ok"
    assert result["outputs"]["manifest_skills"] >= 45
    assert result["outputs"]["legacy_skills"] > 0


def test_skill_scaffold_dry_run_produces_manifest() -> None:
    result = _run("skill_scaffold", {
        "skill_name": "test_native_skill",
        "category": "misc",
        "description": "Test skill for Phase 3 native scaffold validation.",
        "dry_run": True,
    })
    assert result["status"] == "ok"
    assert result["outputs"]["dry_run"] is True
    preview = result["outputs"]["manifest_preview"]
    assert preview["name"] == "test_native_skill"
    assert preview["category"] == "misc"
    assert "TestNativeSkillSkill" in preview["entrypoint"]
    assert preview.get("id") == "test_native_skill"


def test_skill_scaffold_rejects_invalid_name() -> None:
    result = _run("skill_scaffold", {
        "skill_name": "Invalid-Name",
        "category": "misc",
        "description": "Should fail.",
        "dry_run": True,
    })
    assert result["status"] == "fail"


def test_repo_validate_passes_on_clean_repo() -> None:
    result = _run("repo_validate")
    assert result["status"] == "ok"
    assert result["outputs"]["pass"] is True
    assert result["outputs"]["bad_json_count"] == 0


def test_spec_validate_requires_schema() -> None:
    result = _run("spec_validate", {})
    assert result["status"] == "fail"
    assert any("schema" in e for e in result["errors"])


def test_spec_validate_passes_valid_manifest() -> None:
    result = _run("spec_validate", {
        "schema": ".claude/contracts/schemas/manifest_schema.json",
        "examples": [".claude/skills/meta/manifest_validate/manifest.json"],
    })
    assert result["status"] == "ok"
    assert result["outputs"]["valid"] is True


def test_qa_gate_passes_at_level_1() -> None:
    result = _run("qa_gate", {"gate_level": 1})
    assert result["status"] == "ok"
    assert result["outputs"]["pass"] is True
    assert "manifest_validate" in result["outputs"]["gate_results"]


def test_evidence_bundle_build_creates_hash() -> None:
    result = _run("evidence_bundle_build", {
        "artifacts": ["VERSION"],
        "bundle_name": "test_phase3_bundle",
    })
    assert result["status"] == "ok"
    assert "manifest_hash" in result["outputs"]
    assert result["outputs"]["artifact_count"] == 1


def test_security_redactor_dry_run_finds_no_secrets() -> None:
    result = _run("security_redactor", {
        "input_dir": ".claude/contracts/schemas",
        "dry_run": True,
    })
    assert result["status"] == "ok"
    assert result["outputs"]["dry_run"] is True
    assert isinstance(result["outputs"]["redacted_count"], int)


def test_parity_scan_detects_unwrapped_skills() -> None:
    result = _run("parity_scan_and_mvp_planner")
    assert result["status"] == "ok"
    assert result["outputs"]["unwrapped_count"] >= 0
    assert "wrap_candidates" in result["outputs"]
    assert result["outputs"]["parity_percent"] >= 0


def test_eval_run_returns_result_path() -> None:
    result = _run("eval_run")
    assert result["status"] == "ok"
    assert "results_path" in result["outputs"]
    assert Path(result["outputs"]["results_path"]).exists()


def test_pdf_quality_requires_manuscript() -> None:
    result = _run("pdf_quality", {})
    assert result["status"] == "fail"
    assert any("manuscript" in e for e in result["errors"])


def test_pdf_quality_scores_readme() -> None:
    result = _run("pdf_quality", {"manuscript_path": "README.md"})
    assert result["status"] == "ok"
    assert "score" in result["outputs"]
    assert 0 <= result["outputs"]["score"] <= 100
    assert "dimension_scores" in result["outputs"]


@pytest.mark.parametrize("skill_id", NATIVE_SKILLS)
def test_native_skill_is_not_legacy_adapter(skill_id: str) -> None:
    """All Phase 3 skills must NOT be LegacySkillAdapter subclasses."""
    from claudeclockwork.legacy.adapter import LegacySkillAdapter

    registry = build_registry(PROJECT_ROOT)
    cls = registry._classes.get(skill_id)
    assert cls is not None, f"{skill_id} not found in registry"
    assert not issubclass(cls, LegacySkillAdapter), \
        f"{skill_id} is still a LegacySkillAdapter — native implementation required"
