#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from _report_publish import publish_files
from pathlib import Path
from typing import List, Tuple

DEFAULT_LIMITATIONS = [
    "This skill consolidates critic panels; it does not call LLMs.",
    "Scores are subjective; treat them as guidance.",
    "If a critic is missing, the overall view will be incomplete."
]

CRITICS = ["systemic","technical","legal","security","moral","creative","methodical"]

def _safe_float(x, default=0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default

def _ascii_bar(name: str, value: float, width: int = 30) -> str:
    v = max(0.0, min(10.0, value))
    filled = int((v/10.0)*width)
    return f"{name:<12} | {'█'*filled}{' '*(width-filled)} | {v:.1f}/10"

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
    panels_path = Path(inputs.get("panels_path","")).expanduser().resolve()
    output_dir = Path(inputs.get("output_dir",".claude-performance/reports")).resolve()
    export_prefix = str(inputs.get("export_prefix", f"critics_{run_id}"))
    print_cli = bool(inputs.get("print_cli", True))
    export_charts = bool(inputs.get("export_charts", True))

    if not panels_path.exists():
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),"skill_id":"critics_board_review",
                "status":"error","outputs":{},"errors":[f"panels_path missing: {panels_path}"],"warnings":[],
                "metrics":{}}

    panels = json.loads(panels_path.read_text(encoding="utf-8", errors="ignore"))
    # Collect scores
    scores = []
    confidences = []
    notes = {}
    recs = []
    missing = []
    for c in CRITICS:
        p = panels.get(c)
        if not isinstance(p, dict):
            missing.append(c)
            continue
        risk = _safe_float(p.get("risk_0_10", 0))
        conf = _safe_float(p.get("confidence_0_10", 0))
        scores.append((c, risk))
        confidences.append(conf)
        notes[c] = str(p.get("notes","")).strip()
        for r in (p.get("recommendations") or []):
            if r and isinstance(r, str):
                recs.append((c, r.strip(), risk))

    # Prioritize recs by critic risk (higher first)
    recs_sorted = sorted(recs, key=lambda x: x[2], reverse=True)
    top_recs = []
    seen = set()
    for c, r, risk in recs_sorted:
        key = r.lower()
        if key in seen:
            continue
        seen.add(key)
        top_recs.append({"critic": c, "recommendation": r, "risk": risk})
        if len(top_recs) >= 12:
            break

    overall_risk = sum(v for _, v in scores)/len(scores) if scores else 0.0
    avg_conf = sum(confidences)/len(confidences) if confidences else 0.0

    # Simple go/no-go: if security or legal >=8 => no-go unless mitigated
    go_no_go = "go"
    blockers = []
    for c, v in scores:
        if c in ("security","legal") and v >= 8.0:
            go_no_go = "no-go"
            blockers.append(f"{c} risk {v:.1f}/10")
    if overall_risk >= 7.5:
        go_no_go = "no-go"
        blockers.append(f"overall risk {overall_risk:.1f}/10")

    now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    ts_slug = now.replace(":","").replace("-","")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_json = output_dir / f"{export_prefix}_report.json"
    report_md = output_dir / f"{export_prefix}_report.md"

    charts = []
    if export_charts:
        chart_path = output_dir / "charts" / f"{export_prefix}_{ts_slug}_critics.png"
        _plot_scores(scores, f"Critics risk scores ({run_id})", chart_path)
        charts = [str(chart_path)]

    report = {
        "type":"critics_board_report",
        "generated_at": now,
        "run_id": run_id,
        "inputs":{
            "panels_path": str(panels_path),
            "output_dir": str(output_dir),
            "export_prefix": export_prefix
        },
        "scores": [{"critic": c, "risk_0_10": v} for c, v in scores],
        "overall_risk_0_10": overall_risk,
        "avg_confidence_0_10": avg_conf,
        "go_no_go": go_no_go,
        "blockers": blockers,
        "top_recommendations": top_recs,
        "notes": notes,
        "artifacts":{
            "report_json": str(report_json),
            "report_md": str(report_md),
            "charts": charts
        },
        "limitations": DEFAULT_LIMITATIONS,
        "missing_critics": missing
    }

    report_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    md = []
    md.append(f"# Critics Board Report — {run_id}")
    md.append(f"- Generated: `{now}`")
    md.append(f"- Go/No-Go: **{go_no_go}**")
    if blockers:
        md.append("- Blockers:")
        for b in blockers:
            md.append(f"  - {b}")
    md.append("")
    md.append("## Scores")
    md.append("| Critic | Risk (0-10) |")
    md.append("|---|---:|")
    for c, v in scores:
        md.append(f"| `{c}` | {v:.1f} |")
    md.append("")
    md.append(f"**Overall risk:** {overall_risk:.1f}/10  | **Avg confidence:** {avg_conf:.1f}/10")
    md.append("")
    md.append("## Top recommendations")
    for r in top_recs:
        md.append(f"- **{r['critic']}** (risk {r['risk']:.1f}): {r['recommendation']}")
    md.append("")
    md.append("## Notes")
    for c, note in notes.items():
        md.append(f"### {c}")
        md.append(note if note else "(n/a)")
        md.append("")
    if missing:
        md.append("## Missing critics")
        md.append(", ".join(missing))
        md.append("")
    if charts:
        md.append("## Charts")
        for c in charts:
            md.append(f"- `{c}`")
        md.append("")
    md.append("## Limitations")
    for lim in DEFAULT_LIMITATIONS:
        md.append(f"- {lim}")
    report_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    cli = []
    if print_cli:
        cli.append(f"== Critics Board: {run_id} ==")
        cli.append(f"Go/No-Go: {go_no_go}")
        if blockers:
            cli.append("Blockers:")
            for b in blockers:
                cli.append(f"- {b}")
        cli.append("")
        for c, v in scores:
            cli.append(_ascii_bar(c, v))
        cli.append("")
        cli.append("Top recs:")
        for r in top_recs[:6]:
            cli.append(f"- {r['critic']}: {r['recommendation']}")
        if missing:
            cli.append("")
            cli.append("Missing critics: " + ", ".join(missing))

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"critics_board_review",
        "status":"ok",
        "outputs":{
            "report": report,
            "cli_summary": "\n".join(cli) + ("\n" if cli else ""),
            "published": published
        },
        "errors": [],
        "warnings": [],
        "metrics":{
            "critics_present": len(scores),
            "overall_risk": overall_risk
        }
    }
