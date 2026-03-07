"""Phase 20 — Local capability runtime: dispatch to runners, return contract-shaped result."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from claudeclockwork.localai.registry import load_registry
from claudeclockwork.localai.runners import EmbedRunner, AsrRunner

_RUNNERS: dict[str, Any] = {
    "embed.text": EmbedRunner(),
    "audio.asr": AsrRunner(),
}


def run_local_capability(
    capability: str,
    inputs: dict[str, Any],
    project_root: Path | str | None = None,
) -> dict[str, Any]:
    """
    Run a local capability. Returns local_tool_result-shaped dict.
    If runner unavailable: status=error, errors=[{code: "dependency_missing", ...}].
    """
    runner = _RUNNERS.get(capability)
    if runner is None:
        reg = load_registry(project_root or Path.cwd()) if project_root else {"capabilities": {}}
        caps = reg.get("capabilities", {})
        if capability not in caps:
            return {
                "status": "error",
                "capability": capability,
                "inputs": inputs,
                "outputs": {},
                "metrics": {},
                "errors": [{"code": "unknown_capability", "message": f"Unknown capability: {capability}"}],
            }
        # Registry knows it but we have no runner
        return {
            "status": "error",
            "capability": capability,
            "inputs": inputs,
            "outputs": {},
            "metrics": {},
            "errors": [{"code": "runner_unavailable", "message": f"No runner for {capability}"}],
        }
    return runner.run(inputs)
