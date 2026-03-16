from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from claudeclockwork.core.executor.executor import SkillExecutor
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.planner.planner import Planner


class ExecutionPipeline:
    def __init__(self, planner: Planner, executor: SkillExecutor, working_directory: str = ".") -> None:
        self.planner = planner
        self.executor = executor
        self.working_directory = str(Path(working_directory).resolve())

    def run(self, user_input: str, **kwargs) -> dict:
        skill_name = self.planner.pick_skill(user_input)
        if skill_name is None:
            return {
                "type": "skill_result_spec",
                "request_id": str(uuid4()),
                "skill_id": "",
                "status": "fail",
                "outputs": {},
                "errors": ["No matching skill found"],
                "warnings": [],
                "metrics": {},
            }
        context = ExecutionContext(request_id=str(uuid4()), user_input=user_input, working_directory=self.working_directory)
        result = self.executor.execute(skill_name, context, **kwargs)
        return result.to_skill_result_spec(request_id=context.request_id)
