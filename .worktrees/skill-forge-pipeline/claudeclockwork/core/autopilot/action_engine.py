"""Phase 51 — Action engine: apply policy actions on SLO violation, log to telemetry."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dataclasses import dataclass, field


@dataclass
class AutopilotPolicy:
    """Contract: trigger and ordered actions with guardrails."""
    trigger: str = "slo_fail"
    actions: list[dict[str, Any]] = field(default_factory=list)
    max_actions_per_run: int = 5


def run_action_engine(
    policy: AutopilotPolicy,
    gate_result: dict[str, Any],
    run_root: Path | str,
) -> dict[str, Any]:
    """
    If gate_result indicates failure (e.g. passed=False), apply policy actions in order.
    Log each action to telemetry. Returns { applied: [...], logged: bool }.
    """
    run_root = Path(run_root).resolve()
    if gate_result.get("passed") is True:
        return {"applied": [], "logged": True}
    applied: list[dict[str, Any]] = []
    for i, action_spec in enumerate(policy.actions):
        if i >= policy.max_actions_per_run:
            break
        action_type = action_spec.get("action") or action_spec.get("type")
        if not action_type:
            continue
        applied.append({"action": action_type, "params": action_spec.get("params", {})})
    telemetry_path = run_root / "autopilot_telemetry.jsonl"
    telemetry_path.parent.mkdir(parents=True, exist_ok=True)
    event = {"trigger": policy.trigger, "gate_result": gate_result, "applied": applied}
    with telemetry_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    return {"applied": applied, "logged": True}
