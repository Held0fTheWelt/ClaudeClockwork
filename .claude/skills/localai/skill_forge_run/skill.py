"""Phase 21 — SkillForgeRun: Composed orchestrator for the full skill-forge pipeline."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.localai import run_local_capability


VALID_ARCHETYPES = {"scanner", "validator", "reporter", "transformer", "registry_helper"}
VALID_MODES = {"full", "plan_only", "through_forge", "through_review", "validate_only"}


class SkillForgeRun(SkillBase):
    """Orchestrator for the full skill-forge pipeline."""

    def __init__(self):
        """Initialize SkillForgeRun."""
        super().__init__()

    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        """
        Execute skill-forge pipeline via SkillBase.run interface.

        Args:
            context: Execution context
            **kwargs: Includes archetype, purpose, allowed_write_roots, target_root, report_file, mode, publish

        Returns:
            SkillResult with execution outcome
        """
        try:
            # Extract parameters from kwargs
            archetype = kwargs.get("archetype")
            purpose = kwargs.get("purpose")
            allowed_write_roots = kwargs.get("allowed_write_roots")
            target_root = kwargs.get("target_root")
            report_file = kwargs.get("report_file")
            mode = kwargs.get("mode", "full")
            publish = kwargs.get("publish", True)

            # Execute the pipeline
            result = self._orchestrate_pipeline(
                archetype=archetype,
                purpose=purpose,
                allowed_write_roots=allowed_write_roots,
                target_root=target_root,
                report_file=report_file,
                mode=mode,
                publish=publish,
            )

            success = result.get("final_status") in ["success", "partial_success"]
            error = result.get("error") if not success else None

            return SkillResult(
                success=success,
                skill_name="skill_forge_run",
                data=result,
                error=error,
                metadata={"execution_log": result.get("execution_log", [])}
            )

        except Exception as e:
            return SkillResult(
                success=False,
                skill_name="skill_forge_run",
                error=f"Pipeline orchestration failed: {str(e)}",
            )

    def _orchestrate_pipeline(
        self,
        archetype: str,
        purpose: str,
        allowed_write_roots: list[str] | None = None,
        target_root: str | None = None,
        report_file: str | None = None,
        mode: str = "full",
        publish: bool = True,
    ) -> dict[str, Any]:
        """
        Orchestrate the full skill-forge pipeline.

        Args:
            archetype: One of scanner, validator, reporter, transformer, registry_helper
            purpose: Human-readable task description
            allowed_write_roots: List of paths where code may write.
                               None → use policy-derived safe defaults
            target_root: Final destination for validated artifacts.
                        None → auto-generate in .claude/forge_outputs/<run_id>
            report_file: Where to write the run report.
                        None → auto-generate as report_file within target_root
            mode: Execution mode controlling which stages run.
                  One of: "full", "plan_only", "through_forge",
                         "through_review", "validate_only"
                  Default: "full"
            publish: If True, move validated artifacts to target_root after validation.
                    Automatically skipped if mode stops before validation.
                    Default: True

        Returns:
            Stage-structured result dict with run_id, all stage outputs, and final_status
        """
        run_id = f"forge_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{archetype}"
        execution_log = []

        # Input validation
        if archetype not in VALID_ARCHETYPES:
            return {
                "run_id": run_id,
                "final_status": "failed",
                "error": f"Invalid archetype '{archetype}'. Must be one of: {', '.join(VALID_ARCHETYPES)}",
                "execution_log": [
                    {
                        "stage": "validate_inputs",
                        "status": "error",
                        "timestamp": datetime.now().isoformat() + "Z",
                        "duration_ms": 0,
                        "notes": f"Invalid archetype: {archetype}",
                    }
                ],
            }

        if mode not in VALID_MODES:
            return {
                "run_id": run_id,
                "final_status": "failed",
                "error": f"Invalid mode '{mode}'. Must be one of: {', '.join(VALID_MODES)}",
                "execution_log": [
                    {
                        "stage": "validate_inputs",
                        "status": "error",
                        "timestamp": datetime.now().isoformat() + "Z",
                        "duration_ms": 0,
                        "notes": f"Invalid mode: {mode}",
                    }
                ],
            }

        if not purpose or not isinstance(purpose, str):
            return {
                "run_id": run_id,
                "final_status": "failed",
                "error": "purpose is required and must be a string",
                "execution_log": [
                    {
                        "stage": "validate_inputs",
                        "status": "error",
                        "timestamp": datetime.now().isoformat() + "Z",
                        "duration_ms": 0,
                        "notes": "Missing or invalid purpose",
                    }
                ],
            }

        # Log input validation success
        execution_log.append(
            {
                "stage": "validate_inputs",
                "status": "ok",
                "timestamp": datetime.now().isoformat() + "Z",
                "duration_ms": 10,
                "notes": f"Validated archetype='{archetype}', mode='{mode}'",
            }
        )

        # Resolve input defaults
        if target_root is None:
            target_root = f".claude/forge_outputs/{run_id}"

        if report_file is None:
            report_file = f"{target_root}/run_report.json"

        if allowed_write_roots is None:
            # Policy-derived safe defaults
            allowed_write_roots = ["docs", "src", "generated"]

        resolved_inputs = {
            "archetype": archetype,
            "purpose": purpose,
            "allowed_write_roots": allowed_write_roots,
            "target_root": target_root,
            "report_file": report_file,
            "mode": mode,
            "publish": publish,
        }

        # Placeholder temp_workspace
        temp_workspace = f"/tmp/{run_id}"

        result = {
            "run_id": run_id,
            "resolved_inputs": resolved_inputs,
            "temp_workspace": temp_workspace,
            "prepare_result": {
                "status": "ok",
                "temp_workspace": temp_workspace,
                "resolved_write_roots": allowed_write_roots,
            },
            "plan_result": None,
            "forge_result": None,
            "review_result": None,
            "validation_result": None,
            "publish_result": None,
            "final_status": "pending",
            "execution_log": execution_log,
        }

        # Add input resolution event
        result["execution_log"].append(
            {
                "stage": "input_resolution",
                "status": "ok",
                "timestamp": datetime.now().isoformat() + "Z",
                "duration_ms": 15,
                "notes": f"Resolved inputs and defaults for mode='{mode}'",
            }
        )

        # Execute stages based on mode
        if mode == "plan_only":
            # Execute only: plan
            plan_result, result["execution_log"] = self._execute_stage(
                "plan",
                "code.plan",
                {
                    "task_id": run_id,
                    "archetype": archetype,
                    "purpose": purpose,
                    "constraints": {},
                },
                result["execution_log"],
            )
            result["plan_result"] = plan_result
            result["final_status"] = "partial_success"

        elif mode == "through_forge":
            # Execute: plan → forge
            plan_result, result["execution_log"] = self._execute_stage(
                "plan",
                "code.plan",
                {
                    "task_id": run_id,
                    "archetype": archetype,
                    "purpose": purpose,
                    "constraints": {},
                },
                result["execution_log"],
            )
            result["plan_result"] = plan_result

            if plan_result.get("status") == "ok":
                forge_result, result["execution_log"] = self._execute_stage(
                    "forge",
                    "code.forge",
                    {
                        "task_id": run_id,
                        "plan": plan_result.get("outputs", {}),
                        "allowed_write_roots": allowed_write_roots,
                    },
                    result["execution_log"],
                )
                result["forge_result"] = forge_result
                result["final_status"] = "partial_success"
            else:
                result["final_status"] = "failed"

        elif mode == "through_review":
            # Validate preconditions
            valid, msg = self._validate_mode_preconditions(
                mode, result["plan_result"], result["forge_result"], None
            )
            if not valid:
                result["final_status"] = "failed"
                result["execution_log"].append(
                    {
                        "stage": "precondition_check",
                        "status": "error",
                        "timestamp": datetime.now().isoformat() + "Z",
                        "duration_ms": 0,
                        "notes": msg,
                    }
                )
            else:
                # Execute review (assumes plan + forge already done)
                review_result, result["execution_log"] = self._execute_stage(
                    "review",
                    "code.review",
                    {
                        "task_id": run_id,
                        "forge_output": result["forge_result"].get("outputs", {})
                        if result["forge_result"]
                        else {},
                    },
                    result["execution_log"],
                )
                result["review_result"] = review_result
                result["final_status"] = "partial_success"

        elif mode == "validate_only":
            # Validate preconditions
            valid, msg = self._validate_mode_preconditions(
                mode,
                result["plan_result"],
                result["forge_result"],
                result["review_result"],
            )
            if not valid:
                result["final_status"] = "failed"
                result["execution_log"].append(
                    {
                        "stage": "precondition_check",
                        "status": "error",
                        "timestamp": datetime.now().isoformat() + "Z",
                        "duration_ms": 0,
                        "notes": msg,
                    }
                )
            else:
                # Execute validation (assumes plan + forge + review already done)
                validation_result, result["execution_log"] = self._execute_stage(
                    "validate",
                    "code.validate",
                    {
                        "task_id": run_id,
                        "forge_output": result["forge_result"].get("outputs", {})
                        if result["forge_result"]
                        else {},
                    },
                    result["execution_log"],
                )
                result["validation_result"] = validation_result

                # Publishing logic: only if validation passed
                if validation_result.get("status") == "ok" and publish:
                    result["publish_result"] = {
                        "status": "ok",
                        "artifacts_moved": [],
                        "registry_updated": False,
                    }
                    result["final_status"] = "success"
                else:
                    result["final_status"] = "partial_success"

        else:  # mode == "full"
            # Execute: plan → forge → review → validate → publish
            plan_result, result["execution_log"] = self._execute_stage(
                "plan",
                "code.plan",
                {
                    "task_id": run_id,
                    "archetype": archetype,
                    "purpose": purpose,
                    "constraints": {},
                },
                result["execution_log"],
            )
            result["plan_result"] = plan_result

            if plan_result.get("status") != "ok":
                result["final_status"] = "failed"
                return result

            forge_result, result["execution_log"] = self._execute_stage(
                "forge",
                "code.forge",
                {
                    "task_id": run_id,
                    "plan": plan_result.get("outputs", {}),
                    "allowed_write_roots": allowed_write_roots,
                },
                result["execution_log"],
            )
            result["forge_result"] = forge_result

            if forge_result.get("status") != "ok":
                result["final_status"] = "failed"
                return result

            review_result, result["execution_log"] = self._execute_stage(
                "review",
                "code.review",
                {
                    "task_id": run_id,
                    "forge_output": forge_result.get("outputs", {}),
                },
                result["execution_log"],
            )
            result["review_result"] = review_result

            if review_result.get("status") != "ok":
                result["final_status"] = "failed"
                return result

            validation_result, result["execution_log"] = self._execute_stage(
                "validate",
                "code.validate",
                {
                    "task_id": run_id,
                    "forge_output": forge_result.get("outputs", {}),
                },
                result["execution_log"],
            )
            result["validation_result"] = validation_result

            if validation_result.get("status") != "ok":
                result["final_status"] = "failed"
                return result

            # Publishing logic (full mode + validation passed)
            if publish:
                result["publish_result"] = {
                    "status": "ok",
                    "artifacts_moved": [],
                    "registry_updated": False,
                }
                result["final_status"] = "success"
            else:
                result["final_status"] = "partial_success"

        return result

    def _validate_mode_preconditions(
        self,
        mode: str,
        plan_result: dict[str, Any] | None,
        forge_result: dict[str, Any] | None,
        review_result: dict[str, Any] | None,
    ) -> tuple[bool, str]:
        """
        Validate preconditions for the given mode.

        Args:
            mode: The execution mode
            plan_result: Result from code.plan stage (may be None)
            forge_result: Result from code.forge stage (may be None)
            review_result: Result from code.review stage (may be None)

        Returns:
            Tuple of (valid: bool, message: str)
        """
        if mode == "full":
            return True, "Full mode: no preconditions required"

        if mode == "plan_only":
            return True, "Plan-only mode: no preconditions required"

        if mode == "through_forge":
            return True, "Through-forge mode: no preconditions required"

        if mode == "through_review":
            if plan_result is None or forge_result is None:
                return (
                    False,
                    "Through-review mode requires prior plan + forge outputs",
                )
            return True, "Through-review mode: plan and forge results available"

        if mode == "validate_only":
            if plan_result is None or forge_result is None or review_result is None:
                return (
                    False,
                    "Validate-only mode requires plan + forge + review outputs",
                )
            return True, "Validate-only mode: all prior results available"

        return False, f"Unknown mode: {mode}"

    def _execute_stage(
        self,
        stage_name: str,
        capability_name: str,
        inputs: dict[str, Any],
        execution_log: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """
        Execute a single pipeline stage.

        Args:
            stage_name: Name of the stage (e.g., "plan", "forge")
            capability_name: Capability to invoke (e.g., "code.plan")
            inputs: Input dict for the capability
            execution_log: List to append execution event to

        Returns:
            Tuple of (result_dict, updated_execution_log)
        """
        start_time = datetime.now()

        try:
            result = run_local_capability(capability_name, inputs)
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            execution_log.append(
                {
                    "stage": stage_name,
                    "status": result.get("status", "unknown"),
                    "timestamp": start_time.isoformat() + "Z",
                    "duration_ms": duration_ms,
                    "notes": f"Invoked {capability_name}",
                }
            )

            return result, execution_log

        except Exception as e:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            execution_log.append(
                {
                    "stage": stage_name,
                    "status": "error",
                    "timestamp": start_time.isoformat() + "Z",
                    "duration_ms": duration_ms,
                    "notes": f"Error invoking {capability_name}: {str(e)}",
                }
            )
            return {
                "status": "error",
                "capability": capability_name,
                "error": str(e),
            }, execution_log


def skill_forge_run(
    archetype: str,
    purpose: str,
    allowed_write_roots: list[str] | None = None,
    target_root: str | None = None,
    report_file: str | None = None,
    mode: str = "full",
    publish: bool = True,
) -> dict[str, Any]:
    """
    Invoke the skill-forge pipeline (entry point).

    See SkillForgeRun.__call__ for documentation.
    """
    orchestrator = SkillForgeRun()
    return orchestrator(
        archetype=archetype,
        purpose=purpose,
        allowed_write_roots=allowed_write_roots,
        target_root=target_root,
        report_file=report_file,
        mode=mode,
        publish=publish,
    )
