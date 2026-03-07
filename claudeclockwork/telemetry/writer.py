"""Phase 32 — Telemetry event writer: run_id, node_id, capability, duration, status, error_codes to JSONL."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_event(
    runtime_root: Path | str,
    run_id: str,
    node_id: str = "",
    capability: str = "",
    duration_ms: float = 0,
    status: str = "ok",
    error_codes: list[str] | None = None,
) -> None:
    """Append one telemetry event to JSONL. Stable field order."""
    root = Path(runtime_root).resolve()
    telemetry_dir = root / "telemetry"
    telemetry_dir.mkdir(parents=True, exist_ok=True)
    path = telemetry_dir / "events.jsonl"
    event: dict[str, Any] = {
        "run_id": run_id,
        "node_id": node_id,
        "capability": capability,
        "duration_ms": duration_ms,
        "status": status,
    }
    if error_codes:
        event["error_codes"] = list(error_codes)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")
