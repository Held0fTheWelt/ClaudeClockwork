#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

def _load_settings() -> dict:
    p = Path(".claude/settings.local.json")
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    gate_req = inputs.get("gate_request")
    if isinstance(gate_req, dict) and gate_req.get("type") == "policy_gate_request":
        gr = gate_req
    elif req.get("type") == "policy_gate_request":
        gr = req
    else:
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),
                "skill_id":"policy_gatekeeper","status":"fail","outputs":{},
                "metrics":{}, "errors":["Expected policy_gate_request"], "warnings":[]}

    settings = _load_settings()
    no_llm = bool(gr["signals"].get("no_llm")) or bool(settings.get("modes", {}).get("no_llm", False))

    action = gr["requested_action"]
    sig = gr["signals"]
    risk = sig.get("risk","low")
    rf = int(sig.get("repeat_failures",0))
    drift = int(sig.get("drift_events",0))
    over = int(sig.get("over_escalations",0))
    exp = int(sig.get("experiments_requested",0))
    explicit_deep = bool(sig.get("explicit_deep_review", False))

    allowed = True
    reason = "default_allow"
    alt = ""

    # Rule 1: No-LLM mode
    if no_llm:
        if action in ("no_llm_check",):
            allowed = True
            reason = "no_llm_mode"
        elif action in ("experiment", "creative_feedback", "deep_oodle", "rebuild"):
            allowed = False
            reason = "no_llm_mode_blocks_llm_actions"
            alt = "Use tool_only checks or disable no_llm for this action."
        else:
            allowed = False
            reason = "no_llm_mode_unknown_action"
            alt = "Use tool_only."
    else:
        # Deep oodle gate
        if action == "deep_oodle":
            if risk in ("high","critical") or rf >= 3 or drift >= 2 or over >= 2 or explicit_deep:
                allowed = True
                reason = "deep_oodle_triggered"
            else:
                allowed = False
                reason = "deep_oodle_trigger_not_met"
                alt = "Stay tool-first; escalate verifier depth before deep oodle."

        # Creative feedback gate
        if action == "creative_feedback":
            if rf >= 2 or over >= 1 or explicit_deep:
                allowed = True
                reason = "creative_feedback_allowed"
            else:
                allowed = False
                reason = "creative_feedback_requires_signal"
                alt = "Use balanced feedback or tool-only decision_feedback."

        # Rebuild gate
        if action == "rebuild":
            if risk in ("high","critical") or rf >= 2:
                allowed = True
                reason = "rebuild_allowed"
            else:
                allowed = False
                reason = "rebuild_requires_risk_or_failures"
                alt = "Use inherit/verify trust modes."

        # Experiment budget gate
        if action == "experiment":
            max_exp = int(settings.get("experiment", {}).get("max_per_run", 3))
            if exp <= max_exp:
                allowed = True
                reason = "experiment_within_budget"
            else:
                allowed = False
                reason = "experiment_budget_exceeded"
                alt = f"Reduce experiments_requested to <= {max_exp}"

    decision = {
        "type":"policy_gate_decision",
        "request_id": gr["request_id"],
        "requested_action": action,
        "allowed": allowed,
        "reason": reason,
        "alternative": alt
    }

    return {"type":"skill_result_spec","request_id":gr["request_id"],
            "skill_id":"policy_gatekeeper","status":"ok",
            "outputs":{"decision": decision},
            "metrics":{}, "errors":[], "warnings":[]}
