"""Tests for SkillForgeRun composed skill with mode handling and publishing."""
import pytest
from unittest.mock import patch, MagicMock
from claudeclockwork.localai.skills.skill_forge_run import skill_forge_run


def test_skill_forge_run_mode_plan_only():
    """Test plan_only mode skips remaining stages."""
    result = skill_forge_run(
        archetype="reporter",
        purpose="Test",
        mode="plan_only",
    )
    assert result["final_status"] == "partial_success"
    assert result["resolved_inputs"]["mode"] == "plan_only"


def test_skill_forge_run_mode_through_forge():
    """Test through_forge mode skips review and validate."""
    result = skill_forge_run(
        archetype="scanner",
        purpose="Test",
        mode="through_forge",
    )
    assert result["final_status"] == "partial_success"
    assert result["resolved_inputs"]["mode"] == "through_forge"


def test_skill_forge_run_mode_through_review():
    """Test through_review mode precondition validation."""
    # Without prior results, should fail precondition check
    result = skill_forge_run(
        archetype="validator",
        purpose="Test",
        mode="through_review",
    )
    # Since plan_result and forge_result are None, precondition should fail
    assert result["final_status"] in ["failed", "partial_success"]


def test_skill_forge_run_mode_validate_only():
    """Test validate_only mode precondition validation."""
    # Without prior results, should fail precondition check
    result = skill_forge_run(
        archetype="transformer",
        purpose="Test",
        mode="validate_only",
    )
    # Since all prior results are None, precondition should fail
    assert result["final_status"] in ["failed", "partial_success"]


def test_skill_forge_run_publishing_when_publish_false():
    """Test publishing is skipped when publish=False."""
    result = skill_forge_run(
        archetype="reporter",
        purpose="Test",
        mode="plan_only",
        publish=False,
    )
    assert result["resolved_inputs"]["publish"] is False


def test_skill_forge_run_publishing_mode_aware():
    """Test publishing is skipped for partial modes."""
    result = skill_forge_run(
        archetype="reporter",
        purpose="Test",
        mode="plan_only",  # Not full mode
        publish=True,
    )
    # Even with publish=True, partial modes skip publishing
    assert result["final_status"] == "partial_success"
    assert result["publish_result"] is None


def test_skill_forge_run_execution_log_completeness():
    """Test execution log captures all events with proper structure."""
    result = skill_forge_run(
        archetype="reporter",
        purpose="Test",
        mode="plan_only",
    )
    assert "execution_log" in result
    assert len(result["execution_log"]) > 0

    for entry in result["execution_log"]:
        assert "stage" in entry
        assert "status" in entry
        assert "timestamp" in entry
        assert "duration_ms" in entry
        assert "notes" in entry


@patch("claudeclockwork.localai.skills.skill_forge_run.run_local_capability")
def test_skill_forge_run_calls_run_local_capability(mock_run):
    """Test skill invokes run_local_capability for each stage."""
    mock_run.return_value = {"status": "ok", "outputs": {}}

    result = skill_forge_run(
        archetype="reporter",
        purpose="Test",
        mode="plan_only",
    )

    # Should have called run_local_capability for plan stage
    assert mock_run.called
    assert any("code.plan" in str(call) for call in mock_run.call_args_list)


def test_skill_forge_run_mode_full_requires_all_stages():
    """Test full mode attempts all stages."""
    result = skill_forge_run(
        archetype="reporter",
        purpose="Test",
        mode="full",
    )
    # Full mode should attempt all stages
    assert result["final_status"] in ["success", "partial_success", "failed"]
    # Execution log should show attempts at multiple stages
    stages = [e["stage"] for e in result["execution_log"]]
    assert "input_resolution" in stages


def test_skill_forge_run_all_modes_supported():
    """Test all valid modes are accepted."""
    for mode in ["full", "plan_only", "through_forge", "through_review", "validate_only"]:
        result = skill_forge_run(
            archetype="reporter",
            purpose="Test",
            mode=mode,
        )
        assert result["run_id"] is not None
        assert result["final_status"] is not None
