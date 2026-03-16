from __future__ import annotations

from abc import ABC, abstractmethod

from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


class SkillBase(ABC):
    @abstractmethod
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        raise NotImplementedError
