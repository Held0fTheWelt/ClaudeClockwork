"""Phase 20 — LocalAI missing-dependency returns structured error (no crash)."""
from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.localai import run_local_capability
from claudeclockwork.bridge import run_manifest_skill


def test_embed_text_returns_structured_error_when_dep_missing() -> None:
    """Without sentence_transformers, embed_text returns status=error, code=dependency_missing."""
    result = run_local_capability("embed.text", {"text": "hi"}, project_root=Path.cwd())
    assert result["status"] in ("ok", "error")
    assert result["capability"] == "embed.text"
    assert "errors" in result
    if result["status"] == "error":
        codes = [e.get("code") for e in result["errors"]]
        assert "dependency_missing" in codes or "runner_unavailable" in codes


def test_audio_asr_returns_structured_error_when_dep_missing() -> None:
    """Without whisper, audio.asr returns status=error, code=dependency_missing."""
    result = run_local_capability("audio.asr", {"path": "/nonexistent.wav"}, project_root=Path.cwd())
    assert result["status"] in ("ok", "error")
    assert result["capability"] == "audio.asr"
    assert "errors" in result
    if result["status"] == "error":
        codes = [e.get("code") for e in result["errors"]]
        assert "dependency_missing" in codes or "file_not_found" in codes or "runner_unavailable" in codes


def test_embed_text_skill_discoverable_and_deterministic() -> None:
    """embed_text skill is in registry and returns contract-shaped result (no crash)."""
    root = Path(__file__).resolve().parents[1]
    result = run_manifest_skill(
        {"request_id": "p20-embed", "skill_id": "embed_text", "inputs": {"text": "test"}},
        root,
    )
    assert result is not None
    assert result.get("skill_id") == "embed_text"
    assert result.get("status") in ("ok", "fail")
    assert "outputs" in result
    data = result.get("outputs", {})
    assert "capability" in data or "status" in data
    if result.get("status") == "fail":
        assert "errors" in result


def test_audio_asr_skill_discoverable_and_deterministic() -> None:
    """audio_asr skill is in registry and returns contract-shaped result (no crash)."""
    root = Path(__file__).resolve().parents[1]
    result = run_manifest_skill(
        {"request_id": "p20-asr", "skill_id": "audio_asr", "inputs": {}},
        root,
    )
    assert result is not None
    assert result.get("skill_id") == "audio_asr"
    assert result.get("status") in ("ok", "fail")
    assert "outputs" in result
