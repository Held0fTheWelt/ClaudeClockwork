"""Phase 22 — code.forge capability: forge_plan → executable code generation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from claudeclockwork.localai.templates import get_template


class CodeForgeCapability:
    """Generate executable Python code packages from forge_plan."""

    def forge(
        self, plan: dict[str, Any], request: dict[str, Any], output_dir: str
    ) -> dict[str, Any]:
        """
        Generate a code package from a forge_plan and forge_request.

        Args:
            plan: forge_plan dict with task_id, archetype, module_structure, etc.
            request: forge_request dict with task_id, archetype, purpose, constraints
            output_dir: Directory to generate the package in (absolute path)

        Returns:
            forge_result dict with:
            - task_id: str
            - archetype: str
            - code: {file_path: source_code} mapping
            - manifest: package metadata
            - package_root: absolute path to generated package
        """
        task_id = plan.get("task_id")
        archetype = plan.get("archetype")
        purpose = request.get("purpose", "")

        # Generate code files
        code_map = self._generate_code_map(plan, request)

        # Generate manifest
        manifest = self._generate_manifest(plan, request)

        # Determine package root
        module_structure = plan.get("module_structure", {})
        root_package = module_structure.get("root_package", f"forge_{archetype}")
        package_root = str(Path(output_dir) / root_package)

        return {
            "task_id": task_id,
            "archetype": archetype,
            "code": code_map,
            "manifest": manifest,
            "package_root": package_root,
        }

    def _generate_code_map(
        self, plan: dict[str, Any], request: dict[str, Any]
    ) -> dict[str, str]:
        """
        Generate the code files mapping.

        Returns:
            Dict mapping file paths to source code strings
        """
        archetype = plan.get("archetype")
        dependencies = plan.get("dependencies", [])
        purpose = request.get("purpose", "")

        code_map = {}

        # Generate __init__.py
        code_map["__init__.py"] = self._generate_init(archetype)

        # Generate main.py from template
        template_code = get_template(archetype)
        code_map["main.py"] = self._generate_main(
            template_code, dependencies, purpose, archetype
        )

        # Generate schema.py for validator/transformer if needed
        if archetype in ("validator", "transformer"):
            code_map["schema.py"] = self._generate_schema(archetype)

        return code_map

    def _generate_init(self, archetype: str) -> str:
        """Generate __init__.py file."""
        return f'''"""
{archetype.capitalize()} skill package.

Auto-generated from forge template.
"""

__version__ = "0.1.0"
__all__ = []
'''

    def _generate_main(
        self, template_code: str, dependencies: list, purpose: str, archetype: str
    ) -> str:
        """
        Generate main.py from template, adding imports from dependencies.

        Args:
            template_code: Template code as string
            dependencies: List of dependency dicts
            purpose: Purpose statement from request
            archetype: Archetype name

        Returns:
            Generated main.py source code
        """
        # Extract dependency names
        dep_names = [
            d.get("name") if isinstance(d, dict) else d for d in dependencies
        ]

        # Build additional imports beyond template defaults
        additional_imports = self._build_additional_imports(dep_names, archetype)

        # Inject additional imports into template after shebang and docstring
        if additional_imports:
            # Find where to insert: after the docstring
            lines = template_code.split("\n")
            insert_idx = 0
            in_docstring = False
            docstring_count = 0

            for i, line in enumerate(lines):
                if '"""' in line:
                    docstring_count += 1
                    if docstring_count == 2:  # End of module docstring
                        insert_idx = i + 1
                        break

            # Insert additional imports
            if insert_idx > 0:
                lines.insert(insert_idx, additional_imports)
                template_code = "\n".join(lines)

        return template_code

    def _build_additional_imports(
        self, dep_names: list[str], archetype: str
    ) -> str:
        """
        Build additional import statements beyond what's in the template.

        Templates already include: json, sys, typing
        We need to add any OTHER dependencies specified in the plan.
        """
        imports = []

        # Template already includes json, sys, typing, so skip those
        template_defaults = {"json", "sys", "typing"}

        # Standard library imports
        stdlib = {"os", "pathlib", "re", "csv", "logging"}
        for dep in dep_names:
            if dep in stdlib and dep not in template_defaults:
                if dep == "pathlib":
                    imports.append("from pathlib import Path")
                else:
                    imports.append(f"import {dep}")

        # Third-party imports
        third_party = {"yaml", "requests", "boto3", "pandas", "numpy"}
        for dep in dep_names:
            if dep in third_party:
                imports.append(f"import {dep}")

        if imports:
            return "\n".join(sorted(set(imports)))
        return ""

    def _generate_schema(self, archetype: str) -> str:
        """Generate schema.py for validator/transformer archetypes."""
        if archetype == "validator":
            return '''"""Schema definitions for validator."""

INPUT_SCHEMA = {
    "type": "object",
    "properties": {},
    "required": []
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "valid": {"type": "boolean"},
        "errors": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["valid", "errors"]
}
'''
        elif archetype == "transformer":
            return '''"""Schema definitions for transformer."""

INPUT_SCHEMA = {
    "type": "object",
    "properties": {},
    "required": []
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {},
    "required": []
}
'''
        return ""

    def _generate_manifest(
        self, plan: dict[str, Any], request: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate manifest.json metadata."""
        task_id = plan.get("task_id")
        archetype = plan.get("archetype")
        purpose = request.get("purpose", "")
        dependencies = plan.get("dependencies", [])

        # Build dependency list for manifest
        dep_names = [
            d.get("name") if isinstance(d, dict) else d for d in dependencies
        ]

        # Determine entry point based on archetype
        if archetype == "scanner":
            entry_point = "main.scan"
        elif archetype == "validator":
            entry_point = "main.validate"
        elif archetype == "reporter":
            entry_point = "main.report"
        elif archetype == "transformer":
            entry_point = "main.transform"
        elif archetype == "registry_helper":
            entry_point = "main.registry_op"
        else:
            entry_point = "main.main"

        manifest = {
            "task_id": task_id,
            "entry_point": entry_point,
            "archetype": archetype,
            "purpose": purpose,
            "dependencies": dep_names,
            "version": "0.1.0",
        }

        # Add optional schema paths for validators
        if archetype == "validator":
            manifest["input_schema_path"] = "schema.py:INPUT_SCHEMA"
            manifest["output_schema_path"] = "schema.py:OUTPUT_SCHEMA"

        return manifest
