#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

DEFAULT_LIMITATIONS = [
    "This edits a config file; keep it under version control if you want audit history.",
    "If you store the config as YAML elsewhere, this implementation expects JSON-in-YAML (valid JSON)."
]

def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8", errors="ignore"))

def _save(p: Path, obj: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    cfg_path = Path(inputs.get("config_path", ".claude/config/performance_budgeting.yaml")).resolve()
    if not cfg_path.exists():
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),"skill_id":"performance_toggle",
                "status":"error","outputs":{},"errors":[f"config missing: {cfg_path}"],"warnings":[],
                "metrics":{}}

    before = _load(cfg_path)
    after = dict(before)

    if "enabled" in inputs:
        after["enabled"] = bool(inputs["enabled"])
    if "include_self_costs" in inputs:
        after["include_self_costs"] = bool(inputs["include_self_costs"])
    if "print_cli" in inputs:
        after["print_cli"] = bool(inputs["print_cli"])
    if "export_charts" in inputs:
        after["export_charts"] = bool(inputs["export_charts"])
    if "auto_disable" in inputs and isinstance(inputs["auto_disable"], dict):
        after.setdefault("auto_disable", {})
        after["auto_disable"].update(inputs["auto_disable"])

    reason = str(inputs.get("reason","(no reason provided)"))
    _save(cfg_path, after)

    now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    report = {"type":"performance_toggle_report","generated_at":now,"before":before,"after":after,"reason":reason}

    out_dir = Path(".claude-performance/reports").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"performance_toggle_{now.replace(':','').replace('-','')}.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    cli = []
    cli.append("== Performance Budgeting Toggle ==")
    cli.append(f"enabled: {before.get('enabled')} -> {after.get('enabled')}")
    cli.append(f"include_self_costs: {before.get('include_self_costs')} -> {after.get('include_self_costs')}")
    cli.append(f"reason: {reason}")

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"performance_toggle",
        "status":"ok",
        "outputs":{"report": report, "report_json_path": str(out_path), "cli_summary":"\n".join(cli) + "\n"},
        "errors": [],
        "warnings": [],
        "metrics": {"enabled": int(bool(after.get("enabled")))}
    }
