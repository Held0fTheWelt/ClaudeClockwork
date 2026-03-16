"""Phase 34 — External runner sandbox tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from claudeclockwork.localai.runners.external import run_external_sandboxed, ExternalRunner, ALLOWED_BINARIES


def test_non_allowlisted_binary_blocked() -> None:
    out = run_external_sandboxed(["curl", "-s", "https://example.com"], ".", timeout_seconds=1)
    assert out.get("status") == "error"
    assert any(e.get("code") == "policy_denied" for e in out.get("errors", []))


def test_argv_must_be_list() -> None:
    r = ExternalRunner()
    out = r.run({"argv": "echo hello"})
    assert out.get("status") == "error"
    assert "argv must be list" in str(out.get("errors", []))


def test_allowlisted_binary_ok() -> None:
    out = run_external_sandboxed([sys.executable, "-c", "print(1)"], ".", timeout_seconds=5)
    assert out.get("status") == "ok"
    assert "1" in (out.get("stdout") or "")
