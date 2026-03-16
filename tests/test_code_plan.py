"""Tests for code.plan capability — forge_request to forge_plan conversion."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from claudeclockwork.localai.capabilities.code_plan import CodePlanCapability


@pytest.fixture
def code_plan_capability() -> CodePlanCapability:
    """Return a CodePlanCapability instance."""
    return CodePlanCapability()


@pytest.fixture
def basic_forge_request() -> dict:
    """Return a basic forge_request for a scanner archetype."""
    return {
        "task_id": "forge-001",
        "archetype": "scanner",
        "purpose": "Scan Python files for security vulnerabilities",
        "constraints": {
            "allowed_write_roots": [],
            "forbidden_patterns": ["subprocess.call", "compile"],
        },
    }


class TestCodePlanBasic:
    """Test basic happy path for code plan generation."""

    def test_plan_accepts_forge_request_schema(
        self, code_plan_capability: CodePlanCapability, basic_forge_request: dict
    ) -> None:
        """Test that plan() accepts a valid forge_request and returns a forge_plan."""
        result = code_plan_capability.plan(basic_forge_request)
        assert isinstance(result, dict), "Result should be a dict"
        assert "task_id" in result, "Result should contain task_id"
        assert result["task_id"] == "forge-001"

    def test_plan_matches_forge_plan_schema(
        self, code_plan_capability: CodePlanCapability, basic_forge_request: dict
    ) -> None:
        """Test that plan() output matches forge_plan schema structure."""
        result = code_plan_capability.plan(basic_forge_request)

        # Check required fields
        required_fields = [
            "task_id",
            "archetype",
            "module_structure",
            "key_functions",
            "dependencies",
            "safety_notes",
        ]
        for field in required_fields:
            assert (
                field in result
            ), f"Result should contain required field '{field}'"

        # Validate module_structure
        assert isinstance(
            result["module_structure"], dict
        ), "module_structure should be a dict"
        assert "modules" in result["module_structure"]
        assert isinstance(
            result["module_structure"]["modules"], list
        ), "modules should be a list"

        # Validate key_functions
        assert isinstance(
            result["key_functions"], list
        ), "key_functions should be a list"
        for func in result["key_functions"]:
            assert "name" in func
            assert "signature" in func
            assert "purpose" in func

        # Validate dependencies
        assert isinstance(
            result["dependencies"], list
        ), "dependencies should be a list"
        for dep in result["dependencies"]:
            assert isinstance(
                dep, dict
            ), "Each dependency should be a dict or str"
            if isinstance(dep, dict):
                assert "name" in dep

        # Validate safety_notes
        assert isinstance(
            result["safety_notes"], dict
        ), "safety_notes should be a dict"

    def test_plan_includes_safety_notes(
        self, code_plan_capability: CodePlanCapability, basic_forge_request: dict
    ) -> None:
        """Test that safety_notes document write restrictions and forbidden patterns."""
        result = code_plan_capability.plan(basic_forge_request)
        safety_notes = result["safety_notes"]

        # Should document the archetype
        assert "archetype" in safety_notes or any(
            "scanner" in str(v).lower() for v in safety_notes.values()
        ), "safety_notes should mention archetype"

        # Should document write restrictions
        assert (
            "write_restrictions" in safety_notes
            or "allowed_write_roots" in safety_notes
            or any("write" in str(k).lower() for k in safety_notes.keys())
        ), "safety_notes should document write restrictions"

        # Should document forbidden patterns
        assert (
            "forbidden_patterns" in safety_notes
            or "no_operations" in safety_notes
            or any("forbidden" in str(k).lower() for k in safety_notes.keys())
        ), "safety_notes should document forbidden patterns"


class TestCodePlanArchetypes:
    """Test that module structure varies by archetype."""

    def test_plan_scanner_archetype(
        self, code_plan_capability: CodePlanCapability
    ) -> None:
        """Test module structure for scanner archetype."""
        request = {
            "task_id": "forge-scanner-001",
            "archetype": "scanner",
            "purpose": "Scan files for patterns",
            "constraints": {
                "allowed_write_roots": [],
                "forbidden_patterns": [],
            },
        }
        result = code_plan_capability.plan(request)

        assert result["archetype"] == "scanner"
        # Scanners should have a main scan() function
        func_names = [f["name"] for f in result["key_functions"]]
        assert "scan" in func_names, "Scanner should have scan() function"

        # Scanner typically needs pathlib for file operations
        dep_names = [d["name"] if isinstance(d, dict) else d for d in result["dependencies"]]
        assert "pathlib" in dep_names, "Scanner should have pathlib dependency"

    def test_plan_validator_archetype(
        self, code_plan_capability: CodePlanCapability
    ) -> None:
        """Test module structure for validator archetype."""
        request = {
            "task_id": "forge-validator-001",
            "archetype": "validator",
            "purpose": "Validate JSON schema compliance",
            "constraints": {
                "allowed_write_roots": [],
                "forbidden_patterns": [],
            },
        }
        result = code_plan_capability.plan(request)

        assert result["archetype"] == "validator"
        # Validators should have a validate() function
        func_names = [f["name"] for f in result["key_functions"]]
        assert "validate" in func_names, "Validator should have validate() function"

        # Validators should include schema module
        module_names = [m["name"] for m in result["module_structure"]["modules"]]
        assert (
            "schema.py" in module_names or any("schema" in m for m in module_names)
        ), "Validator should have schema module"

    def test_plan_reporter_archetype(
        self, code_plan_capability: CodePlanCapability
    ) -> None:
        """Test module structure for reporter archetype."""
        request = {
            "task_id": "forge-reporter-001",
            "archetype": "reporter",
            "purpose": "Generate reports from data",
            "constraints": {
                "allowed_write_roots": ["/tmp/reports"],
                "forbidden_patterns": [],
            },
        }
        result = code_plan_capability.plan(request)

        assert result["archetype"] == "reporter"
        # Reporters should have a report() function
        func_names = [f["name"] for f in result["key_functions"]]
        assert "report" in func_names, "Reporter should have report() function"

    def test_plan_transformer_archetype(
        self, code_plan_capability: CodePlanCapability
    ) -> None:
        """Test module structure for transformer archetype."""
        request = {
            "task_id": "forge-transformer-001",
            "archetype": "transformer",
            "purpose": "Transform data from one format to another",
            "constraints": {
                "allowed_write_roots": ["/output"],
                "forbidden_patterns": ["compile"],
            },
        }
        result = code_plan_capability.plan(request)

        assert result["archetype"] == "transformer"
        # Transformers should have a transform() function
        func_names = [f["name"] for f in result["key_functions"]]
        assert (
            "transform" in func_names
        ), "Transformer should have transform() function"

    def test_plan_registry_helper_archetype(
        self, code_plan_capability: CodePlanCapability
    ) -> None:
        """Test module structure for registry_helper archetype."""
        request = {
            "task_id": "forge-helper-001",
            "archetype": "registry_helper",
            "purpose": "Register and manage registry entries",
            "constraints": {
                "allowed_write_roots": ["/registry"],
                "forbidden_patterns": [],
            },
        }
        result = code_plan_capability.plan(request)

        assert result["archetype"] == "registry_helper"
        # Registry helpers should have a registry_op() function
        func_names = [f["name"] for f in result["key_functions"]]
        assert (
            "registry_op" in func_names
        ), "Registry helper should have registry_op() function"


class TestCodePlanSafety:
    """Test safety constraint handling."""

    def test_plan_safety_constraints_reflected(
        self, code_plan_capability: CodePlanCapability
    ) -> None:
        """Test that constraints are reflected in safety_notes."""
        request = {
            "task_id": "forge-constraint-001",
            "archetype": "scanner",
            "purpose": "Scan files",
            "constraints": {
                "allowed_write_roots": ["/allowed/path1", "/allowed/path2"],
                "forbidden_patterns": ["subprocess.call", "compile", "exec"],
            },
        }
        result = code_plan_capability.plan(request)
        safety_notes = result["safety_notes"]

        # Check that constraints are documented
        constraint_str = json.dumps(safety_notes)
        assert (
            "/allowed/path1" in constraint_str or "allowed_write_roots" in constraint_str
        ), "safety_notes should document allowed_write_roots"
        assert (
            "forbidden_patterns" in constraint_str
        ), "safety_notes should document forbidden_patterns"

    def test_plan_read_only_when_no_write_roots(
        self, code_plan_capability: CodePlanCapability
    ) -> None:
        """Test that safety_notes indicate read-only when no write roots allowed."""
        request = {
            "task_id": "forge-readonly-001",
            "archetype": "scanner",
            "purpose": "Scan files",
            "constraints": {
                "allowed_write_roots": [],
                "forbidden_patterns": [],
            },
        }
        result = code_plan_capability.plan(request)
        safety_notes = result["safety_notes"]

        # Should indicate read-only
        constraint_str = json.dumps(safety_notes).lower()
        assert (
            "read-only" in constraint_str
            or "no write" in constraint_str
            or "cannot write" in constraint_str
            or "write_restrictions" in safety_notes
        ), "safety_notes should indicate read-only restriction"

    def test_plan_base_dependencies_always_present(
        self, code_plan_capability: CodePlanCapability
    ) -> None:
        """Test that base dependencies (json, sys, typing) are always present."""
        request = {
            "task_id": "forge-deps-001",
            "archetype": "reporter",
            "purpose": "Generate reports",
            "constraints": {
                "allowed_write_roots": ["/reports"],
                "forbidden_patterns": [],
            },
        }
        result = code_plan_capability.plan(request)
        dep_names = [
            d["name"] if isinstance(d, dict) else d for d in result["dependencies"]
        ]

        # Base dependencies should always be present
        assert "json" in dep_names, "json should always be a dependency"
        assert "sys" in dep_names, "sys should always be a dependency"
        assert "typing" in dep_names, "typing should always be a dependency"
