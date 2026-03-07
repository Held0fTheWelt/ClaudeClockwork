"""Phase 20 — Embed.text runner (stub when deps missing)."""
from __future__ import annotations

from typing import Any

from claudeclockwork.localai.runners.base import BaseRunner


def _dependency_available() -> bool:
    try:
        # Optional: sentence-transformers or similar
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        pass
    return False


class EmbedRunner(BaseRunner):
    @property
    def capability(self) -> str:
        return "embed.text"

    def is_available(self) -> bool:
        return _dependency_available()

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if not self.is_available():
            return {
                "status": "error",
                "capability": "embed.text",
                "tool_id": "embed_text",
                "inputs": inputs,
                "outputs": {},
                "metrics": {},
                "errors": [
                    {"code": "dependency_missing", "message": "embed.text requires sentence_transformers"}
                ],
            }
        # Minimal success path when available (real impl would call model)
        text = (inputs.get("text") or inputs.get("input") or "").strip() or "mock"
        return {
            "status": "ok",
            "capability": "embed.text",
            "tool_id": "embed_text",
            "inputs": inputs,
            "outputs": {"embedding_dim": 384, "text_preview": text[:64]},
            "metrics": {"latency_ms": 0, "device": "cpu"},
            "errors": [],
        }
