#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from _report_publish import publish_files
from pathlib import Path
from typing import Any, Dict, List, Tuple

DEFAULT_LIMITATIONS = [
    "Panel notes are provided by LLM roles externally (this skill does not call LLMs).",
    "Scores are subjective; treat them as guidance.",
    "If the panel JSON is incomplete, the report will be partial."
]

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))

def _safe_float(x, default=0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default

def _ascii_bar(name: str, value: float, width: int = 30) -> str:
    # value 0..10
    v = max(0.0, min(10.0, value))
    filled = int((v/10.0)*width)
    return f"{name:<14} | {'█'*filled}{' '*(width-filled)} | {v:.1f}/10"

def _plot_scores(scores: List[Tuple[str,float]], title: str, out_path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labels = [k for k,_ in scores]
    values = [v for _,v in scores]
    plt.figure()
    plt.bar(range(len(values)), values)
    plt.xticks(range(len(labels)), labels, rotation=45, ha="right")
    plt.ylim(0,10)
    plt.title(title)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    run_id = str(inputs.get("run_id","run-unknown"))
    budget_report_path = Path(inputs.get("budget_report_path","")).expanduser().resolve()
    panels_path = Path(inputs.get("panels_path","")).expanduser().resolve()
    output_dir = Path(inputs.get("output_dir",".claude-performance/reports")).resolve()
    export_prefix = str(inputs.get("export_prefix", f"review_{run_id}"))
    print_cli = bool(inputs.get("print_cli", True))
    export_charts = bool(inputs.get("export_charts", True))

    warnings = []
    if not budget_report_path.exists():
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),"skill_id":"efficiency_review",
                "status":"error","outputs":{},"errors":[f"budget_report_path missing: {budget_report_path}"],"warnings":[],
                "metrics":{}}
    if not panels_path.exists():
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),"skill_id":"efficiency_review",
                "status":"error","outputs":{},"errors":[f"panels_path missing: {panels_path}"],"warnings":[],
                "metrics":{}}

    budget = _load_json(budget_report_path)
    panels = _load_json(panels_path)

    worker_oodle = panels.get("worker_oodle", {})
    worker_deepseek = panels.get("worker_deepseek", {})
    teamlead = panels.get("teamlead", {})
    judge_oodle = panels.get("judge_oodle", {})

    effort_w1 = _safe_float(worker_oodle.get("effort_0_10", 0))
    effec_w1 = _safe_float(worker_oodle.get("effectiveness_0_10", 0))
    effort_w2 = _safe_float(worker_deepseek.get("effort_0_10", 0))
    effec_w2 = _safe_float(worker_deepseek.get("effectiveness_0_10", 0))
    lead_effort = _safe_float(teamlead.get("expected_effort_0_10", 0))
    quality = _safe_float(judge_oodle.get("quality_0_10", 0))

    # Combine estimates (simple, transparent)
    effort_est = (effort_w1 + effort_w2) / 2.0 if (effort_w1 or effort_w2) else 0.0
    effec_est = (effec_w1 + effec_w2) / 2.0 if (effec_w1 or effec_w2) else 0.0
    qual_est = quality

    could_be_better = bool(judge_oodle.get("could_be_better", False))
    how = str(judge_oodle.get("how","")).strip()

    total_tokens = budget.get("totals", {}).get("total_tokens", 0)
    top_role = None
    try:
        br = budget.get("breakdowns", {}).get("by_role", [])
        if br:
            top_role = max(br, key=lambda x: x.get("total_tokens",0)).get("key")
    except Exception:
        top_role = None

    summary = []
    summary.append(f"Total tokens: {total_tokens}")
    if top_role:
        summary.append(f"Top cost driver (role): {top_role}")
    summary.append(f"Effort estimate (workers avg): {effort_est:.1f}/10")
    summary.append(f"Effectiveness estimate (workers avg): {effec_est:.1f}/10")
    summary.append(f"Quality (judge): {qual_est:.1f}/10")
    summary.append(f"TeamLead expected effort: {lead_effort:.1f}/10")
    if could_be_better:
        summary.append("Judge thinks it could be better. See 'how' for improvements.")

    now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    ts_slug = now.replace(":","").replace("-","")
    output_dir.mkdir(parents=True, exist_ok=True)

    review_json = output_dir / f"{export_prefix}_review.json"
    review_md = output_dir / f"{export_prefix}_review.md"

    charts = []
    if export_charts:
        charts_dir = output_dir / "charts"
        chart = charts_dir / f"{export_prefix}_{ts_slug}_scores.png"
        _plot_scores([("effort", effort_est), ("effectiveness", effec_est), ("quality", qual_est), ("lead_effort", lead_effort)],
                     f"Efficiency review scores ({run_id})", chart)
        charts = [str(chart)]

    report = {
        "type":"efficiency_review",
        "generated_at": now,
        "run_id": run_id,
        "inputs":{
            "budget_report_path": str(budget_report_path),
            "panels_path": str(panels_path),
            "output_dir": str(output_dir),
            "export_prefix": export_prefix
        },
        "panels":{
            "worker_oodle": worker_oodle,
            "worker_deepseek": worker_deepseek,
            "teamlead": teamlead,
            "judge_oodle": judge_oodle
        },
        "final_judgement":{
            "effort_estimate": effort_est,
            "effectiveness_estimate": effec_est,
            "quality_estimate": qual_est,
            "summary": " | ".join(summary)
        },
        "artifacts":{
            "review_json": str(review_json),
            "review_md": str(review_md),
            "charts": charts
        },
        "limitations": DEFAULT_LIMITATIONS
    }

    review_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    md = []
    md.append(f"# Efficiency Review — {run_id}")
    md.append(f"- Generated: `{now}`")
    md.append(f"- Budget report: `{budget_report_path}`")
    md.append(f"- Panels: `{panels_path}`")
    md.append("")
    md.append("## Final judgement")
    md.append(f"- Effort estimate: **{effort_est:.1f}/10**")
    md.append(f"- Effectiveness estimate: **{effec_est:.1f}/10**")
    md.append(f"- Quality estimate (judge): **{qual_est:.1f}/10**")
    md.append(f"- TeamLead expected effort: **{lead_effort:.1f}/10**")
    md.append("")
    md.append("## Judge: could it be better?")
    md.append(f"- Could be better: **{could_be_better}**")
    md.append(f"- How: {how if how else '(n/a)'}")
    md.append("")
    md.append("## Budget context")
    md.append(f"- Total tokens: **{total_tokens}**")
    if top_role:
        md.append(f"- Top cost driver (role): **{top_role}**")
    md.append("")
    md.append("## Panel notes")
    md.append("### Worker (Oodle)")
    md.append(worker_oodle.get("notes","(n/a)"))
    md.append("\n### Worker (DeepSeek)")
    md.append(worker_deepseek.get("notes","(n/a)"))
    md.append("\n### TeamLead")
    md.append(teamlead.get("notes","(n/a)"))
    md.append("\n### Judge (Oodle)")
    md.append(judge_oodle.get("how","(n/a)"))
    md.append("")
    if charts:
        md.append("## Charts")
        for c in charts:
            md.append(f"- `{c}`")
        md.append("")
    md.append("## Limitations")
    for lim in DEFAULT_LIMITATIONS:
        md.append(f"- {lim}")
    review_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    published = publish_files(run_id, "performance", [str(review_json), str(review_md)] + charts, "review")

    cli = []
    if print_cli:
        cli.append(f"== Efficiency Review: {run_id} ==")
        cli.append(f"Tokens: {total_tokens}")
        cli.append("")
        cli.append(_ascii_bar("effort", effort_est))
        cli.append(_ascii_bar("effectiveness", effec_est))
        cli.append(_ascii_bar("quality", qual_est))
        cli.append(_ascii_bar("lead_effort", lead_effort))
        if could_be_better:
            cli.append("")
            cli.append("Judge: could be better -> see review_md for 'how'.")

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"efficiency_review",
        "status":"ok",
        "outputs":{
            "review": report,
            "cli_summary": "\n".join(cli) + ("\n" if cli else ""),
            "published": published
        },
        "errors": [],
        "warnings": warnings,
        "metrics":{
            "total_tokens": int(total_tokens),
            "effort_estimate": effort_est,
            "quality_estimate": qual_est
        }
    }
