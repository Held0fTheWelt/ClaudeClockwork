"""Phase 39 — Recovery: fallback strategies and telemetry."""
from __future__ import annotations

from typing import Any


def fallback_local_worker(_envelope: dict[str, Any]) -> str:
    """Strategy: reroute to local worker. Returns strategy id."""
    return "local_worker"


def fallback_bypass_cache() -> str:
    """Strategy: bypass cache and recompute. Returns strategy id."""
    return "bypass_cache"


def record_recovery(action: str, node_id: str, reason: str) -> dict[str, Any]:
    """Record recovery action for telemetry."""
    return {"action": action, "node_id": node_id, "reason": reason}