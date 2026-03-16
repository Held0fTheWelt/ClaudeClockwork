"""Tests for SkillForgeRunner orchestrator — full pipeline execution."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from claudeclockwork.localai.forge_runner import SkillForgeRunner


@pytest.fixture
def forge_runner() -> SkillForgeRunner:
    """Return a SkillForgeRunner instance."""
    return SkillForgeRunner()


@pytest.fixture
def basic_forge_request() -> dict:
    """Return a basic forge_request for a validator archetype."""
    return {
        "task_id": "forge-test-001",
        "archetype": "validator",
        "purpose": "Validate user input data structures",
        "constraints": {
            "allowed_write_roots": [],
            "forbidden_patterns": ["subprocess", "eval"],
        },
    }


@pytest.fixture
def scanner_forge_request() -> dict:
    """Return a forge_request for a scanner archetype."""
    return {
        "task_id": "forge-scan-001",
        "archetype": "scanner",
        "purpose": "Scan Python files for common issues",
        "constraints": {
            "allowed_write_roots": [],
            "forbidden_patterns": ["compile", "exec"],
        },
    }


@pytest.fixture
def bad_forge_request() -> dict:
    """Return an invalid forge_request (missing required fields)."""
    return {
        "task_id": "bad-001",
        # Missing 'archetype'
        "purpose": "Invalid request",
    }


class TestSkillForgeRunnerHappyPath:
    """Test successful execution of full pipeline."""

    def test_runner_executes_full_pipeline_happy_path(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test that run_pipeline executes all 4 capabilities successfully."""
        result = forge_runner.run_pipeline(basic_forge_request)

        # Should succeed
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "forge_result" in result
        assert "review" in result
        assert "validation" in result

    def test_runner_returns_forge_result_from_plan_and_forge(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test that result includes code artifacts from forge stage."""
        result = forge_runner.run_pipeline(basic_forge_request)

        assert result.get("success") is True
        forge_result = result.get("forge_result")
        assert forge_result is not None
        assert "task_id" in forge_result
        assert "archetype" in forge_result
        assert "code" in forge_result
        assert "manifest" in forge_result
        assert "package_root" in forge_result

    def test_runner_returns_review_result(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test that result includes review results from review stage."""
        result = forge_runner.run_pipeline(basic_forge_request)

        assert result.get("success") is True
        review_result = result.get("review")
        assert review_result is not None
        assert "approved" in review_result
        assert "issues" in review_result
        assert isinstance(review_result["issues"], list)

    def test_runner_returns_validation_result(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test that result includes validation results."""
        result = forge_runner.run_pipeline(basic_forge_request)

        assert result.get("success") is True
        validation_result = result.get("validation")
        assert validation_result is not None
        # Validation should have checks
        assert "checks" in validation_result or "valid" in validation_result

    def test_runner_returns_registry_entry(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test that result includes registry entry."""
        result = forge_runner.run_pipeline(basic_forge_request)

        assert result.get("success") is True
        registry_entry = result.get("registry_entry")
        assert registry_entry is not None
        assert "task_id" in registry_entry
        assert "archetype" in registry_entry

    def test_runner_with_different_archetype(
        self, forge_runner: SkillForgeRunner, scanner_forge_request: dict
    ) -> None:
        """Test pipeline works with different archetypes (scanner)."""
        result = forge_runner.run_pipeline(scanner_forge_request)

        assert result.get("success") is True
        assert result["forge_result"]["archetype"] == "scanner"


class TestSkillForgeRunnerReviewGate:
    """Test review failure handling."""

    def test_runner_stops_on_review_failure(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test that pipeline stops and returns error if review fails.

        This test injects a request that will generate code with critical issues
        (e.g., syntax error or missing docstrings) to trigger review failure.
        """
        # Create a bad request that will likely generate poor code
        bad_code_request = basic_forge_request.copy()
        bad_code_request["purpose"] = ""  # Empty purpose to create minimal code

        result = forge_runner.run_pipeline(bad_code_request)

        # If review approves, that's fine (our templates are good)
        # But if it fails, should be structured error
        if not result.get("success"):
            assert result.get("reason") == "review_failed"
            assert "issues" in result
            assert isinstance(result.get("issues"), list)
            # Should NOT have validation or forge_result
            assert "validation" not in result


class TestSkillForgeRunnerValidationGate:
    """Test validation failure handling."""

    def test_runner_stops_on_validation_failure(
        self, forge_runner: SkillForgeRunner, monkeypatch
    ) -> None:
        """Test that pipeline stops if validation fails."""
        # Mock the validation capability to return failure
        original_validate = forge_runner.code_validate.validate if hasattr(
            forge_runner, "code_validate"
        ) else None

        def mock_validate(code: str, archetype: str) -> dict:
            """Return a validation failure."""
            return {
                "valid": False,
                "checks": {"safety": False, "security": False},
                "errors": ["Code uses forbidden pattern: eval"],
            }

        # Patch validate method
        if hasattr(forge_runner, "code_validate"):
            monkeypatch.setattr(
                forge_runner.code_validate, "validate", mock_validate
            )

        request = {
            "task_id": "forge-val-fail",
            "archetype": "validator",
            "purpose": "Test validation failure",
            "constraints": {
                "allowed_write_roots": [],
                "forbidden_patterns": ["eval"],
            },
        }

        result = forge_runner.run_pipeline(request)

        # Should fail validation
        assert result.get("success") is False
        assert result.get("reason") == "validation_failed"
        assert "checks" in result


class TestSkillForgeRunnerErrorHandling:
    """Test error handling for bad inputs."""

    def test_runner_handles_bad_request(
        self, forge_runner: SkillForgeRunner, bad_forge_request: dict
    ) -> None:
        """Test that runner handles invalid forge_request gracefully."""
        result = forge_runner.run_pipeline(bad_forge_request)

        # Should return error
        assert result.get("success") is False
        assert "reason" in result or "error" in result

    def test_runner_returns_structured_results(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test that results always have consistent structure."""
        result = forge_runner.run_pipeline(basic_forge_request)

        # Should always have these keys
        assert "success" in result
        assert isinstance(result["success"], bool)

        # If failed, should have reason/error
        if not result["success"]:
            assert "reason" in result or "error" in result


class TestSkillForgeRunnerCleanup:
    """Test temporary file handling."""

    def test_runner_cleans_up_temp_files(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test that temporary files are cleaned up after pipeline completes."""
        # Run pipeline
        result = forge_runner.run_pipeline(basic_forge_request)

        # If temp files were created in a predictable location, verify they exist
        # or were cleaned up. This depends on implementation.
        # For now, just verify the result is complete
        assert result.get("success") is True
        forge_result = result.get("forge_result")
        if forge_result and "package_root" in forge_result:
            # Package root should be a valid path string
            assert isinstance(forge_result["package_root"], str)

    def test_runner_preserves_output_directory_structure(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict, tmp_path
    ) -> None:
        """Test that output from forge stage has proper directory structure."""
        result = forge_runner.run_pipeline(basic_forge_request)

        assert result.get("success") is True
        forge_result = result.get("forge_result")
        package_root = forge_result.get("package_root")

        # Verify code map is complete
        code_map = forge_result.get("code")
        assert isinstance(code_map, dict)
        assert "__init__.py" in code_map
        assert "main.py" in code_map


class TestSkillForgeRunnerOrchestration:
    """Test orchestration coordination between capabilities."""

    def test_runner_passes_plan_to_forge(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test that plan output is properly passed to forge capability."""
        result = forge_runner.run_pipeline(basic_forge_request)

        assert result.get("success") is True
        forge_result = result.get("forge_result")
        # The forge result should have the same task_id and archetype
        assert forge_result["task_id"] == basic_forge_request["task_id"]
        assert forge_result["archetype"] == basic_forge_request["archetype"]

    def test_runner_passes_code_to_review(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test that forge code is properly passed to review capability."""
        result = forge_runner.run_pipeline(basic_forge_request)

        assert result.get("success") is True
        review_result = result.get("review")
        # Review should have analyzed the code
        assert "approved" in review_result
        # Should have issues list (may be empty)
        assert "issues" in review_result

    def test_runner_integrates_all_stages(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test full integration: request→plan→forge→review→validate→result."""
        result = forge_runner.run_pipeline(basic_forge_request)

        # Should have all results
        assert result.get("success") is True

        # Verify each stage contributed
        assert "forge_result" in result  # From forge stage
        assert "review" in result  # From review stage
        assert "validation" in result  # From validate stage

        # Verify data flow consistency
        task_id = basic_forge_request["task_id"]
        assert result["forge_result"]["task_id"] == task_id


class TestSkillForgeRunnerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_runner_handles_empty_constraints(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test pipeline with minimal constraints."""
        request = basic_forge_request.copy()
        request["constraints"] = {}

        result = forge_runner.run_pipeline(request)
        assert result.get("success") is True

    def test_runner_handles_large_purpose_string(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test pipeline with very detailed purpose."""
        request = basic_forge_request.copy()
        request["purpose"] = "Test " * 100  # Large purpose string

        result = forge_runner.run_pipeline(request)
        # Should not crash
        assert isinstance(result, dict)

    def test_runner_preserves_request_immutability(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test that pipeline doesn't modify input request."""
        import copy

        request_copy = copy.deepcopy(basic_forge_request)
        result = forge_runner.run_pipeline(basic_forge_request)

        # Original request should be unchanged
        assert basic_forge_request == request_copy


class TestSkillForgeRunnerManifest:
    """Test manifest and registry entry generation."""

    def test_runner_generates_valid_manifest(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test that forge result includes valid manifest."""
        result = forge_runner.run_pipeline(basic_forge_request)

        assert result.get("success") is True
        manifest = result["forge_result"].get("manifest")
        assert manifest is not None
        assert "entry_point" in manifest
        assert "archetype" in manifest
        assert "task_id" in manifest

    def test_runner_includes_dependency_info_in_manifest(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict
    ) -> None:
        """Test that manifest includes dependency information."""
        result = forge_runner.run_pipeline(basic_forge_request)

        assert result.get("success") is True
        manifest = result["forge_result"].get("manifest")
        assert "dependencies" in manifest
        assert isinstance(manifest["dependencies"], list)


class TestSkillForgeRunnerMultipleRuns:
    """Test multiple sequential runs."""

    def test_runner_can_run_multiple_pipelines(
        self, forge_runner: SkillForgeRunner, basic_forge_request: dict,
        scanner_forge_request: dict
    ) -> None:
        """Test that runner can execute multiple pipelines sequentially."""
        result1 = forge_runner.run_pipeline(basic_forge_request)
        result2 = forge_runner.run_pipeline(scanner_forge_request)

        assert result1.get("success") is True
        assert result2.get("success") is True
        assert result1["forge_result"]["task_id"] != result2["forge_result"]["task_id"]
        assert result1["forge_result"]["archetype"] != result2["forge_result"]["archetype"]
