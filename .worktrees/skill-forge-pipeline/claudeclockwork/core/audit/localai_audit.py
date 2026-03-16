"""Phase 24 — Audit log for LocalAI invocations (including blocked attempts)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def log_localai_invocation(
    project_root: Path | str,
    capability: str,
    params_hash: str,
    duration_ms: float,
    status: str,
    blocked: bool = False,
) -> None:
    """Append one audit record to runtime root audit log."""
    root = Path(project_root).resolve()
    run_root = root / ".clockwork_runtime"
    audit_dir = run_root / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    log_file = audit_dir / "localai_audit.jsonl"
    record = {
        "capability": capability,
        "params_hash": params_hash,
        "duration_ms": round(duration_ms, 2),
        "status": status,
        "blocked": blocked,
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
