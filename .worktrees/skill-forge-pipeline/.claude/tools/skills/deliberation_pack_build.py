#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

def _read_text(p: Path, max_lines: int = 200) -> str:
    try:
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return ""
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[-max_lines:])

def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    pack_id = inputs.get("pack_id","dp-auto")
    purpose = inputs.get("purpose","Deep reasoning pack")

    paths = inputs.get("paths", {})
    def P(key):
        val = paths.get(key,"")
        return Path(val).resolve() if val else None

    plan_p = P("plan")
    routing_p = P("routing_spec")
    qsig_p = P("quality_signal")
    ledger_p = P("ops_ledger_summary")
    critic_p = P("critic_report")
    logs = paths.get("logs", [])
    if isinstance(logs, str):
        logs = [logs]
    log_paths = [Path(x).resolve() for x in logs if x]

    summary=[]
    snippets=[]
    questions=inputs.get("questions", [])
    if not isinstance(questions, list) or not questions:
        questions = ["What is the best next decision given these signals?"]

    qsig = _load_json(qsig_p) if qsig_p and qsig_p.exists() else {}
    ledger = _load_json(ledger_p) if ledger_p and ledger_p.exists() else {}

    rf = qsig.get("repeat_failures")
    sev = qsig.get("severity_max")
    if rf is not None:
        summary.append(f"repeat_failures={rf}")
    if sev:
        summary.append(f"severity_max={sev}")

    waste = ledger.get("waste", {})
    for k in ["over_escalations","pack_bloat_events","redundant_rereads"]:
        if k in waste:
            summary.append(f"{k}={waste.get(k)}")

    def add_json_snip(p: Path):
        try:
            obj = _load_json(p)
        except Exception:
            return
        txt = json.dumps(obj, indent=2, ensure_ascii=False)
        if len(txt) > 4000:
            txt = txt[:4000] + "\n...TRUNCATED..."
        snippets.append({"source": str(p), "content": txt})

    for p in [plan_p,routing_p,qsig_p,ledger_p,critic_p]:
        if p and p.exists():
            add_json_snip(p)

    for lp in log_paths[:5]:
        if lp.exists():
            snippets.append({"source": str(lp), "content": _read_text(lp, max_lines=200)})

    pack = {
        "type":"deliberation_pack_spec",
        "pack_id": pack_id,
        "purpose": purpose,
        "inputs": {
            "plan": str(plan_p) if plan_p else "",
            "routing_spec": str(routing_p) if routing_p else "",
            "quality_signal": str(qsig_p) if qsig_p else "",
            "ops_ledger_summary": str(ledger_p) if ledger_p else "",
            "critic_report": str(critic_p) if critic_p else "",
            "logs": [str(p) for p in log_paths]
        },
        "summary": summary[:12] if summary else ["no_compact_signals_found"],
        "snippets": snippets,
        "questions": questions[:10],
        "constraints": inputs.get("constraints", [])
    }

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"deliberation_pack_build",
        "status":"ok",
        "outputs":{"deliberation_pack": pack},
        "metrics":{"summary_items": len(pack["summary"]), "snippets": len(snippets)},
        "errors":[],
        "warnings":[]
    }
