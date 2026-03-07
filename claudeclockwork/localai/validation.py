"""Phase 24 — LocalAI parameter validation (schemas + input validation)."""
from __future__ import annotations

from typing import Any

# Minimal schema keys per capability (optional full JSON Schema later)
EMBED_TEXT_PARAMS = {"text", "input"}
AUDIO_ASR_PARAMS = {"path", "audio_path"}


def validate_embed_text(inputs: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate embed.text inputs. Returns (valid, errors)."""
    errors: list[str] = []
    if not isinstance(inputs, dict):
        return False, ["inputs must be a dict"]
    # Allow empty; text/input optional
    for k in inputs:
        if k not in EMBED_TEXT_PARAMS:
            errors.append(f"unknown param: {k}")
    return len(errors) == 0, errors


def validate_audio_asr(inputs: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate audio.asr inputs. Returns (valid, errors)."""
    errors: list[str] = []
    if not isinstance(inputs, dict):
        return False, ["inputs must be a dict"]
    for k in inputs:
        if k not in AUDIO_ASR_PARAMS:
            errors.append(f"unknown param: {k}")
    return len(errors) == 0, errors


def validate_localai_inputs(capability: str, inputs: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate inputs for a capability. Returns (valid, errors)."""
    if capability == "embed.text":
        return validate_embed_text(inputs)
    if capability == "audio.asr":
        return validate_audio_asr(inputs)
    return True, []
