"""Phase 60 — Remote worker fleet: HTTP transport stub, token auth, heartbeat. Deterministic stubs for tests."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RemoteWorkerStub:
    """Stub: worker endpoint, token, heartbeat/capabilities. No real network."""
    endpoint: str = "http://localhost:0"
    token: str = ""
    capabilities: list[str] = None

    def __post_init__(self) -> None:
        if self.capabilities is None:
            self.capabilities = ["skill_call"]


def heartbeat(worker: RemoteWorkerStub) -> dict[str, Any]:
    """Stub: return capability advertisement."""
    return {"status": "ok", "capabilities": worker.capabilities}


def dispatch_remote_stub(worker: RemoteWorkerStub, envelope: dict[str, Any]) -> dict[str, Any]:
    """Stub: no real HTTP; return deterministic response."""
    return {"status": "ok", "stub": True, "worker": worker.endpoint}
