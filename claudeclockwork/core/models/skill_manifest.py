from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SkillManifest:
    name: str
    version: str
    category: str
    description: str
    entrypoint: str
    permissions: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    enabled: bool = True
    trust_level: str = "local"
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SkillManifest":
        return cls(
            name=data["name"],
            version=data.get("version", "0.1.0"),
            category=data.get("category", "uncategorized"),
            description=data.get("description", ""),
            entrypoint=data["entrypoint"],
            permissions=list(data.get("permissions", [])),
            aliases=list(data.get("aliases", [])),
            tags=list(data.get("tags", [])),
            enabled=bool(data.get("enabled", True)),
            trust_level=data.get("trust_level", "local"),
            inputs=dict(data.get("inputs", {})),
            outputs=dict(data.get("outputs", {})),
            metadata=dict(data.get("metadata", {})),
        )
