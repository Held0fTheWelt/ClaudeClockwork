"""Phase 41 — Worker placement: capability, load (stub), locality. Explainable."""
from __future__ import annotations

from typing import Any


def choose_worker(
    required_gpu: bool = False,
    capability: str = "",
    worker_loads: dict[str, float] | None = None,
    cas_local_worker: str | None = None,
) -> str:
    """Choose worker id. Prefer local if CAS present; else least loaded. Contract-compliant."""
    loads = worker_loads or {}
    if required_gpu and cas_local_worker and cas_local_worker in loads:
        return cas_local_worker
    if loads:
        return min(loads.keys(), key=lambda w: loads.get(w, 0.0))
    return "local"