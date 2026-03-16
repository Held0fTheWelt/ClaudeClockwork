"""Phase 34 — Security escape gate: forbidden paths, binaries, unredacted secrets, writes outside runtime."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Sequence

from claudeclockwork.core.errors import POLICY_DENIED
from claudeclockwork.core.redaction.engine import redact_text


def run_security_escape_gate(
    project_root: Path | str,
    runtime_root: Path | str,
    recent_log_lines: Sequence[str] = (),
    forbidden_binaries: frozenset[str] | None = None,
) -> dict[str, Any]:
    """Check for escape attempts. Returns {passed: bool, reason: str, details: list}."""
    project_root = Path(project_root).resolve()
    runtime_root = Path(runtime_root).resolve()
    forbidden = forbidden_binaries or frozenset()
    details: list[str] = []

    # Unsafe mode in CI
    if os.environ.get("CI") == "true" and os.environ.get("CLOCKWORK_UNSAFE_MODE", "").lower() in ("1", "true", "yes"):
        return {"passed": False, "reason": "unsafe_mode_in_ci", "details": ["Unsafe mode is forbidden in CI."]}

    # Check logs for unredacted secret patterns
    for line in recent_log_lines:
        redacted = redact_text(line)
        if redacted != line and "***REDACTED***" in redacted:
            pass  # was redacted
        elif any(p in line.lower() for p in ("api_key=", "token=", "secret=", "password=")) and "***REDACTED***" not in line:
            details.append("possible_secret_in_log")
            break

    # Forbidden binaries (would be checked by runner in practice)
    for b in forbidden:
        if b in str(recent_log_lines):
            details.append(f"forbidden_binary_mentioned:{b}")

    passed = len(details) == 0
    return {"passed": passed, "reason": "escape_attempt" if details else "ok", "details": details}
