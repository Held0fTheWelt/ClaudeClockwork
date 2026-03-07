"""Phase 60 — Remote worker fleet: deterministic network stubs."""
from claudeclockwork.workers.remote_stub import RemoteWorkerStub, heartbeat, dispatch_remote_stub


def test_heartbeat_capability_advertisement() -> None:
    w = RemoteWorkerStub(capabilities=["skill_call", "gate_check"])
    out = heartbeat(w)
    assert out["status"] == "ok"
    assert "skill_call" in out["capabilities"]


def test_dispatch_stub_deterministic() -> None:
    w = RemoteWorkerStub(endpoint="http://stub:9999")
    out = dispatch_remote_stub(w, {"job": "test"})
    assert out["status"] == "ok"
    assert out.get("stub") is True
