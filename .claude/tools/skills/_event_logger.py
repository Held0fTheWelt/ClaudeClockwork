#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

DEFAULT_EVENTS_DIR = Path(".claude-performance/events")

def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def resolve_events_file(run_id: str, override: str | None = None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    DEFAULT_EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    return (DEFAULT_EVENTS_DIR / f"{run_id}.jsonl").resolve()

def append_event(event: Dict[str, Any], events_file: Path) -> None:
    events_file.parent.mkdir(parents=True, exist_ok=True)
    with events_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
