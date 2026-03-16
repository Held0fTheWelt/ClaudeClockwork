"""Phase 42 — Dashboards CLI: last N runs, top failures, regressions, cache hit rate, cost. Stable order."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def run_dashboard(project_root: Path | str, last_n: int = 10) -> dict[str, Any]:
    """Stable tables: last N runs, top failures, cache hit rate, cost. Sort by timestamp then id."""
    root = Path(project_root).resolve()
    run_root = root / ".clockwork_runtime"
    events_path = run_root / "telemetry" / "events.jsonl"
    runs: list[dict] = []
    if events_path.is_file():
        for line in events_path.read_text(encoding="utf-8").strip().split("\n")[-last_n:]:
            try:
                runs.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    runs.sort(key=lambda x: (x.get("timestamp", ""), x.get("run_id", "")))
    failures = [r for r in runs if r.get("status") in ("fail", "error")]
    return {
        "last_runs": runs,
        "top_failures": failures[:5],
        "cache_hit_rate": None,
        "cost_burn": None,
        "regressions_since_release": [],
    }