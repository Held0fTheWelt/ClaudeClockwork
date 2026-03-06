from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.runtime import build_executor, build_registry


def run_manifest_skill(req: dict, project_root: str | Path) -> dict | None:
    skill_id = req.get("skill_id")
    if not skill_id:
        return None
    project_root = Path(project_root).resolve()
    registry = build_registry(project_root)
    manifest = registry.get_manifest(skill_id)
    if manifest is None:
        return None
    executor = build_executor(project_root)
    context = ExecutionContext(
        request_id=req.get("request_id", ""),
        user_input=skill_id,
        working_directory=str(project_root),
    )
    result = executor.execute(skill_id, context, **(req.get("inputs") or {}))
    return result.to_skill_result_spec(request_id=context.request_id)
