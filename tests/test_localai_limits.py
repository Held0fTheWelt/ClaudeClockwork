"""Phase 24 — LocalAI validation and limits (parameter validation, no real runner)."""
from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.localai.validation import (
    validate_embed_text,
    validate_audio_asr,
    validate_localai_inputs,
)


def test_validate_embed_text_accepts_valid() -> None:
    valid, errs = validate_embed_text({"text": "hello"})
    assert valid
    assert not errs


def test_validate_embed_text_rejects_unknown_param() -> None:
    valid, errs = validate_embed_text({"text": "hi", "unknown_key": 1})
    assert not valid
    assert any("unknown" in e for e in errs)


def test_validate_audio_asr_accepts_path() -> None:
    valid, errs = validate_audio_asr({"path": "/tmp/x.wav"})
    assert valid


def test_validate_localai_inputs_unknown_capability_passes() -> None:
    valid, errs = validate_localai_inputs("unknown.cap", {})
    assert valid  # no schema => pass through
