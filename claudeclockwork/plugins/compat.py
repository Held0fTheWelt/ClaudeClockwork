"""Phase 40 — Compatibility matrix: Clockwork version ↔ plugin; reject incompatible."""
from __future__ import annotations


def parse_version(v: str) -> tuple[int, ...]:
    parts = []
    for s in (v or "").strip().replace("-", ".").split("."):
        try:
            parts.append(int(s))
        except ValueError:
            break
    return tuple(parts) if parts else (0,)


def is_compatible(clockwork_compat: str | None, clockwork_version: str) -> tuple[bool, str]:
    """Return (compatible, error_message)."""
    if not clockwork_compat or not clockwork_compat.strip():
        return True, ""
    cur = parse_version(clockwork_version)
    for part in clockwork_compat.split(","):
        part = part.strip()
        if part.startswith(">="):
            want = parse_version(part[2:].strip())
            if cur < want:
                return False, f"Clockwork {clockwork_version} below required {part}"
        elif part.startswith("<"):
            want = parse_version(part[1:].strip())
            if cur >= want:
                return False, f"Clockwork {clockwork_version} above allowed {part}"
    return True, ""
