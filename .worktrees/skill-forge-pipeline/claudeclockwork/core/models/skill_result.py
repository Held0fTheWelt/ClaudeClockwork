from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SkillResult:
    success: bool
    skill_name: str
    data: Any = None
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_skill_result_spec(self, request_id: str = "") -> dict[str, Any]:
        return {
            "type": "skill_result_spec",
            "request_id": request_id,
            "skill_id": self.skill_name,
            "status": "ok" if self.success else "fail",
            "outputs": self.data or {},
            "errors": [] if self.success or not self.error else [self.error],
            "warnings": self.warnings,
            "metrics": self.metadata,
        }
