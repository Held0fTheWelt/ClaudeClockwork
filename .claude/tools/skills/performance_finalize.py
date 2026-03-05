#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

DEFAULT_LIMITATIONS = [
    "This is deterministic orchestration. It calls other deterministic skills in-process.",
    "Token accuracy depends on your event logging. If you don't log per step, attribution will be coarse."
]

def _load_cfg(cfg_path: Path) -> dict:
    return json.loads(cfg_path.read_text(encoding="utf-8", errors="ignore"))

def _save_cfg(cfg_path: Path, cfg: dict) -> None:
    cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

def _import_run(root: Path, module_path: Path, fn_name: str = "run"):
    import importlib.util
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return getattr(mod, fn_name)

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    run_id = str(inputs.get("run_id","run-unknown"))
    cfg_path = Path(inputs.get("config_path",".claude/config/performance_budgeting.yaml")).resolve()
    if not cfg_path.exists():
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),"skill_id":"performance_finalize",
                "status":"error","outputs":{},"errors":[f"config missing: {cfg_path}"],"warnings":[],
                "metrics":{}}

    cfg = _load_cfg(cfg_path)
    enabled = bool(cfg.get("enabled", True))

    now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    ts_slug = now.replace(":","").replace("-","")

    if not enabled:
        return {
            "type":"skill_result_spec",
            "request_id": req.get("request_id",""),
            "skill_id":"performance_finalize",
            "status":"ok",
            "outputs":{"skipped": True, "reason":"performance budgeting disabled", "cli_summary":"== Performance finalize ==\n(disabled)\n"},
            "errors": [],
            "warnings": [],
            "metrics": {"skipped": 1}
        }

    # Build events sources
    sources = inputs.get("events_sources") or []
    if not sources:
        tmpl = cfg.get("events_sources_template") or [".claude-performance/events/{run_id}.jsonl"]
        sources = [t.format(run_id=run_id) for t in tmpl]

    output_dir = cfg.get("output_dir",".claude-performance/reports")
    export_prefix = f"budget_{run_id}"
    top_n = int(cfg.get("top_n", 10))

    # Call budget_analyze
    root = Path(".").resolve()
    budget_run = _import_run(root, root/".claude/tools/skills/budget_analyze.py")
    budget_req = {
        "type":"skill_request_spec",
        "request_id": req.get("request_id","")+":budget",
        "skill_id":"budget_analyze",
        "inputs":{
            "run_id": run_id,
            "events_sources": sources,
            "output_dir": output_dir,
            "export_prefix": export_prefix,
            "top_n": top_n,
            "print_cli": bool(cfg.get("print_cli", True)),
            "export_charts": bool(cfg.get("export_charts", True))
        }
    }
    budget_res = budget_run(budget_req)
    budget_report = (budget_res.get("outputs", {}) or {}).get("report", {})
    cli = (budget_res.get("outputs", {}) or {}).get("cli_summary","")

    # Auto-disable if configured
    auto = cfg.get("auto_disable") or {}
    if bool(auto.get("enabled", False)):
        threshold = int(auto.get("disable_if_total_tokens_gte", 0) or 0)
        total_tokens = int(((budget_report.get("totals") or {}).get("total_tokens")) or 0)
        if threshold and total_tokens >= threshold:
            cfg["enabled"] = False
            _save_cfg(cfg_path, cfg)
            cli += f"\n[auto-disable] performance budgeting disabled (total_tokens={total_tokens} >= {threshold})\n"

    # Optionally do review consolidation (panels file provided)
    do_review = bool(inputs.get("do_review", False))
    panels_path = inputs.get("panels_path")
    review_res = None
    if do_review and panels_path:
        eff_run = _import_run(root, root/".claude/tools/skills/efficiency_review.py")
        review_req = {
            "type":"skill_request_spec",
            "request_id": req.get("request_id","")+":review",
            "skill_id":"efficiency_review",
            "inputs":{
                "run_id": run_id,
                "budget_report_path": f"{output_dir}/{export_prefix}_report.json",
                "panels_path": panels_path,
                "output_dir": output_dir,
                "export_prefix": f"review_{run_id}",
                "print_cli": bool(cfg.get("print_cli", True)),
                "export_charts": bool(cfg.get("export_charts", True))
            }
        }
        review_res = eff_run(review_req)
        cli += "\n" + ((review_res.get("outputs", {}) or {}).get("cli_summary",""))

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"performance_finalize",
        "status":"ok",
        "outputs":{
            "budget_result": budget_res,
            "review_result": review_res,
            "cli_summary": cli
        },
        "errors": [],
        "warnings": budget_res.get("warnings", []) if isinstance(budget_res, dict) else [],
        "metrics": {
            "enabled_after": int(bool(_load_cfg(cfg_path).get("enabled", True))),
            "auto_disabled": int(not bool(_load_cfg(cfg_path).get("enabled", True)) and bool(auto.get("enabled", False)))
        }
    }
