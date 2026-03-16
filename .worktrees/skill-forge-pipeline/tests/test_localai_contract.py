"""Phase 20 — LocalAI contract validation tests (no real weights)."""
from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.localai import validate_local_tool_result


def test_local_tool_result_success_shape_valid() -> None:
    """Valid success result passes contract validation."""
    result = {
        "status": "ok",
        "capability": "embed.text",
        "tool_id": "embed_text",
        "inputs": {"text": "hello"},
        "outputs": {"embedding_dim": 384},
        "metrics": {"latency_ms": 10, "device": "cpu"},
        "errors": [],
    }
    valid, errs = validate_local_tool_result(result)
    assert valid, errs
    assert not errs


def test_local_tool_result_error_shape_valid() -> None:
    """Valid error result (dependency_missing) passes contract validation."""
    result = {
        "status": "error",
        "capability": "audio.asr",
        "tool_id": "audio_asr",
        "inputs": {"path": "/tmp/x.wav"},
        "outputs": {},
        "metrics": {},
        "errors": [{"code": "dependency_missing", "message": "whisper not installed"}],
    }
    valid, errs = validate_local_tool_result(result)
    assert valid, errs
    assert not errs


def test_local_tool_result_metrics_keys() -> None:
    """Result with metrics latency_ms and device is valid."""
    result = {
        "status": "ok",
        "capability": "embed.text",
        "inputs": {},
        "outputs": {},
        "metrics": {"latency_ms": 0, "device": "cpu"},
        "errors": [],
    }
    valid, errs = validate_local_tool_result(result)
    assert valid, errs
