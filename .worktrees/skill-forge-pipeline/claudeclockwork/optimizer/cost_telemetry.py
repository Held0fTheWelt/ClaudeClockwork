"""Phase 49 — Cost telemetry schema and collection. Deterministic."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def record_cost_event(
    run_root: Path | str,
    run_id: str,
    node_id: str,
    cost_units: float,
    duration_ms: float,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Append a cost event to telemetry JSONL. Schema: run_id, node_id, cost_units, duration_ms, metadata."""
    path = Path(run_root).resolve() / "cost_telemetry.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "run_id": run_id,
        "node_id": node_id,
        "cost_units": cost_units,
        "duration_ms": duration_ms,
        **(metadata or {}),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def load_cost_events(run_root: Path | str) -> list[dict[str, Any]]:
    """Load all cost events from telemetry file. Deterministic order."""
    path = Path(run_root).resolve() / "cost_telemetry.jsonl"
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
