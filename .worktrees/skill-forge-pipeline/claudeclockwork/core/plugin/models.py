from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PluginManifest:
    id: str
    name: str
    version: str
    description: str
    permissions: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    requires_plugins: list[str] = field(default_factory=list)
    optional_plugins: list[str] = field(default_factory=list)
    enabled_by_default: bool = True
    trust_level: str = "local"
    lifecycle: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PluginManifest":
        name = data.get("name", "")
        return cls(
            id=data.get("id", name),
            name=name,
            version=data.get("version", "0.1.0"),
            description=data.get("description", ""),
            permissions=list(data.get("permissions", [])),
            capabilities=list(data.get("capabilities", [])),
            requires_plugins=list(data.get("requires_plugins", [])),
            optional_plugins=list(data.get("optional_plugins", [])),
            enabled_by_default=bool(data.get("enabled_by_default", True)),
            trust_level=data.get("trust_level", "local"),
            lifecycle=dict(data.get("lifecycle", {})),
            metadata={k: v for k, v in data.items() if k not in {
                "id", "name", "version", "description", "permissions", "capabilities",
                "requires_plugins", "optional_plugins", "enabled_by_default",
                "trust_level", "lifecycle",
            }},
        )
