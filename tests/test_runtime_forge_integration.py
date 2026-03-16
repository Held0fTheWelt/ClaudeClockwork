"""Integration tests for forge capabilities in the LocalAI runtime."""
import pytest
from claudeclockwork.localai import run_local_capability


class TestCodePlanCapability:
    """Test code.plan capability via runtime dispatch."""

    def test_code_plan_is_available(self):
        """Regression test: code.plan capability should be available."""
        result = run_local_capability("code.plan", {
            "task_id": "integration_test_001",
            "archetype": "reporter",
            "purpose": "Generate documentation",
            "constraints": {}
        })

        # REGRESSION: Should NOT return unknown_capability
        assert result["status"] != "unknown_capability"
        assert result["capability"] == "code.plan"

    def test_code_plan_returns_contract_shaped_result(self):
        """Test code.plan returns properly structured result."""
        result = run_local_capability("code.plan", {
            "task_id": "test",
            "archetype": "validator",
            "purpose": "Validate data",
            "constraints": {}
        })

        # Verify contract shape
        assert "status" in result
        assert "capability" in result
        assert "inputs" in result
        assert "outputs" in result
        assert "metrics" in result
        assert "errors" in result

    def test_code_plan_all_archetypes(self):
        """Test code.plan works with all valid archetypes."""
        archetypes = ["scanner", "validator", "reporter", "transformer", "registry_helper"]

        for archetype in archetypes:
            result = run_local_capability("code.plan", {
                "task_id": f"test_{archetype}",
                "archetype": archetype,
                "purpose": f"Test {archetype}",
                "constraints": {}
            })

            assert result["status"] != "unknown_capability"
            assert result["capability"] == "code.plan"


class TestCodeForgeCapability:
    """Test code.forge capability via runtime dispatch."""

    def test_code_forge_is_available(self):
        """Regression test: code.forge capability should be available."""
        result = run_local_capability("code.forge", {
            "task_id": "test",
            "plan": {},
            "allowed_write_roots": ["src"]
        })

        # REGRESSION: Should NOT return unknown_capability
        assert result["status"] != "unknown_capability"
        assert result["capability"] == "code.forge"

    def test_code_forge_returns_contract_shaped_result(self):
        """Test code.forge returns properly structured result."""
        result = run_local_capability("code.forge", {
            "task_id": "test",
            "plan": {},
            "allowed_write_roots": ["generated"]
        })

        # Verify contract shape
        assert "status" in result
        assert "capability" in result
        assert "inputs" in result
        assert "outputs" in result
        assert "metrics" in result
        assert "errors" in result


class TestCodeReviewCapability:
    """Test code.review capability via runtime dispatch."""

    def test_code_review_is_available(self):
        """Regression test: code.review capability should be available."""
        result = run_local_capability("code.review", {
            "task_id": "test",
            "forge_output": {}
        })

        # REGRESSION: Should NOT return unknown_capability
        assert result["status"] != "unknown_capability"
        assert result["capability"] == "code.review"

    def test_code_review_returns_contract_shaped_result(self):
        """Test code.review returns properly structured result."""
        result = run_local_capability("code.review", {
            "task_id": "test",
            "forge_output": {}
        })

        # Verify contract shape
        assert "status" in result
        assert "capability" in result
        assert "inputs" in result
        assert "outputs" in result
        assert "metrics" in result
        assert "errors" in result


class TestCodeValidateCapability:
    """Test code.validate capability via runtime dispatch."""

    def test_code_validate_is_available(self):
        """Regression test: code.validate capability should be available."""
        result = run_local_capability("code.validate", {
            "task_id": "test",
            "forge_output": {}
        })

        # REGRESSION: Should NOT return unknown_capability
        assert result["status"] != "unknown_capability"
        assert result["capability"] == "code.validate"

    def test_code_validate_returns_contract_shaped_result(self):
        """Test code.validate returns properly structured result."""
        result = run_local_capability("code.validate", {
            "task_id": "test",
            "forge_output": {}
        })

        # Verify contract shape
        assert "status" in result
        assert "capability" in result
        assert "inputs" in result
        assert "outputs" in result
        assert "metrics" in result
        assert "errors" in result


class TestRegressionAllCapabilitiesAvailable:
    """Regression tests for all capabilities."""

    def test_all_code_capabilities_available(self):
        """Test that all four code.* capabilities are available in runtime."""
        capabilities = ["code.plan", "code.forge", "code.review", "code.validate"]
        test_inputs = {
            "code.plan": {
                "task_id": "test",
                "archetype": "reporter",
                "purpose": "Test",
                "constraints": {}
            },
            "code.forge": {
                "task_id": "test",
                "plan": {},
                "allowed_write_roots": []
            },
            "code.review": {
                "task_id": "test",
                "forge_output": {}
            },
            "code.validate": {
                "task_id": "test",
                "forge_output": {}
            }
        }

        for capability in capabilities:
            result = run_local_capability(capability, test_inputs[capability])
            # All should succeed in returning a result (contract-shaped or error)
            # None should return "unknown_capability"
            assert "status" in result
            assert "capability" in result
            assert result["capability"] == capability
            assert result["status"] != "unknown_capability"

    def test_run_local_capability_no_longer_rejects_forge_capabilities(self):
        """Negative test: Verify forge capabilities are NOT rejected."""
        for capability in ["code.plan", "code.forge", "code.review", "code.validate"]:
            result = run_local_capability(capability, {"task_id": "test"})
            # Should not return unknown_capability error
            assert result.get("status") != "unknown_capability"
            assert "error" not in result or "unknown" not in str(result.get("error", "")).lower()
