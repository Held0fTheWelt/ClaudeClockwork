"""Phase 35 — Dispatcher: submit job envelope to local worker with idempotency."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from claudeclockwork.workers.local_worker import process_envelope
from claudeclockwork.workers.retry import with_retry, idempotency_get, idempotency_set


def dispatch(envelope: dict[str, Any], project_root: Path | str) -> dict[str, Any]:
    """Dispatch envelope to local worker. Uses idempotency cache and retry policy."""
    root = Path(project_root).resolve()
    run_root = root / ".clockwork_runtime"
    key = envelope.get("idempotency_key")
    if key:
        cached = idempotency_get(run_root, key)
        if cached is not None:
            return cached
    out = with_retry(lambda: process_envelope(envelope, project_root), run_root=run_root)
    if key and out.get("status") == "ok":
        idempotency_set(run_root, key, out)
    return out
