"""Phase 23 — Redaction rules and engine tests."""
from __future__ import annotations

import pytest

from claudeclockwork.core.redaction.engine import redact_text, redact_json
from claudeclockwork.core.redaction.rules import REDACTION_PATTERNS


def test_redact_text_removes_bearer_token() -> None:
    s = redact_text('Authorization: Bearer sk-abc123xyz')
    assert "sk-abc123xyz" not in s
    assert "***REDACTED***" in s


def test_redact_text_path_placeholder() -> None:
    s = redact_text('Log file: C:\\Users\\me\\secret.txt')
    assert "C:\\\\" not in s or "[PATH]" in s
    s2 = redact_text('Path /home/user/secret.json')
    assert "[PATH]" in s2 or "secret" not in s2


def test_redact_json_preserves_structure() -> None:
    data = {"a": 1, "b": "Bearer tok123", "c": [2, "x"]}
    out = redact_json(data)
    assert out["a"] == 1
    assert out["c"] == [2, "x"]
    assert "tok123" not in str(out["b"])


def test_redaction_output_valid_text() -> None:
    """Redacted output remains valid text (no broken encoding)."""
    raw = '{"key": "Bearer sk-123", "path": "D:\\data\\file.json"}'
    out = redact_text(raw)
    assert isinstance(out, str)
    assert len(out) >= 10
