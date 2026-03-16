"""Phase 51 — SLO Autopilot: policy contract, action engine, mitigation paths."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from claudeclockwork.core.autopilot.action_engine import run_action_engine, AutopilotPolicy


def test_action_engine_skips_when_passed(tmp_path: Path) -> None:
    policy = AutopilotPolicy(actions=[{"action": "budget_switch", "params": {"profile": "fast"}}])
    result = run_action_engine(policy, {"passed": True}, tmp_path)
    assert result["applied"] == []
    assert result["logged"] is True


def test_action_engine_applies_actions_on_fail(tmp_path: Path) -> None:
    policy = AutopilotPolicy(
        actions=[
            {"action": "budget_switch", "params": {"profile": "fast"}},
            {"action": "incident_export", "params": {"path": ".report/incident"}},
        ],
    )
    gate_result = {"passed": False, "failure_rate": 0.2}
    result = run_action_engine(policy, gate_result, tmp_path)
    assert len(result["applied"]) == 2
    assert result["applied"][0]["action"] == "budget_switch"
    assert result["logged"] is True


def test_action_engine_logs_to_telemetry(tmp_path: Path) -> None:
    policy = AutopilotPolicy(actions=[{"action": "disable_plugin", "params": {"plugin_id": "x"}}])
    run_action_engine(policy, {"passed": False}, tmp_path)
    telemetry_path = tmp_path / "autopilot_telemetry.jsonl"
    assert telemetry_path.is_file()
    line = telemetry_path.read_text(encoding="utf-8").strip().splitlines()[-1]
    event = json.loads(line)
    assert event["trigger"] == "slo_fail"
    assert len(event["applied"]) == 1


def test_guardrail_max_actions(tmp_path: Path) -> None:
    policy = AutopilotPolicy(max_actions_per_run=2, actions=[
        {"action": "a"}, {"action": "b"}, {"action": "c"},
    ])
    result = run_action_engine(policy, {"passed": False}, tmp_path)
    assert len(result["applied"]) == 2
