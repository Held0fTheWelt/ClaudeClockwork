from __future__ import annotations

from claudeclockwork.legacy.adapter import LegacySkillAdapter


class ClockworkVersionBumpSkill(LegacySkillAdapter):
    legacy_skill_id = "clockwork_version_bump"
