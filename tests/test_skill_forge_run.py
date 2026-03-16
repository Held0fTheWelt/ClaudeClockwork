"""Tests for SkillForgeRun composed skill."""
import pytest
from claudeclockwork.localai.skills.skill_forge_run import skill_forge_run


def test_skill_forge_run_instantiation():
    """Test skill_forge_run can be invoked."""
    result = skill_forge_run(
        archetype="reporter",
        purpose="Generate documentation",
    )
    assert result is not None
    assert "run_id" in result
    assert "resolved_inputs" in result


def test_skill_forge_run_invalid_archetype():
    """Test skill_forge_run rejects invalid archetype."""
    result = skill_forge_run(
        archetype="invalid_archetype",
        purpose="Test",
    )
    assert result["final_status"] == "failed"
    assert "Invalid archetype" in result["error"]


def test_skill_forge_run_invalid_mode():
    """Test skill_forge_run rejects invalid mode."""
    result = skill_forge_run(
        archetype="reporter",
        purpose="Test",
        mode="invalid_mode",
    )
    assert result["final_status"] == "failed"
    assert "Invalid mode" in result["error"]


def test_skill_forge_run_missing_purpose():
    """Test skill_forge_run rejects missing purpose."""
    result = skill_forge_run(
        archetype="reporter",
        purpose="",
    )
    assert result["final_status"] == "failed"
    assert "purpose is required" in result["error"]


def test_skill_forge_run_valid_inputs_all_archetypes():
    """Test skill_forge_run accepts all valid archetypes."""
    for archetype in ["scanner", "validator", "reporter", "transformer", "registry_helper"]:
        result = skill_forge_run(
            archetype=archetype,
            purpose=f"Test {archetype}",
        )
        assert result["final_status"] in ["partial_success", "success"]
        assert result["resolved_inputs"]["archetype"] == archetype


def test_skill_forge_run_default_inputs():
    """Test skill_forge_run resolves default inputs correctly."""
    result = skill_forge_run(
        archetype="reporter",
        purpose="Test",
    )
    assert result["resolved_inputs"]["allowed_write_roots"] == ["docs", "src", "generated"]
    assert "target_root" in result["resolved_inputs"]
    assert "report_file" in result["resolved_inputs"]
    assert result["resolved_inputs"]["mode"] == "full"
    assert result["resolved_inputs"]["publish"] is True


def test_skill_forge_run_custom_inputs():
    """Test skill_forge_run respects custom inputs."""
    result = skill_forge_run(
        archetype="validator",
        purpose="Test",
        allowed_write_roots=["/tmp/test"],
        target_root="/tmp/target",
        report_file="/tmp/report.json",
        mode="plan_only",
        publish=False,
    )
    assert result["resolved_inputs"]["allowed_write_roots"] == ["/tmp/test"]
    assert result["resolved_inputs"]["target_root"] == "/tmp/target"
    assert result["resolved_inputs"]["report_file"] == "/tmp/report.json"
    assert result["resolved_inputs"]["mode"] == "plan_only"
    assert result["resolved_inputs"]["publish"] is False


def test_skill_forge_run_execution_log_structure():
    """Test skill_forge_run returns structured execution log."""
    result = skill_forge_run(
        archetype="reporter",
        purpose="Test",
    )
    assert "execution_log" in result
    assert isinstance(result["execution_log"], list)
    for entry in result["execution_log"]:
        assert "stage" in entry
        assert "status" in entry
        assert "timestamp" in entry
        assert "duration_ms" in entry
        assert "notes" in entry
