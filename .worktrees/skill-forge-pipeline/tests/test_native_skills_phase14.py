"""
Phase 14 — Native Skill Promotion tests.

24 tests (4 per skill × 6 skills):
  1. Entrypoint not LegacySkillAdapter
  2. Smoke run returns ok
  3. Output keys present
  4. Graceful empty / default inputs
"""

from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.runtime import build_registry
from claudeclockwork.core.base.skill_base import SkillBase

ROOT = Path(__file__).resolve().parents[1]


def _run(skill_id: str, inputs: dict | None = None) -> dict:
    result = run_manifest_skill(
        {"request_id": "p14", "skill_id": skill_id, "inputs": inputs or {}},
        ROOT,
    )
    assert result is not None, f"{skill_id}: no result returned"
    return result


def _is_native(skill_id: str) -> bool:
    """Phase 17: all skills are native (SkillBase)."""
    registry = build_registry(ROOT)
    cls = registry._classes.get(skill_id)
    assert cls is not None, f"{skill_id} not found in registry"
    return issubclass(cls, SkillBase)


# ---------------------------------------------------------------------------
# capability_map_build — already native from Phase 3
# ---------------------------------------------------------------------------

def test_capability_map_build_is_native() -> None:
    assert _is_native("capability_map_build")


def test_capability_map_build_smoke() -> None:
    result = _run("capability_map_build")
    assert result["status"] == "ok"


def test_capability_map_build_output_keys() -> None:
    result = _run("capability_map_build")
    assert result["status"] == "ok"
    assert "manifest_skills" in result["outputs"]
    assert result["outputs"]["manifest_skills"] > 0


def test_capability_map_build_empty_inputs_use_defaults() -> None:
    result = _run("capability_map_build", {})
    assert result["status"] == "ok"
    assert isinstance(result["outputs"].get("legacy_skills"), int)


# ---------------------------------------------------------------------------
# skill_registry_search — already native from Phase 3
# ---------------------------------------------------------------------------

def test_skill_registry_search_is_native() -> None:
    assert _is_native("skill_registry_search")


def test_skill_registry_search_smoke() -> None:
    result = _run("skill_registry_search", {"query": "qa"})
    assert result["status"] == "ok"


def test_skill_registry_search_output_keys() -> None:
    result = _run("skill_registry_search", {"query": "qa"})
    assert "summary" in result["outputs"]
    assert "manifest_hits" in result["outputs"]


def test_skill_registry_search_requires_query() -> None:
    result = _run("skill_registry_search", {})
    assert result["status"] == "fail"


# ---------------------------------------------------------------------------
# qa_gate — already native from Phase 3
# ---------------------------------------------------------------------------

def test_qa_gate_is_native() -> None:
    assert _is_native("qa_gate")


def test_qa_gate_smoke() -> None:
    result = _run("qa_gate", {"gate_level": 1})
    assert result["status"] == "ok"


def test_qa_gate_output_keys() -> None:
    result = _run("qa_gate", {"gate_level": 1})
    assert "pass" in result["outputs"]
    assert "gate_results" in result["outputs"]


def test_qa_gate_empty_inputs_use_defaults() -> None:
    result = _run("qa_gate", {})
    assert result["status"] in ("ok", "fail")
    assert "gate_results" in result["outputs"]


# ---------------------------------------------------------------------------
# eval_run — already native from Phase 3
# ---------------------------------------------------------------------------

def test_eval_run_is_native() -> None:
    assert _is_native("eval_run")


def test_eval_run_smoke() -> None:
    result = _run("eval_run")
    assert result["status"] == "ok"


def test_eval_run_output_keys() -> None:
    result = _run("eval_run")
    assert "results_path" in result["outputs"]
    assert "pass_count" in result["outputs"]
    assert "fail_count" in result["outputs"]


def test_eval_run_results_file_exists() -> None:
    result = _run("eval_run")
    assert result["status"] == "ok"
    results_path = Path(result["outputs"]["results_path"])
    assert results_path.exists()


# ---------------------------------------------------------------------------
# budget_router — promoted to native in Phase 14
# ---------------------------------------------------------------------------

def test_budget_router_is_native() -> None:
    assert _is_native("budget_router")


def test_budget_router_smoke() -> None:
    result = _run("budget_router", {"complexity": 3, "risk": 2, "urgency": 1, "mode": "balanced"})
    assert result["status"] == "ok"


def test_budget_router_output_keys() -> None:
    result = _run("budget_router", {"complexity": 3, "risk": 2, "urgency": 1})
    assert result["status"] == "ok"
    for key in ("tier", "model", "rationale", "escalation_level"):
        assert key in result["outputs"], f"missing key: {key}"


def test_budget_router_empty_inputs_use_defaults() -> None:
    result = _run("budget_router", {})
    assert result["status"] == "ok"
    assert isinstance(result["outputs"]["escalation_level"], int)


# ---------------------------------------------------------------------------
# plan_lint — promoted to native in Phase 14
# ---------------------------------------------------------------------------

def test_plan_lint_is_native() -> None:
    assert _is_native("plan_lint")


def test_plan_lint_requires_input() -> None:
    result = _run("plan_lint", {})
    assert result["status"] == "fail"
    assert any("path" in e or "text" in e for e in result["errors"])


def test_plan_lint_output_keys_on_inline_text() -> None:
    plan_text = (
        "# Plan\n\n"
        "## Definition of Done\n\n"
        "- [ ] Task one done\n\n"
        "## N1 — Task\n\nDo the thing.\n\n"
        "## Acceptance Criteria\n\n"
        "- Passes tests\n\n"
        "## Files Changed\n\n"
        "| File | Change |\n"
        "|------|--------|\n"
        "| foo.py | Added |\n"
    )
    result = _run("plan_lint", {"text": plan_text})
    assert result["status"] == "ok"
    assert "pass" in result["outputs"]
    assert "errors" in result["outputs"]


def test_plan_lint_detects_missing_sections() -> None:
    result = _run("plan_lint", {"text": "# Just a title\n\nSome content."})
    assert result["status"] == "fail"
    assert len(result["outputs"]["errors"]) > 0
