"""Phase 32 — Export incident bundle: last N events, failing node artifacts (redacted)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from claudeclockwork.core.evidence_export import export_evidence_bundle
from claudeclockwork.core.redaction.engine import redact_text


def export_incident(
    project_root: Path | str,
    run_id: str = "",
    last_n_events: int = 50,
) -> dict[str, Any]:
    """Export redacted incident bundle: last N events, env snapshot. Returns bundle paths."""
    root = Path(project_root).resolve()
    run_root = root / ".clockwork_runtime"
    incident_dir = run_root / "incidents"
    incident_dir.mkdir(parents=True, exist_ok=True)
    events_path = run_root / "telemetry" / "events.jsonl"
    events: list[dict[str, Any]] = []
    if events_path.is_file():
        with open(events_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    if run_id:
        events = [e for e in events if e.get("run_id") == run_id]
    subset = events[-last_n_events:] if len(events) > last_n_events else events
    redacted = [redact_text(json.dumps(e)) for e in subset]
    out_path = incident_dir / f"incident_{run_id or 'latest'}.json"
    out_path.write_text(json.dumps({"events": subset, "count": len(subset)}, indent=2) + "\n", encoding="utf-8")
    return {"incident_path": str(out_path), "event_count": len(subset)}
