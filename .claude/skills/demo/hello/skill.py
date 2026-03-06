from __future__ import annotations

from claudeclockwork.legacy.adapter import LegacySkillAdapter


class HelloSkill(LegacySkillAdapter):
    legacy_skill_id = "hello"
