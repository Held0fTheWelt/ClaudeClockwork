"""Phase 20 — Pluggable runners for local capabilities."""
from __future__ import annotations

from claudeclockwork.localai.runners.base import BaseRunner
from claudeclockwork.localai.runners.embed import EmbedRunner
from claudeclockwork.localai.runners.asr import AsrRunner
from claudeclockwork.localai.runners.code_plan import CodePlanRunner
from claudeclockwork.localai.runners.code_forge import CodeForgeRunner
from claudeclockwork.localai.runners.code_review import CodeReviewRunner
from claudeclockwork.localai.runners.code_validate import CodeValidateRunner

__all__ = [
    "BaseRunner",
    "EmbedRunner",
    "AsrRunner",
    "CodePlanRunner",
    "CodeForgeRunner",
    "CodeReviewRunner",
    "CodeValidateRunner",
]
