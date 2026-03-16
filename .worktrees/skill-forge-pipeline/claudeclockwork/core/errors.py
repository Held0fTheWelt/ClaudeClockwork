"""Phase 32 — Standard error codes (failure taxonomy)."""
from __future__ import annotations

DEPENDENCY_MISSING = "dependency_missing"
POLICY_DENIED = "policy_denied"
TIMEOUT = "timeout"
VALIDATION_FAILED = "validation_failed"
REGRESSION_BLOCKED = "regression_blocked"
UNKNOWN_CAPABILITY = "unknown_capability"
RUNNER_UNAVAILABLE = "runner_unavailable"

ALL_CODES = frozenset({
    DEPENDENCY_MISSING,
    POLICY_DENIED,
    TIMEOUT,
    VALIDATION_FAILED,
    REGRESSION_BLOCKED,
    UNKNOWN_CAPABILITY,
    RUNNER_UNAVAILABLE,
})
