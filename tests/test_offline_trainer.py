"""Phase 31 — Offline trainer tests: deterministic snapshot, guardrails."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from claudeclockwork.router.training.offline_trainer import run_offline_training


def test_offline_trainer_deterministic_snapshot() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "router_feedback.jsonl").write_text(
            '{"option_id": "opt1", "success": true}\n{"option_id": "opt1", "success": false}\n',
            encoding="utf-8",
        )
        r1 = run_offline_training(root, seed=42)
        r2 = run_offline_training(root, seed=42)
        assert r1["profile_count"] == r2["profile_count"]
        assert (root / "router_profiles_snapshot.json").is_file()
        snap = json.loads((root / "router_profiles_snapshot.json").read_text())
        assert "profiles" in snap
        assert snap["profiles"].get("opt1", {}).get("trials") == 2
        assert snap["profiles"].get("opt1", {}).get("successes") == 1


def test_offline_trainer_guardrails_exclude_banned() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "router_feedback.jsonl").write_text(
            '{"option_id": "banned_opt", "success": true}\n',
            encoding="utf-8",
        )
        run_offline_training(root, banned={"banned_opt"})
        snap = json.loads((root / "router_profiles_snapshot.json").read_text())
        assert "banned_opt" not in snap.get("profiles", {})
