"""Phase 59 — Plugin certification: deterministic tier assignment."""
import json
from pathlib import Path

import pytest

from claudeclockwork.plugins.certification import run_certification


def test_tier_experimental_invalid_bundle(tmp_path: Path) -> None:
    (tmp_path / "plugin.json").write_text("{}", encoding="utf-8")  # no id
    out = run_certification(tmp_path, tmp_path)
    assert out["tier"] == "experimental"


def test_tier_verified_valid_bundle(tmp_path: Path) -> None:
    (tmp_path / "plugin.json").write_text(json.dumps({"id": "p1"}), encoding="utf-8")
    out = run_certification(tmp_path, tmp_path)
    assert out["tier"] in ("verified", "certified")
