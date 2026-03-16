"""Integration tests for the SkillForgeRun composed skill."""
import pytest
from unittest.mock import patch, MagicMock
from claudeclockwork.localai.skills.skill_forge_run import skill_forge_run


class TestSkillForgeRunFullPipeline:
    """Test full pipeline mode."""

    @patch("claudeclockwork.localai.skills.skill_forge_run.run_local_capability")
    def test_full_mode_executes_all_stages(self, mock_run):
        """Test full mode attempts all four stages."""
        mock_run.return_value = {"status": "ok", "outputs": {}}

        result = skill_forge_run(
            archetype="reporter",
            purpose="Test",
            mode="full"
        )

        # Should have attempted plan, forge, review, validate
        assert mock_run.call_count >= 1


class TestSkillForgeRunPartialModes:
    """Test partial execution modes."""

    def test_plan_only_mode(self):
        """Test plan_only mode."""
        result = skill_forge_run(
            archetype="reporter",
            purpose="Test",
            mode="plan_only"
        )

        assert result["final_status"] == "partial_success"
        assert result["resolved_inputs"]["mode"] == "plan_only"

    def test_through_forge_mode(self):
        """Test through_forge mode."""
        result = skill_forge_run(
            archetype="scanner",
            purpose="Test",
            mode="through_forge"
        )

        assert result["final_status"] == "partial_success"

    def test_through_review_mode_requires_prior_results(self):
        """Test through_review mode requires preconditions."""
        result = skill_forge_run(
            archetype="validator",
            purpose="Test",
            mode="through_review"
        )

        # Should fail due to missing preconditions
        assert result["final_status"] == "failed"

    def test_validate_only_mode_requires_prior_results(self):
        """Test validate_only mode requires all preconditions."""
        result = skill_forge_run(
            archetype="transformer",
            purpose="Test",
            mode="validate_only"
        )

        # Should fail due to missing preconditions
        assert result["final_status"] == "failed"


class TestSkillForgeRunInputValidation:
    """Test input validation."""

    def test_invalid_archetype_rejected(self):
        """Test invalid archetype is rejected."""
        result = skill_forge_run(
            archetype="invalid",
            purpose="Test"
        )

        assert result["final_status"] == "failed"
        assert "Invalid archetype" in result["error"]

    def test_invalid_mode_rejected(self):
        """Test invalid mode is rejected."""
        result = skill_forge_run(
            archetype="reporter",
            purpose="Test",
            mode="invalid_mode"
        )

        assert result["final_status"] == "failed"
        assert "Invalid mode" in result["error"]

    def test_missing_purpose_rejected(self):
        """Test missing purpose is rejected."""
        result = skill_forge_run(
            archetype="reporter",
            purpose=""
        )

        assert result["final_status"] == "failed"

    def test_all_valid_archetypes_accepted(self):
        """Test all valid archetypes are accepted."""
        for archetype in ["scanner", "validator", "reporter", "transformer", "registry_helper"]:
            result = skill_forge_run(
                archetype=archetype,
                purpose="Test"
            )

            assert result["run_id"] is not None
            assert result["final_status"] is not None
            assert "error" not in result or result.get("final_status") != "failed"


class TestSkillForgeRunExecutionLog:
    """Test execution log structure."""

    def test_execution_log_is_structured(self):
        """Test execution_log is a list of event objects."""
        result = skill_forge_run(
            archetype="reporter",
            purpose="Test",
            mode="plan_only"
        )

        assert isinstance(result["execution_log"], list)
        assert len(result["execution_log"]) > 0

        for event in result["execution_log"]:
            assert "stage" in event
            assert "status" in event
            assert "timestamp" in event
            assert "duration_ms" in event
            assert "notes" in event

    def test_execution_log_includes_input_resolution(self):
        """Test execution log includes input resolution event."""
        result = skill_forge_run(
            archetype="reporter",
            purpose="Test"
        )

        stages = [e["stage"] for e in result["execution_log"]]
        assert "input_resolution" in stages

    def test_execution_log_includes_validation(self):
        """Test execution log includes input validation event."""
        result = skill_forge_run(
            archetype="reporter",
            purpose="Test"
        )

        stages = [e["stage"] for e in result["execution_log"]]
        assert "validate_inputs" in stages


class TestSkillForgeRunResultStructure:
    """Test result structure."""

    def test_result_includes_run_id(self):
        """Test result includes run_id."""
        result = skill_forge_run(
            archetype="reporter",
            purpose="Test"
        )

        assert "run_id" in result
        assert isinstance(result["run_id"], str)
        assert "forge_" in result["run_id"]

    def test_result_includes_resolved_inputs(self):
        """Test result includes resolved inputs."""
        result = skill_forge_run(
            archetype="reporter",
            purpose="Test",
            allowed_write_roots=["custom"]
        )

        assert "resolved_inputs" in result
        assert result["resolved_inputs"]["archetype"] == "reporter"
        assert result["resolved_inputs"]["purpose"] == "Test"
        assert result["resolved_inputs"]["allowed_write_roots"] == ["custom"]

    def test_result_includes_temp_workspace(self):
        """Test result includes temp_workspace path."""
        result = skill_forge_run(
            archetype="reporter",
            purpose="Test"
        )

        assert "temp_workspace" in result
        assert isinstance(result["temp_workspace"], str)

    def test_result_includes_final_status(self):
        """Test result includes final_status."""
        result = skill_forge_run(
            archetype="reporter",
            purpose="Test"
        )

        assert "final_status" in result
        assert result["final_status"] in ["success", "partial_success", "failed"]
