from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutionContext:
    request_id: str
    user_input: str
    working_directory: str = "."
    allowed_permissions: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)
    memory: dict[str, Any] = field(default_factory=dict)
