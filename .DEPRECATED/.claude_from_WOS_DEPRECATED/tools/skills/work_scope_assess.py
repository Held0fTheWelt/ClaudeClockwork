#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime

DEFAULT_LIMITATIONS = [
    "Heuristic scoring; does not understand semantics fully.",
    "Use critic feedback loop to improve parameters over time."
]

def _safe_num(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    task = str(inputs.get("task","")).strip()
    task_type = str(inputs.get("task_type","general")).strip()
    signals = inputs.get("signals") or {}

    # Heuristic complexity score 0..10
    score = 0.0
    reasons = []

    length = len(task)
    if length > 800:
        score += 2.0; reasons.append("long_task_description")
    elif length > 250:
        score += 1.0; reasons.append("medium_task_description")

    files = _safe_num(signals.get("files_touched", 0), 0)
    if files >= 30:
        score += 2.5; reasons.append("many_files")
    elif files >= 10:
        score += 1.5; reasons.append("multi_file_change")
    elif files >= 3:
        score += 0.8; reasons.append("few_files")

    if bool(signals.get("requires_code_changes", False)):
        score += 1.5; reasons.append("code_changes")
    if bool(signals.get("ambiguity_high", False)):
        score += 2.0; reasons.append("high_ambiguity")
    if bool(signals.get("has_security_impact", False)):
        score += 2.0; reasons.append("security_impact")
    if bool(signals.get("has_legal_impact", False)):
        score += 1.0; reasons.append("legal_impact")

    score = max(0.0, min(10.0, score))

    # Tier mapping
    if score <= 3.0:
        tier = "low"
    elif score <= 6.0:
        tier = "medium"
    else:
        tier = "high"

    now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    report = {
        "type":"work_scope_report",
        "generated_at": now,
        "task": task,
        "task_type": task_type,
        "complexity_score_0_10": score,
        "tier": tier,
        "reasons": reasons,
        "signals": signals
    }

    # write into .report by convention if run_id env exists
    run_id = __import__("os").getenv("CLOCKWORK_RUN_ID","run-unknown")
    out_dir = __import__("pathlib").Path(".report")/"routing"/run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir/"work_scope_report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"work_scope_assess",
        "status":"ok",
        "outputs":{
            "report": report,
            "report_json_path": str(out_path)
        },
        "errors": [],
        "warnings": [],
        "metrics":{
            "complexity_score": score
        }
    }
