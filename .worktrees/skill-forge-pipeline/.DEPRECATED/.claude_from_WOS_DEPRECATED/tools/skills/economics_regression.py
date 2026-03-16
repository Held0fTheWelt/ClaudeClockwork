#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    # Paths are optional; this skill is evidence-driven.
    rules_path = Path(inputs.get("rules","")).resolve() if inputs.get("rules") else None
    routing_spec = Path(inputs.get("routing_spec","")).resolve() if inputs.get("routing_spec") else None
    ledger_summary = Path(inputs.get("ops_ledger_summary","")).resolve() if inputs.get("ops_ledger_summary") else None
    quality_signal = Path(inputs.get("quality_signal","")).resolve() if inputs.get("quality_signal") else None

    rules = _load_json(rules_path) if rules_path and rules_path.exists() else {"rules":[]}
    data = {}
    if routing_spec and routing_spec.exists(): data["routing_spec"] = _load_json(routing_spec)
    if ledger_summary and ledger_summary.exists(): data["ops_ledger_summary"] = _load_json(ledger_summary)
    if quality_signal and quality_signal.exists(): data["quality_signal"] = _load_json(quality_signal)

    # Minimal evaluation: detect Claude tier used and whether Oodle-first is claimed.
    violations=[]
    claude_tier = None
    oodle_order_ok = True

    rs = data.get("routing_spec", {})
    claude_tier = (rs.get("claude_tier") or rs.get("models",{}).get("claude_tier"))
    if claude_tier and isinstance(claude_tier, str) and claude_tier not in {"C0","C1","C2","C3","C4"}:
        violations.append(f"Unknown claude tier value: {claude_tier}")

    # If rules exist, we only implement a small deterministic subset:
    # - forbid C3 unless critical_gate true
    if claude_tier == "C3":
        critical_gate = bool(rs.get("critical_gate", False))
        if not critical_gate:
            violations.append("C3 used without critical_gate=true")

    # If ops ledger summary exists and says escalations but no ordering info, warn.
    ls = data.get("ops_ledger_summary", {})
    escal = ls.get("overview", {}).get("escalations", {})
    # We cannot infer order without event stream; note as warning.
    warnings=[]
    if escal and ("oodle" in escal or "claude" in escal):
        warnings.append("Escalation ordering not verifiable without event stream; provide OpsLedgerEvent log for strict checks.")

    status = "ok" if not violations else "fail"
    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id": req.get("skill_id","economics_regression"),
        "status": status,
        "outputs": {
            "violations": violations,
            "claude_tier": claude_tier,
            "rules_loaded": bool(rules.get("rules")),
        },
        "metrics": {"violation_count": len(violations)},
        "errors": violations if status=="fail" else [],
        "warnings": warnings,
    }
