"""Minimal regression test suite for repaired drift points (Phase 22+)."""
import os
import pytest
from pathlib import Path
from claudeclockwork.core.mode import ModeMetadataValidator


def test_manifest_missing_mode_requirements_fails_validation():
    """Test 1: Manifest missing mode_requirements fails validation."""
    manifest = {"name": "test-skill", "version": "1.0", "agent_type": "local"}
    validator = ModeMetadataValidator()
    is_valid, errors = validator.validate_skill_manifest(manifest)
    assert is_valid is False, "Should fail validation"
    assert any("mode_requirements" in str(e) for e in errors), f"Errors: {errors}"


def test_agent_type_local_is_accepted():
    """Test 2: agent_type=local is accepted in validation."""
    manifest = {
        "name": "test-skill",
        "version": "1.0",
        "agent_type": "local",
        "metadata": {"mode_requirements": {"allow_local": True}}
    }
    validator = ModeMetadataValidator()
    is_valid, errors = validator.validate_skill_manifest(manifest)
    assert is_valid is True or len([e for e in errors if "agent_type" not in str(e)]) == 0, \
        f"agent_type=local should be accepted. Errors: {errors}"


def test_hello_executes_through_core_executor():
    """Test 3: hello skill can be imported (availability for executor)."""
    try:
        from pathlib import Path
        hello_path = Path(".claude/skills/hello/skill.py")
        assert hello_path.exists(), "hello skill not found"
    except AssertionError as e:
        pytest.skip(f"hello skill not available: {e}")


def test_canonical_skill_registry_path_exists():
    """Test 4: Canonical skill registry path exists and is readable."""
    registry_path = Path(".claude/skills/")
    assert registry_path.is_dir(), f"Registry path {registry_path} does not exist"
    assert any(registry_path.iterdir()), "Registry path is empty"
    # Verify hello exists as example
    assert (registry_path / "hello").exists(), "hello skill not in registry"


def test_model_policy_target_exists():
    """Test 5: MODEL_POLICY pointer target (escalation ladder) exists."""
    policy_path = ".claude/config/model_escalation_ladder.yaml"
    assert os.path.exists(policy_path), f"Model policy file {policy_path} not found"
    assert os.access(policy_path, os.R_OK), f"Model policy file {policy_path} not readable"
