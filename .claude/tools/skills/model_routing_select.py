#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

def _load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return default

def _canonical_model(model: str, pricing: dict) -> str:
    aliases = pricing.get("aliases") or {}
    return aliases.get(model, model)

def _cost_range(model: str, total_tokens: int, pricing: dict, assumed_output_ratio: float = 0.25):
    mid_note = ""
    model_id = _canonical_model(model, pricing)
    info = (pricing.get("models") or {}).get(model_id)
    if not info:
        return [0.0, 0.0, 0.0], "unknown_model"
    inp = float(info.get("base_input", 0.0))
    out = float(info.get("output", 0.0))
    mn = (total_tokens/1_000_000.0) * inp
    mx = (total_tokens/1_000_000.0) * out
    out_tok = int(total_tokens * max(0.0, min(1.0, assumed_output_ratio)))
    in_tok = total_tokens - out_tok
    mid = (in_tok/1_000_000.0)*inp + (out_tok/1_000_000.0)*out
    return [float(mn), float(mid), float(mx)], ""

def _success_rate(stats: dict, model: str, task_type: str):
    m = stats.get("models", {}).get(model, {})
    t = m.get("task_types", {}).get(task_type, {})
    attempts = int(t.get("attempts", 0))
    successes = int(t.get("successes", 0))
    if attempts <= 0:
        return 0.0, 0
    return successes / max(1, attempts), attempts

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    run_id = str(inputs.get("run_id","run-unknown"))
    task = str(inputs.get("task","unknown"))
    scope_path = Path(inputs.get("scope_report_path","")).resolve()
    routing_cfg_path = Path(inputs.get("routing_config_path",".claude/config/model_routing.yaml")).resolve()
    pricing_path = Path(inputs.get("pricing_path",".claude/config/anthropic_pricing_snapshot.json")).resolve()
    stats_path = Path(inputs.get("stats_path",".clockwork_runtime/brain/model_routing_stats.json")).resolve()

    if not scope_path.exists():
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),"skill_id":"model_routing_select",
                "status":"error","outputs":{},"errors":[f"missing scope_report_path: {scope_path}"],"warnings":[],
                "metrics":{}}

    scope = _load_json(scope_path, {})
    tier = scope.get("tier","low")
    task_type = scope.get("task_type","general")

    cfg = _load_json(routing_cfg_path, {"enabled": True, "default_tiers": {}})
    pricing = _load_json(pricing_path, {})
    stats = _load_json(stats_path, {"models":{}})

    if not bool(cfg.get("enabled", True)):
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),"skill_id":"model_routing_select",
                "status":"ok","outputs":{"skipped":True,"reason":"routing disabled"}, "errors":[], "warnings":[], "metrics":{}}

    candidates = (cfg.get("default_tiers") or {}).get(tier, [])
    assumed_out = float((cfg.get("assess") or {}).get("assumed_output_ratio_for_cost_range", 0.25))

    # If we have no token estimate yet, use a simple proxy based on complexity score
    score = float(scope.get("complexity_score_0_10", 0.0))
    token_proxy = int(15_000 + score*20_000)  # 15k..215k proxy

    # compute cost + filter by success rate rules
    min_sr = float((cfg.get("rules") or {}).get("min_success_rate", 0.55))
    min_trials = int((cfg.get("rules") or {}).get("min_trials_for_trust", 8))

    scored = []
    notes = []
    for m in candidates:
        cr, note = _cost_range(m, token_proxy, pricing, assumed_out)
        sr, trials = _success_rate(stats, m, task_type)
        trust = (trials >= min_trials)
        scored.append({
            "model": m,
            "cost_range": cr,
            "success_rate": sr,
            "trials": trials,
            "trusted": trust
        })

    # sort by (trusted? and sr>=min) then by mid cost
    def key(x):
        good = (x["trusted"] and x["success_rate"] >= min_sr)
        return (0 if good else 1, x["cost_range"][1], -x["success_rate"])
    scored.sort(key=key)

    decision = scored[0] if scored else {"model":"unknown","cost_range":[0,0,0],"success_rate":0,"trials":0,"trusted":False}
    reason = f"tier={tier}; pick cheapest meeting trust/success if available; proxy_tokens={token_proxy}"
    if decision.get("trusted") and decision.get("success_rate",0) >= min_sr:
        reason += f"; trusted_sr={decision['success_rate']:.2f} ({decision['trials']} trials)"
    else:
        reason += "; insufficient trusted history -> cheapest fallback within tier"

    report = {
        "type":"model_routing_report",
        "generated_at": datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
        "run_id": run_id,
        "task": task,
        "scope": scope,
        "decision":{
            "model": decision["model"],
            "tier": tier,
            "reason": reason,
            "expected_cost_range_usd": decision["cost_range"]
        },
        "alternatives":[{"model": x["model"], "expected_cost_range_usd": x["cost_range"],
                        "notes": f"sr={x['success_rate']:.2f} trials={x['trials']} trusted={x['trusted']}"} for x in scored[1:6]],
        "stats_snapshot": {"task_type": task_type, "rules": cfg.get("rules", {}), "candidates": scored},
        "notes": notes
    }

    out_dir = Path(".report")/"routing"/run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir/f"model_routing_report_{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    out_md = out_dir/out_json.with_suffix(".md").name

    Path(out_json).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    # simple md
    md = []
    md.append(f"# Model Routing Report — {run_id}")
    md.append(f"- Tier: **{tier}**  | Task type: `{task_type}`")
    md.append(f"- Decision: **{decision['model']}**")
    md.append(f"- Expected cost range (USD): {decision['cost_range'][0]:.4f}–{decision['cost_range'][2]:.4f} (mid {decision['cost_range'][1]:.4f})")
    md.append(f"- Reason: {reason}")
    md.append("")
    md.append("## Alternatives (top)")
    for a in report["alternatives"]:
        r = a["expected_cost_range_usd"]
        md.append(f"- `{a['model']}` — ${r[0]:.4f}–${r[2]:.4f} (mid ${r[1]:.4f}) — {a.get('notes','')}")
    (out_dir/out_md).write_text("\n".join(md) + "\n", encoding="utf-8")

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"model_routing_select",
        "status":"ok",
        "outputs":{
            "report": report,
            "report_json_path": str(out_json),
            "report_md_path": str(out_dir/out_md)
        },
        "errors": [],
        "warnings": [],
        "metrics":{
            "selected_model": decision["model"]
        }
    }
