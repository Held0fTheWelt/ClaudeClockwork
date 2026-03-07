"""Phase 32 — CLI telemetry summary: top failures, regressions (deterministic output)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def run_telemetry_summary(
    runtime_root: Path | str,
    last_n: int = 20,
) -> dict[str, Any]:
    """Parse events.jsonl; return top failures and deterministic summary."""
    root = Path(runtime_root).resolve()
    path = root / "telemetry" / "events.jsonl"
    events: list[dict[str, Any]] = []
    if path.is_file():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    # Stable sort by run_id, then node_id
    events.sort(key=lambda e: (e.get("run_id", ""), e.get("node_id", "")))
    last = events[-last_n:] if len(events) > last_n else events
    failures = [e for e in last if e.get("status") != "ok"]
    error_counts: dict[str, int] = {}
    for e in failures:
        for c in e.get("error_codes", []):
            error_counts[c] = error_counts.get(c, 0) + 1
    top_errors = sorted(error_counts.items(), key=lambda x: -x[1])
    return {
        "total_events": len(events),
        "last_n": last_n,
        "failure_count": len(failures),
        "top_error_codes": top_errors[:10],
    }
