# Phase 17 — LegacySkillAdapter REMOVED.
# All manifest skills use inline native delegation (SkillBase).
# Do not import LegacySkillAdapter; it no longer exists.

def __getattr__(name: str):
    if name == "LegacySkillAdapter":
        raise ImportError(
            "LegacySkillAdapter was removed in Phase 17. "
            "All skills use SkillBase with inline delegation to legacy .py modules."
        )
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
