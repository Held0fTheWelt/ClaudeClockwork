#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def _safe_load(path_str: str) -> dict:
    if not path_str:
        return {}
    p = Path(path_str)
    if not p.exists():
        return {}
    try:
        return _load_json(p)
    except Exception:
        return {}

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    # Support either feeding FeedbackRequestSpec via inputs, or embedding evidence paths directly.
    fb = inputs.get("feedback_request") if isinstance(inputs.get("feedback_request"), dict) else None
    if fb is None and req.get("type") == "feedback_request_spec":
        fb = req

    recipient_role = (fb or {}).get("recipient_role", inputs.get("recipient_role","personaler"))
    mode = (fb or {}).get("feedback_mode", inputs.get("feedback_mode","balanced"))
    budget = (fb or {}).get("budget", inputs.get("budget","tool_only"))

    evidence = (fb or {}).get("evidence", inputs.get("evidence", {})) or {}
    routing = _safe_load(evidence.get("routing_spec",""))
    ledger = _safe_load(evidence.get("ops_ledger_summary",""))
    qsig = _safe_load(evidence.get("quality_signal",""))
    critic = _safe_load(evidence.get("critic_report",""))

    issues=[]
    recs=[]

    # Heuristics: detect over-escalation if claude tier > C0 but no repeat failures or high severity.
    claude_tier = routing.get("claude_tier") or routing.get("models",{}).get("claude_tier")
    repeat_failures = qsig.get("repeat_failures") or qsig.get("signals",{}).get("repeat_failures")
    severity_max = qsig.get("severity_max") or qsig.get("signals",{}).get("severity_max")
    try:
        rf = int(repeat_failures) if repeat_failures is not None else 0
    except Exception:
        rf = 0

    if isinstance(claude_tier, str) and claude_tier not in ("C0", None, ""):
        if rf < 2 and (severity_max not in ("high","critical")):
            issues.append({"code":"over_escalation","severity":"med","summary":"Claude tier raised without repeat failures/high severity."})
            recs.append("Prefer Oodle-first verifier before raising Claude tier.")

    # Pack bloat / redundant reread from ledger if present
    waste = ledger.get("waste", {})
    if waste.get("pack_bloat_events", 0):
        issues.append({"code":"pack_bloat","severity":"low","summary":"Pack bloat events detected."})
        recs.append("Tighten pack hints and enforce pack budget caps.")
    if waste.get("redundant_rereads", 0):
        issues.append({"code":"redundant_reread","severity":"med","summary":"Redundant re-reads detected."})
        recs.append("Use inherit/verify trust modes; avoid rebuild unless risk is high.")

    # Drift events
    quality = ledger.get("quality", {})
    if quality.get("drift_events", 0):
        issues.append({"code":"drift","severity":"high","summary":"Role drift events detected."})
        recs.append("Clarify agent scope; enforce needs_specialist reporting instead of scope creep.")

    # Missing roles/skills recommendations (ledger capacity)
    cap = ledger.get("capacity", {})
    missing_roles = cap.get("missing_roles", []) if isinstance(cap.get("missing_roles", []), list) else []
    if missing_roles:
        issues.append({"code":"missing_role","severity":"low","summary":"Missing roles suggested by ops ledger."})
        if mode != "strict":
            recs.append(f"Consider adding role(s): {', '.join(missing_roles[:3])}")

    # Creative mode adds one bold option (still capped)
    if mode == "creative":
        recs.append("Try 'creativity_burst' + 'idea_scoring' before planning to improve options cheaply.")

    # Cap recommendations based on mode
    max_recs = 1 if mode == "strict" else 3
    recs = recs[:max_recs]

    verdict = "keep"
    if any(i["severity"] == "high" for i in issues):
        verdict = "escalate"
    elif issues:
        verdict = "adjust"

    out = {
        "type":"decision_feedback_spec",
        "request_id": (fb or {}).get("request_id", req.get("request_id","")),
        "recipient_role": recipient_role,
        "verdict": verdict,
        "issues": issues,
        "recommendations": recs,
        "notes": "tool-first decision feedback"
    }

    return {
        "type":"skill_result_spec",
        "request_id": (fb or {}).get("request_id", req.get("request_id","")),
        "skill_id":"decision_feedback",
        "status":"ok",
        "outputs":{"decision_feedback": out, "mode": mode, "budget": budget},
        "metrics":{"issues": len(issues), "recommendations": len(recs)},
        "errors":[],
        "warnings":[]
    }
