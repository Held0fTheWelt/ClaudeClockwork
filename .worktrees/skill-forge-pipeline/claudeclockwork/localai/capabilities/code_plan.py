"""Phase 21 — code.plan capability: forge_request → forge_plan conversion."""
from __future__ import annotations

from typing import Any


class CodePlanCapability:
    """Convert forge_request to forge_plan (high-level implementation plan)."""

    def plan(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Convert a forge_request into a forge_plan.

        Args:
            request: forge_request dict with task_id, archetype, purpose, constraints

        Returns:
            forge_plan dict with module_structure, key_functions, dependencies, safety_notes
        """
        task_id = request.get("task_id")
        archetype = request.get("archetype")
        purpose = request.get("purpose")
        constraints = request.get("constraints", {})
        allowed_write_roots = constraints.get("allowed_write_roots", [])
        forbidden_patterns = constraints.get("forbidden_patterns", [])

        # Build module_structure based on archetype
        module_structure = self._build_module_structure(archetype)

        # Build key_functions based on archetype
        key_functions = self._build_key_functions(archetype, purpose)

        # Build dependencies based on archetype
        dependencies = self._build_dependencies(archetype)

        # Build safety_notes from constraints
        safety_notes = self._build_safety_notes(
            archetype, allowed_write_roots, forbidden_patterns
        )

        return {
            "task_id": task_id,
            "archetype": archetype,
            "module_structure": module_structure,
            "key_functions": key_functions,
            "dependencies": dependencies,
            "safety_notes": safety_notes,
        }

    def _build_module_structure(self, archetype: str) -> dict[str, Any]:
        """Build module structure based on archetype."""
        base_modules = [
            {"name": "__init__.py", "purpose": "Package initialization"},
            {"name": "main.py", "purpose": f"Main {archetype} implementation"},
        ]

        # Add schema.py for validators
        if archetype == "validator":
            base_modules.append(
                {"name": "schema.py", "purpose": "Schema definitions and validators"}
            )

        return {
            "root_package": f"forge_{archetype}",
            "modules": base_modules,
        }

    def _build_key_functions(self, archetype: str, purpose: str) -> list[dict[str, Any]]:
        """Build key function definitions based on archetype."""
        if archetype == "scanner":
            return [
                {
                    "name": "scan",
                    "signature": "def scan(path: str) -> list[dict[str, Any]]",
                    "purpose": f"Scan files at path. {purpose}",
                }
            ]
        elif archetype == "validator":
            return [
                {
                    "name": "validate",
                    "signature": "def validate(data: dict[str, Any]) -> tuple[bool, list[str]]",
                    "purpose": f"Validate input data. {purpose}",
                }
            ]
        elif archetype == "reporter":
            return [
                {
                    "name": "report",
                    "signature": "def report(data: dict[str, Any]) -> str",
                    "purpose": f"Generate report from data. {purpose}",
                }
            ]
        elif archetype == "transformer":
            return [
                {
                    "name": "transform",
                    "signature": "def transform(input_data: dict[str, Any]) -> dict[str, Any]",
                    "purpose": f"Transform input data to output format. {purpose}",
                }
            ]
        elif archetype == "registry_helper":
            return [
                {
                    "name": "registry_op",
                    "signature": "def registry_op(operation: str, **kwargs) -> dict[str, Any]",
                    "purpose": f"Perform registry operations. {purpose}",
                }
            ]
        else:
            return []

    def _build_dependencies(self, archetype: str) -> list[dict[str, Any]]:
        """Build dependency list based on archetype."""
        # Base dependencies always present
        base_deps = [
            {"name": "json", "purpose": "JSON serialization and parsing"},
            {"name": "sys", "purpose": "System-level operations"},
            {"name": "typing", "purpose": "Type hints"},
        ]

        # Add archetype-specific dependencies
        if archetype == "scanner":
            base_deps.append(
                {
                    "name": "pathlib",
                    "purpose": "Path manipulation for file scanning",
                }
            )
        elif archetype == "registry_helper":
            base_deps.append(
                {
                    "name": "yaml",
                    "purpose": "YAML parsing for registry operations",
                }
            )

        return base_deps

    def _build_safety_notes(
        self,
        archetype: str,
        allowed_write_roots: list[str],
        forbidden_patterns: list[str],
    ) -> dict[str, Any]:
        """Build safety notes from constraints."""
        write_status = (
            "read-only" if not allowed_write_roots else f"write to {allowed_write_roots}"
        )

        safety_notes: dict[str, Any] = {
            "archetype": archetype,
            "write_restrictions": write_status,
            "execution_model": f"{archetype} skill will be invoked via forge pipeline",
        }

        if allowed_write_roots:
            safety_notes["allowed_write_roots"] = allowed_write_roots

        if forbidden_patterns:
            safety_notes["forbidden_patterns"] = forbidden_patterns
            safety_notes[
                "no_operations"
            ] = f"Explicitly forbidden: {', '.join(forbidden_patterns)}"

        # Add archetype-specific safety guidance
        if archetype == "scanner":
            safety_notes["security_concerns"] = [
                "Ensure file access respects sandbox boundaries",
                "Do not follow symlinks outside allowed paths",
            ]
        elif archetype == "validator":
            safety_notes["security_concerns"] = [
                "Validate all input structures before processing",
                "Prevent ReDoS in regex patterns",
            ]
        elif archetype == "transformer":
            safety_notes["security_concerns"] = [
                "Sanitize output to prevent injection attacks",
                "Validate transformation logic against all input types",
            ]
        elif archetype == "reporter":
            safety_notes["security_concerns"] = [
                "Do not leak sensitive information in reports",
                "Redact confidential data before output",
            ]

        return safety_notes
