"""Phase 23 — Evidence export tests (redacted bundle + manifest)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from claudeclockwork.core.evidence_export import export_evidence_bundle


def test_export_evidence_bundle_creates_manifest_and_zip() -> None:
    """Export with redact=True creates bundle and manifest with redacted=True."""
    root = Path(__file__).resolve().parents[1]
    out = export_evidence_bundle(root, out_dir=root / ".clockwork_runtime" / "redacted_exports", redact=True)
    assert out["redacted"] is True
    assert "bundle_path" in out
    assert "manifest_path" in out
    manifest_path = Path(out["manifest_path"])
    assert manifest_path.is_file()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data.get("redacted") is True
    assert "timestamp" in data
    assert "file_count" in data
