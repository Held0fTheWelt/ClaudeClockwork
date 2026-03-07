"""Phase 20 — Pluggable runners for local capabilities."""
from __future__ import annotations

from claudeclockwork.localai.runners.base import BaseRunner
from claudeclockwork.localai.runners.embed import EmbedRunner
from claudeclockwork.localai.runners.asr import AsrRunner

__all__ = ["BaseRunner", "EmbedRunner", "AsrRunner"]
