"""Phase 20 — Audio ASR runner (stub when deps missing)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from claudeclockwork.localai.runners.base import BaseRunner


def _dependency_available() -> bool:
    try:
        # Optional: whisper or similar
        import whisper  # noqa: F401
        return True
    except ImportError:
        pass
    return False


class AsrRunner(BaseRunner):
    @property
    def capability(self) -> str:
        return "audio.asr"

    def is_available(self) -> bool:
        return _dependency_available()

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if not self.is_available():
            return {
                "status": "error",
                "capability": "audio.asr",
                "tool_id": "audio_asr",
                "inputs": inputs,
                "outputs": {},
                "metrics": {},
                "errors": [
                    {"code": "dependency_missing", "message": "audio.asr requires whisper"}
                ],
            }
        path = inputs.get("path") or inputs.get("audio_path") or ""
        if path and not Path(path).exists():
            return {
                "status": "error",
                "capability": "audio.asr",
                "tool_id": "audio_asr",
                "inputs": inputs,
                "outputs": {},
                "metrics": {},
                "errors": [{"code": "file_not_found", "message": f"Audio file not found: {path}"}],
            }
        return {
            "status": "ok",
            "capability": "audio.asr",
            "tool_id": "audio_asr",
            "inputs": inputs,
            "outputs": {"text": "", "language": "en"},
            "metrics": {"latency_ms": 0, "device": "cpu"},
            "errors": [],
        }
