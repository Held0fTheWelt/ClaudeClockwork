"""Phase 35 — Retry policy and idempotency for workers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from claudeclockwork.core.errors import POLICY_DENIED, VALIDATION_FAILED

NON_RETRYABLE = frozenset({POLICY_DENIED, VALIDATION_FAILED})


def is_retryable(result: dict[str, Any]) -> bool:
    """True if result indicates a retryable error (e.g. timeout, transient)."""
    if result.get("status") == "ok":
        return False
    errors = result.get("errors") or []
    for e in errors:
        if e.get("code") in NON_RETRYABLE:
            return False
    if result.get("error") and "timeout" in str(result.get("error", "")).lower():
        return True
    return True


def with_retry(
    fn: Callable[[], dict[str, Any]],
    run_root: Path | str,
    max_attempts: int = 3,
) -> dict[str, Any]:
    """Run fn up to max_attempts; retry only on retryable errors."""
    run_root = Path(run_root).resolve()
    last: dict[str, Any] = {}
    for _ in range(max_attempts):
        last = fn()
        if last.get("status") == "ok":
            return last
        if not is_retryable(last):
            return last
    return last


def idempotency_get(runtime_root: Path | str, key: str) -> dict[str, Any] | None:
    """Return cached result for idempotency_key if present."""
    root = Path(runtime_root).resolve() / "idempotency"
    p = root / f"{key}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def idempotency_set(runtime_root: Path | str, key: str, result: dict[str, Any]) -> None:
    """Store result for idempotency_key."""
    root = Path(runtime_root).resolve() / "idempotency"
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{key}.json").write_text(json.dumps(result) + "\n", encoding="utf-8")
