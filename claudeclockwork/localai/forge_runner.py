"""Phase 25 — SkillForgeRunner: orchestrates the complete skill-forge pipeline."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Any

from claudeclockwork.localai.capabilities.code_forge import CodeForgeCapability
from claudeclockwork.localai.capabilities.code_plan import CodePlanCapability
from claudeclockwork.localai.capabilities.code_review import CodeReviewCapability
from claudeclockwork.localai.capabilities.code_validate import CodeValidateCapability


class SkillForgeRunner:
    """Orchestrates the complete skill-forge pipeline.

    Pipeline flow:
    forge_request
        → code.plan → forge_plan
        → code.forge → forge_result (code artifacts)
        → code.review → review_result (quality check)
        → code.validate → validation_result (safety gates)
        → FINAL RESULT (success=True or False)
    """

    def __init__(self, registry_path: str = ".claude/config/localai_registry.yaml"):
        """Initialize SkillForgeRunner with capability instances.

        Args:
            registry_path: Path to registry (for future use)
        """
        self.registry_path = registry_path
        self.code_plan = CodePlanCapability()
        self.code_forge = CodeForgeCapability()
        self.code_review = CodeReviewCapability()
        self.code_validate = CodeValidateCapability()

    def run_pipeline(self, forge_request: dict[str, Any]) -> dict[str, Any]:
        """Execute full pipeline: plan → forge → review → validate.

        Args:
            forge_request: Request dict with task_id, archetype, purpose, constraints

        Returns:
            Result dict with structure:
            {
                "success": bool,
                "forge_result": {...},  # From forge stage
                "review": {...},        # From review stage
                "validation": {...},    # From validate stage
                "registry_entry": {...} # For registry
            }
            Or on failure:
            {
                "success": False,
                "reason": "review_failed" | "validation_failed" | "bad_request",
                "issues": [...],
                "error": "..."
            }
        """
        # Validate request has required fields
        if not self._validate_request(forge_request):
            return {
                "success": False,
                "reason": "bad_request",
                "error": "forge_request missing required fields: task_id, archetype",
            }

        temp_dir = None
        try:
            # Create temporary directory for code generation
            temp_dir = tempfile.mkdtemp(prefix="forge_")

            # Stage 1: Plan
            forge_plan = self.code_plan.plan(forge_request)

            # Stage 2: Forge (code generation)
            forge_result = self.code_forge.forge(
                forge_plan, forge_request, temp_dir
            )

            # Stage 3: Review (quality gate)
            review_result = self._review_all_code(
                forge_result["code"],
                forge_result["archetype"],
            )

            if not review_result.get("approved", False):
                return {
                    "success": False,
                    "reason": "review_failed",
                    "issues": review_result.get("issues", []),
                    "suggestions": review_result.get("suggestions", []),
                }

            # Stage 4: Validate (safety gate)
            validation_result = self._validate_all_code(
                forge_result["code"],
                forge_result["archetype"],
            )

            if not validation_result.get("valid", False):
                return {
                    "success": False,
                    "reason": "validation_failed",
                    "checks": validation_result.get("checks", {}),
                    "errors": validation_result.get("errors", []),
                }

            # All stages passed
            registry_entry = self._create_registry_entry(forge_result, forge_request)

            return {
                "success": True,
                "forge_result": forge_result,
                "review": review_result,
                "validation": validation_result,
                "registry_entry": registry_entry,
            }

        except Exception as e:
            return {
                "success": False,
                "reason": "pipeline_error",
                "error": str(e),
            }
        finally:
            # Clean up temporary directory
            if temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _validate_request(self, request: dict[str, Any]) -> bool:
        """Validate that forge_request has required fields."""
        required_fields = ["task_id", "archetype"]
        return all(field in request for field in required_fields)

    def _review_all_code(self, code_map: dict[str, str], archetype: str) -> dict[str, Any]:
        """Review all code files and aggregate results.

        Args:
            code_map: Dict of {filename: source_code}
            archetype: Code archetype for context

        Returns:
            Aggregated review result
        """
        all_issues = []
        all_suggestions = set()
        approved = True

        for file_path, source_code in code_map.items():
            # Skip non-Python files
            if not file_path.endswith(".py"):
                continue

            result = self.code_review.review(source_code, archetype)
            all_issues.extend(result.get("issues", []))
            all_suggestions.update(result.get("suggestions", []))

            if not result.get("approved", False):
                approved = False

        return {
            "approved": approved,
            "issues": all_issues,
            "suggestions": list(all_suggestions),
        }

    def _validate_all_code(
        self, code_map: dict[str, str], archetype: str
    ) -> dict[str, Any]:
        """Validate all code files and aggregate results.

        Args:
            code_map: Dict of {filename: source_code}
            archetype: Code archetype for context

        Returns:
            Aggregated validation result
        """
        all_errors = []
        all_checks = {}
        valid = True

        for file_path, source_code in code_map.items():
            # Skip non-Python files
            if not file_path.endswith(".py"):
                continue

            result = self.code_validate.validate(source_code, archetype)
            all_errors.extend(result.get("errors", []))

            # Merge checks (all must pass)
            for check_name, check_result in result.get("checks", {}).items():
                if check_name not in all_checks:
                    all_checks[check_name] = True
                all_checks[check_name] = (
                    all_checks[check_name] and check_result
                )

            if not result.get("valid", False):
                valid = False

        return {
            "valid": valid,
            "checks": all_checks,
            "errors": all_errors,
        }

    def _create_registry_entry(
        self, forge_result: dict[str, Any], forge_request: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a registry entry from forge results.

        Args:
            forge_result: Result from forge stage
            forge_request: Original forge request

        Returns:
            Registry entry dict
        """
        manifest = forge_result.get("manifest", {})

        return {
            "task_id": forge_result.get("task_id"),
            "archetype": forge_result.get("archetype"),
            "purpose": forge_request.get("purpose"),
            "entry_point": manifest.get("entry_point"),
            "dependencies": manifest.get("dependencies", []),
            "version": manifest.get("version", "0.1.0"),
            "package_root": forge_result.get("package_root"),
        }
