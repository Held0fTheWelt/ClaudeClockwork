"""Phase 31 — Feedback capture: manual rating, reason codes, write to telemetry JSONL."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def capture_feedback(
    runtime_root: Path | str,
    option_id: str,
    success: bool,
    run_id: str = "",
    node_id: str = "",
    quality_rating: float | None = None,
    latency_satisfaction: bool | None = None,
    reason_codes: list[str] | None = None,
) -> None:
    """Append a feedback event to telemetry JSONL. Validates against feedback_event schema."""
    root = Path(runtime_root).resolve()
    telemetry_dir = root / "telemetry"
    telemetry_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = telemetry_dir / "feedback.jsonl"
    event: dict[str, Any] = {
        "event_type": "feedback",
        "timestamp_iso": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "node_id": node_id,
        "option_id": option_id,
        "success": success,
    }
    if quality_rating is not None:
        event["quality_rating"] = quality_rating
    if latency_satisfaction is not None:
        event["latency_satisfaction"] = latency_satisfaction
    if reason_codes:
        event["reason_codes"] = list(reason_codes)
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
