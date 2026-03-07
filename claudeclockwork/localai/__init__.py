"""Phase 20 — Local non-LLM tooling (embeddings, ASR, optional vision)."""
from __future__ import annotations

from claudeclockwork.localai.contracts import validate_local_tool_result
from claudeclockwork.localai.registry import load_registry
from claudeclockwork.localai.runtime import run_local_capability

__all__ = [
    "run_local_capability",
    "load_registry",
    "validate_local_tool_result",
]
