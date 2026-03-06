from __future__ import annotations

from claudeclockwork.core.planner.capability_matcher import CapabilityMatcher
from claudeclockwork.core.registry.skill_registry import SkillRegistry


class Planner:
    def __init__(self, registry: SkillRegistry) -> None:
        self.registry = registry

    def pick_skill(self, user_input: str) -> str | None:
        ranked = CapabilityMatcher.rank(user_input, self.registry.list_skills(enabled_only=True))
        return ranked[0].name if ranked else None
