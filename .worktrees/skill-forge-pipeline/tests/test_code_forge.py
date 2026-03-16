"""Tests for code.forge capability — forge_plan to executable code generation."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from claudeclockwork.localai.capabilities.code_forge import CodeForgeCapability


@pytest.fixture
def code_forge_capability() -> CodeForgeCapability:
    """Return a CodeForgeCapability instance."""
    return CodeForgeCapability()


@pytest.fixture
def basic_forge_plan() -> dict:
    """Return a basic forge_plan for a scanner archetype."""
    return {
        "task_id": "forge-001",
        "archetype": "scanner",
        "module_structure": {
            "root_package": "forge_scanner",
            "modules": [
                {"name": "__init__.py", "purpose": "Package initialization"},
                {"name": "main.py", "purpose": "Main scanner implementation"},
            ],
        },
        "key_functions": [
            {
                "name": "scan",
                "signature": "def scan(path: str) -> list[dict[str, Any]]",
                "purpose": "Scan files at path",
            }
        ],
        "dependencies": [
            {"name": "json", "purpose": "JSON serialization"},
            {"name": "sys", "purpose": "System operations"},
            {"name": "typing", "purpose": "Type hints"},
            {"name": "pathlib", "purpose": "Path operations"},
        ],
        "safety_notes": {
            "archetype": "scanner",
            "write_restrictions": "read-only",
        },
    }


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


@pytest.fixture
def temp_output_dir(tmp_path) -> str:
    """Return a temporary directory for code generation."""
    return str(tmp_path)


class TestCodeForgeBasic:
    """Test basic happy path for code forge generation."""

    def test_forge_generates_package_from_plan(
        self,
        code_forge_capability: CodeForgeCapability,
        basic_forge_plan: dict,
        basic_forge_request: dict,
        temp_output_dir: str,
    ) -> None:
        """Test that forge() generates a package from plan and request."""
        result = code_forge_capability.forge(
            basic_forge_plan, basic_forge_request, temp_output_dir
        )

        assert isinstance(result, dict), "Result should be a dict"
        assert "task_id" in result, "Result should contain task_id"
        assert result["task_id"] == "forge-001"
        assert "code" in result, "Result should contain code map"
        assert isinstance(result["code"], dict), "code should be a dict of files"

    def test_forge_generates_valid_python(
        self,
        code_forge_capability: CodeForgeCapability,
        basic_forge_plan: dict,
        basic_forge_request: dict,
        temp_output_dir: str,
    ) -> None:
        """Test that generated code is valid Python (can be parsed)."""
        result = code_forge_capability.forge(
            basic_forge_plan, basic_forge_request, temp_output_dir
        )

        code_map = result["code"]
        for file_path, source_code in code_map.items():
            # Skip schema files if they're not Python
            if file_path.endswith(".yaml") or file_path.endswith(".json"):
                continue

            # Try to parse as Python
            try:
                ast.parse(source_code)
            except SyntaxError as e:
                pytest.fail(
                    f"Generated code in {file_path} is not valid Python: {str(e)}"
                )

    def test_forge_respects_archetype_template(
        self,
        code_forge_capability: CodeForgeCapability,
        basic_forge_plan: dict,
        basic_forge_request: dict,
        temp_output_dir: str,
    ) -> None:
        """Test that forge uses the correct template for the archetype."""
        result = code_forge_capability.forge(
            basic_forge_plan, basic_forge_request, temp_output_dir
        )

        code_map = result["code"]
        main_py = code_map.get("main.py", "")

        # Scanner should have a scan() function
        assert "def scan(" in main_py, "Scanner template should have scan() function"
        assert (
            "json.load(sys.stdin)" in main_py
        ), "Scanner template should read JSON from stdin"

    def test_forge_includes_manifest(
        self,
        code_forge_capability: CodeForgeCapability,
        basic_forge_plan: dict,
        basic_forge_request: dict,
        temp_output_dir: str,
    ) -> None:
        """Test that forge generates manifest.json with required fields."""
        result = code_forge_capability.forge(
            basic_forge_plan, basic_forge_request, temp_output_dir
        )

        assert "manifest" in result, "Result should contain manifest"
        manifest = result["manifest"]

        required_fields = [
            "entry_point",
            "archetype",
            "purpose",
            "dependencies",
            "version",
        ]
        for field in required_fields:
            assert field in manifest, f"Manifest should contain '{field}'"

        assert manifest["archetype"] == "scanner"
        assert manifest["version"] == "0.1.0"


class TestCodeForgeArchetypeTemplates:
    """Test that code generation respects archetype-specific templates."""

    def test_forge_scanner_has_scan_function(
        self,
        code_forge_capability: CodeForgeCapability,
        temp_output_dir: str,
    ) -> None:
        """Test that scanner archetype generates scan() function."""
        plan = {
            "task_id": "forge-scanner-001",
            "archetype": "scanner",
            "module_structure": {
                "root_package": "forge_scanner",
                "modules": [
                    {"name": "__init__.py", "purpose": "Package initialization"},
                    {"name": "main.py", "purpose": "Main scanner implementation"},
                ],
            },
            "key_functions": [
                {
                    "name": "scan",
                    "signature": "def scan(path: str) -> list[dict[str, Any]]",
                    "purpose": "Scan files",
                }
            ],
            "dependencies": [
                {"name": "json", "purpose": "JSON serialization"},
                {"name": "pathlib", "purpose": "Path operations"},
            ],
            "safety_notes": {"archetype": "scanner"},
        }
        request = {
            "task_id": "forge-scanner-001",
            "archetype": "scanner",
            "purpose": "Scan files",
            "constraints": {},
        }

        result = code_forge_capability.forge(plan, request, temp_output_dir)
        main_py = result["code"]["main.py"]

        assert "def scan(" in main_py, "Should have scan() function"
        assert "NotImplementedError" in main_py or "..." in main_py

    def test_forge_validator_has_validate_function(
        self,
        code_forge_capability: CodeForgeCapability,
        temp_output_dir: str,
    ) -> None:
        """Test that validator archetype generates validate() function."""
        plan = {
            "task_id": "forge-validator-001",
            "archetype": "validator",
            "module_structure": {
                "root_package": "forge_validator",
                "modules": [
                    {"name": "__init__.py", "purpose": "Package initialization"},
                    {"name": "main.py", "purpose": "Main validator implementation"},
                    {"name": "schema.py", "purpose": "Schema definitions"},
                ],
            },
            "key_functions": [
                {
                    "name": "validate",
                    "signature": "def validate(data: dict[str, Any]) -> tuple[bool, list[str]]",
                    "purpose": "Validate input",
                }
            ],
            "dependencies": [
                {"name": "json", "purpose": "JSON serialization"},
            ],
            "safety_notes": {"archetype": "validator"},
        }
        request = {
            "task_id": "forge-validator-001",
            "archetype": "validator",
            "purpose": "Validate JSON",
            "constraints": {},
        }

        result = code_forge_capability.forge(plan, request, temp_output_dir)
        main_py = result["code"]["main.py"]

        assert "def validate(" in main_py, "Should have validate() function"
        assert "valid" in main_py.lower()

    def test_forge_reporter_has_report_function(
        self,
        code_forge_capability: CodeForgeCapability,
        temp_output_dir: str,
    ) -> None:
        """Test that reporter archetype generates report() function."""
        plan = {
            "task_id": "forge-reporter-001",
            "archetype": "reporter",
            "module_structure": {
                "root_package": "forge_reporter",
                "modules": [
                    {"name": "__init__.py", "purpose": "Package initialization"},
                    {"name": "main.py", "purpose": "Main reporter implementation"},
                ],
            },
            "key_functions": [
                {
                    "name": "report",
                    "signature": "def report(data: dict[str, Any]) -> str",
                    "purpose": "Generate report",
                }
            ],
            "dependencies": [
                {"name": "json", "purpose": "JSON serialization"},
            ],
            "safety_notes": {"archetype": "reporter"},
        }
        request = {
            "task_id": "forge-reporter-001",
            "archetype": "reporter",
            "purpose": "Generate reports",
            "constraints": {},
        }

        result = code_forge_capability.forge(plan, request, temp_output_dir)
        main_py = result["code"]["main.py"]

        assert "def report(" in main_py, "Should have report() function"

    def test_forge_transformer_has_transform_function(
        self,
        code_forge_capability: CodeForgeCapability,
        temp_output_dir: str,
    ) -> None:
        """Test that transformer archetype generates transform() function."""
        plan = {
            "task_id": "forge-transformer-001",
            "archetype": "transformer",
            "module_structure": {
                "root_package": "forge_transformer",
                "modules": [
                    {"name": "__init__.py", "purpose": "Package initialization"},
                    {"name": "main.py", "purpose": "Main transformer implementation"},
                ],
            },
            "key_functions": [
                {
                    "name": "transform",
                    "signature": "def transform(input_data: dict[str, Any]) -> dict[str, Any]",
                    "purpose": "Transform data",
                }
            ],
            "dependencies": [
                {"name": "json", "purpose": "JSON serialization"},
            ],
            "safety_notes": {"archetype": "transformer"},
        }
        request = {
            "task_id": "forge-transformer-001",
            "archetype": "transformer",
            "purpose": "Transform data",
            "constraints": {},
        }

        result = code_forge_capability.forge(plan, request, temp_output_dir)
        main_py = result["code"]["main.py"]

        assert "def transform(" in main_py, "Should have transform() function"

    def test_forge_registry_helper_has_registry_op_function(
        self,
        code_forge_capability: CodeForgeCapability,
        temp_output_dir: str,
    ) -> None:
        """Test that registry_helper archetype generates registry_op() function."""
        plan = {
            "task_id": "forge-helper-001",
            "archetype": "registry_helper",
            "module_structure": {
                "root_package": "forge_registry_helper",
                "modules": [
                    {"name": "__init__.py", "purpose": "Package initialization"},
                    {
                        "name": "main.py",
                        "purpose": "Main registry helper implementation",
                    },
                ],
            },
            "key_functions": [
                {
                    "name": "registry_op",
                    "signature": "def registry_op(operation: str, **kwargs) -> dict[str, Any]",
                    "purpose": "Registry operation",
                }
            ],
            "dependencies": [
                {"name": "json", "purpose": "JSON serialization"},
                {"name": "yaml", "purpose": "YAML parsing"},
            ],
            "safety_notes": {"archetype": "registry_helper"},
        }
        request = {
            "task_id": "forge-helper-001",
            "archetype": "registry_helper",
            "purpose": "Registry operations",
            "constraints": {},
        }

        result = code_forge_capability.forge(plan, request, temp_output_dir)
        main_py = result["code"]["main.py"]

        assert "def registry_op(" in main_py, "Should have registry_op() function"

    def test_forge_registry_helper_yaml_safety(
        self,
        code_forge_capability: CodeForgeCapability,
        temp_output_dir: str,
    ) -> None:
        """Test that registry_helper includes YAML safety comments."""
        plan = {
            "task_id": "forge-helper-yaml-001",
            "archetype": "registry_helper",
            "module_structure": {
                "root_package": "forge_registry_helper",
                "modules": [
                    {"name": "__init__.py", "purpose": "Package initialization"},
                    {
                        "name": "main.py",
                        "purpose": "Main registry helper implementation",
                    },
                ],
            },
            "key_functions": [
                {
                    "name": "registry_op",
                    "signature": "def registry_op(input_spec: Dict[str, Any]) -> Dict[str, Any]",
                    "purpose": "Registry operation",
                }
            ],
            "dependencies": [
                {"name": "json", "purpose": "JSON serialization"},
                {"name": "yaml", "purpose": "YAML parsing"},
            ],
            "safety_notes": {
                "archetype": "registry_helper",
                "security_concerns": [
                    "Only reads/writes YAML files in allowed_write_roots",
                    "Never executes arbitrary code",
                ],
            },
        }
        request = {
            "task_id": "forge-helper-yaml-001",
            "archetype": "registry_helper",
            "purpose": "Registry operations with YAML",
            "constraints": {},
        }

        result = code_forge_capability.forge(plan, request, temp_output_dir)
        main_py = result["code"]["main.py"]

        # Should have YAML import
        assert "yaml" in main_py.lower(), "Should import yaml for registry_helper"


class TestCodeForgeDependencies:
    """Test dependency handling in code generation."""

    def test_forge_dependencies_in_imports(
        self,
        code_forge_capability: CodeForgeCapability,
        temp_output_dir: str,
    ) -> None:
        """Test that plan dependencies appear in generated imports."""
        plan = {
            "task_id": "forge-deps-001",
            "archetype": "scanner",
            "module_structure": {
                "root_package": "forge_scanner",
                "modules": [
                    {"name": "__init__.py", "purpose": "Package initialization"},
                    {"name": "main.py", "purpose": "Main implementation"},
                ],
            },
            "key_functions": [
                {
                    "name": "scan",
                    "signature": "def scan(path: str) -> list[dict[str, Any]]",
                    "purpose": "Scan files",
                }
            ],
            "dependencies": [
                {"name": "json", "purpose": "JSON serialization"},
                {"name": "sys", "purpose": "System operations"},
                {"name": "pathlib", "purpose": "Path operations"},
                {"name": "typing", "purpose": "Type hints"},
            ],
            "safety_notes": {"archetype": "scanner"},
        }
        request = {
            "task_id": "forge-deps-001",
            "archetype": "scanner",
            "purpose": "Scan files",
            "constraints": {},
        }

        result = code_forge_capability.forge(plan, request, temp_output_dir)
        main_py = result["code"]["main.py"]

        # Check for standard imports based on dependencies
        assert "import json" in main_py, "Should import json"
        assert "import sys" in main_py, "Should import sys"
        assert "from pathlib" in main_py or "import pathlib" in main_py


class TestCodeForgeOutput:
    """Test forge output structure and manifest."""

    def test_forge_package_root_path(
        self,
        code_forge_capability: CodeForgeCapability,
        basic_forge_plan: dict,
        basic_forge_request: dict,
        temp_output_dir: str,
    ) -> None:
        """Test that forge returns absolute path to generated package."""
        result = code_forge_capability.forge(
            basic_forge_plan, basic_forge_request, temp_output_dir
        )

        assert (
            "package_root" in result
        ), "Result should contain package_root (absolute path)"
        package_root = result["package_root"]
        assert (
            Path(package_root).is_absolute()
        ), "package_root should be an absolute path"

    def test_forge_manifest_valid_json(
        self,
        code_forge_capability: CodeForgeCapability,
        basic_forge_plan: dict,
        basic_forge_request: dict,
        temp_output_dir: str,
    ) -> None:
        """Test that manifest can be serialized to JSON."""
        result = code_forge_capability.forge(
            basic_forge_plan, basic_forge_request, temp_output_dir
        )

        manifest = result["manifest"]
        try:
            json_str = json.dumps(manifest)
            json.loads(json_str)
        except (TypeError, json.JSONDecodeError) as e:
            pytest.fail(f"Manifest is not valid JSON-serializable: {str(e)}")

    def test_forge_code_files_map_completeness(
        self,
        code_forge_capability: CodeForgeCapability,
        basic_forge_plan: dict,
        basic_forge_request: dict,
        temp_output_dir: str,
    ) -> None:
        """Test that code map includes __init__.py and main.py at minimum."""
        result = code_forge_capability.forge(
            basic_forge_plan, basic_forge_request, temp_output_dir
        )

        code_map = result["code"]
        assert "__init__.py" in code_map, "Should include __init__.py"
        assert "main.py" in code_map, "Should include main.py"

        # Check they're non-empty
        assert len(code_map["__init__.py"]) > 0, "__init__.py should not be empty"
        assert len(code_map["main.py"]) > 0, "main.py should not be empty"
