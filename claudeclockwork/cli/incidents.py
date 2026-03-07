"""Phase 42 — Incident view: why did this run fail? Deterministic summary."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def incident_summary(project_root: Path | str, run_id: str | None = None, last_n: int = 1) -> dict[str, Any]:
    """Parse telemetry/workgraph metadata; return failed node, error codes, recovery, suggested next step."""
    root = Path(project_root).resolve()
    run_root = root / ".clockwork_runtime"
    events_path = run_root / "telemetry" / "events.jsonl"
    out: dict[str, Any] = {"failed_node": None, "error_codes": [], "recovery_actions": [], "suggested_next": "Docs/failure_taxonomy.md"}
    if not events_path.is_file():
        return out
    lines = events_path.read_text(encoding="utf-8").strip().split("\n")
    for line in reversed(lines[-50:]):
        try:
            e = json.loads(line)
            if e.get("status") == "fail" or e.get("status") == "error":
                out["failed_node"] = out.get("failed_node") or e.get("node_id")
                if e.get("error_code") and e["error_code"] not in out["error_codes"]:
                    out["error_codes"].append(e["error_code"])
        except (json.JSONDecodeError, TypeError):
            pass
    out["error_codes"] = sorted(out["error_codes"])
    return out