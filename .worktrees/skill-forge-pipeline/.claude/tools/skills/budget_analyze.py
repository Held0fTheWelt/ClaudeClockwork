#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any
from _report_publish import publish_files

DEFAULT_LIMITATIONS = [
    "Requires token events to be logged (JSONL/JSON). Without logging, it cannot infer costs.",
    "Token costs depend on the model and on input vs output split; if you only log total_tokens, cost estimates will be coarse.",
    "Pricing snapshot is local and can drift; update `.claude/config/anthropic_pricing_snapshot.json` when pricing changes.",
    "Cache costs can only be estimated if cache token fields are logged."
]

def _read_jsonl(path: Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out

def _safe_int(x, default=0) -> int:
    try:
        return int(x)
    except Exception:
        return default

def _ascii_bar_int(name: str, value: int, max_value: int, width: int = 36) -> str:
    if max_value <= 0:
        max_value = 1
    filled = int((value / max_value) * width)
    filled = max(0, min(width, filled))
    return f"{name:<18} | {'█'*filled}{' '*(width-filled)} | {value}"

def _ascii_bar_usd(name: str, value: float, max_value: float, width: int = 36) -> str:
    if max_value <= 0:
        max_value = 1.0
    filled = int((value / max_value) * width)
    filled = max(0, min(width, filled))
    return f"{name:<18} | {'█'*filled}{' '*(width-filled)} | ${value:.4f}"

def _plot_bar(items: List[Tuple[str,float]], title: str, out_path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [k for k, _ in items]
    values = [v for _, v in items]
    plt.figure()
    plt.bar(range(len(values)), values)
    plt.xticks(range(len(labels)), labels, rotation=45, ha="right")
    plt.title(title)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()

def _load_pricing(pricing_path: Path) -> dict:
    try:
        return json.loads(pricing_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}

def _canonical_model(model: str, pricing: dict) -> str:
    aliases = pricing.get("aliases") or {}
    if model in aliases:
        return aliases[model]
    return model

def _estimate_cost_usd(model: str, input_tokens: int, output_tokens: int, pricing: dict) -> tuple[float, str]:
    """
    Returns (usd, note). If unknown model, usd=0 and note marks unknown.
    """
    model_id = _canonical_model(model, pricing)
    models = pricing.get("models") or {}
    info = models.get(model_id)
    if not info:
        return 0.0, f"unknown_model:{model}"
    inp_rate = float(info.get("base_input", info.get("input_usd_per_mtok", 0.0)))
    out_rate = float(info.get("output", info.get("output_usd_per_mtok", 0.0)))
    usd = (input_tokens / 1_000_000.0) * inp_rate + (output_tokens / 1_000_000.0) * out_rate
    return usd, ""


def _estimate_cost_range_usd(model: str, total_tokens: int, pricing: dict, assumed_output_ratio: float = 0.25) -> tuple[float, float, float, str]:
    """Return (min_usd, mid_usd, max_usd, note).
    - min: all tokens treated as base input
    - max: all tokens treated as output
    - mid: split using assumed_output_ratio (default 25% output)
    """
    model_id = _canonical_model(model, pricing)
    info = (pricing.get("models") or {}).get(model_id)
    if not info:
        return 0.0, 0.0, 0.0, f"unknown_model:{model}"
    inp = float(info.get("base_input", 0.0))
    out = float(info.get("output", 0.0))
    min_usd = (total_tokens/1_000_000.0) * inp
    max_usd = (total_tokens/1_000_000.0) * out
    out_tok = int(total_tokens * max(0.0, min(1.0, assumed_output_ratio)))
    in_tok = total_tokens - out_tok
    mid_usd = (in_tok/1_000_000.0)*inp + (out_tok/1_000_000.0)*out
    return min_usd, mid_usd, max_usd, "range_estimated"


def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    run_id = str(inputs.get("run_id", "run-unknown"))
    sources = list(inputs.get("events_sources", []))
    output_dir = Path(inputs.get("output_dir", ".claude-performance/reports")).resolve()
    export_prefix = str(inputs.get("export_prefix", f"budget_{run_id}"))
    top_n = int(inputs.get("top_n", 10))
    print_cli = bool(inputs.get("print_cli", True))
    export_charts = bool(inputs.get("export_charts", True))
    pricing_path = Path(inputs.get("pricing_path", ".claude/config/anthropic_pricing_snapshot.json")).resolve()

    warnings = []
    events: list[dict] = []

    for s in sources:
        p = Path(s).expanduser().resolve()
        if not p.exists():
            warnings.append(f"missing events source: {s}")
            continue
        if p.suffix.lower() == ".jsonl":
            events.extend(_read_jsonl(p))
        elif p.suffix.lower() == ".json":
            try:
                obj = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
                if isinstance(obj, list):
                    events.extend(obj)
                elif isinstance(obj, dict) and isinstance(obj.get("events"), list):
                    events.extend(obj["events"])
            except Exception:
                warnings.append(f"failed to parse json: {s}")
        else:
            warnings.append(f"unsupported source format: {s}")

    pricing = _load_pricing(pricing_path)
    if not pricing:
        warnings.append(f"pricing snapshot missing/unreadable: {pricing_path} (cost estimates disabled)")

    norm = []
    unknown_models = set()

    for e in events:
        rid = str(e.get("run_id", "")) or run_id
        if rid != run_id:
            continue
        role = str(e.get("role", "unknown"))
        model = str(e.get("model", "unknown"))
        task = str(e.get("task", "unknown"))
        phase = str(e.get("phase", ""))

        pt = _safe_int(e.get("prompt_tokens", e.get("input_tokens", 0)))
        ct = _safe_int(e.get("completion_tokens", e.get("output_tokens", 0)))
        tt = _safe_int(e.get("total_tokens", e.get("tokens", pt + ct)))

        # estimated cost: prefer explicit cents if present (e.g., from analytics)
        explicit_cents = e.get("estimated_cost_cents")
        cost_usd = 0.0
        cost_note = ""
        if explicit_cents is not None:
            try:
                cost_usd = float(explicit_cents) / 100.0
                cost_note = "explicit_cost"
            except Exception:
                cost_usd, cost_note = _estimate_cost_usd(model, pt, ct, pricing) if pricing else (0.0, "no_pricing")
        else:
            cost_usd, cost_note = _estimate_cost_usd(model, pt, ct, pricing) if pricing else (0.0, "no_pricing")

        if cost_note.startswith("unknown_model"):
            unknown_models.add(model)

        # If we only have total tokens (no prompt/output split), estimate a cost range
        if (pt == 0 and ct == 0) and tt > 0 and pricing:
            mn, mid, mx, noteR = _estimate_cost_range_usd(model, tt, pricing, assumed_output_ratio=float(inputs.get("assumed_output_ratio", 0.25)))
            cost_usd = mid if cost_usd == 0.0 else cost_usd
            # attach range (mid used as headline)
            range_min, range_mid, range_max = mn, mid, mx
            if noteR:
                cost_note = (cost_note + "|" if cost_note else "") + noteR
        else:
            range_min = range_mid = range_max = 0.0

        norm.append({
            "ts": str(e.get("ts", "")),
            "run_id": rid,
            "role": role,
            "model": model,
            "task": task,
            "phase": phase,
            "prompt_tokens": pt,
            "completion_tokens": ct,
            "total_tokens": tt,
            "estimated_cost_usd": cost_usd,
            "estimated_cost_usd_min": float(range_min),
            "estimated_cost_usd_mid": float(range_mid),
            "estimated_cost_usd_max": float(range_max),
            "cost_note": cost_note,
            "notes": str(e.get("notes", "")),
        })

    total_tokens = sum(x["total_tokens"] for x in norm)
    prompt_tokens = sum(x["prompt_tokens"] for x in norm)
    completion_tokens = sum(x["completion_tokens"] for x in norm)
    total_cost_usd = sum(x["estimated_cost_usd"] for x in norm)

    by_role_t = defaultdict(int)
    by_model_t = defaultdict(int)
    by_task_t = defaultdict(int)

    by_role_c = defaultdict(float)
    by_model_c = defaultdict(float)
    by_task_c = defaultdict(float)

    for e in norm:
        by_role_t[e["role"]] += e["total_tokens"]
        by_model_t[e["model"]] += e["total_tokens"]
        by_task_t[e["task"]] += e["total_tokens"]
        by_role_c[e["role"]] += e["estimated_cost_usd"]
        by_model_c[e["model"]] += e["estimated_cost_usd"]
        by_task_c[e["task"]] += e["estimated_cost_usd"]

    def top_items_int(d):
        items = sorted(d.items(), key=lambda x: x[1], reverse=True)
        return items[:top_n], items

    def top_items_float(d):
        items = sorted(d.items(), key=lambda x: x[1], reverse=True)
        return items[:top_n], items

    top_role_t, all_role_t = top_items_int(by_role_t)
    top_model_t, all_model_t = top_items_int(by_model_t)
    top_task_t, all_task_t = top_items_int(by_task_t)

    top_role_c, all_role_c = top_items_float(by_role_c)
    top_model_c, all_model_c = top_items_float(by_model_c)
    top_task_c, all_task_c = top_items_float(by_task_c)

    def to_breakdown_int(items):
        return [{"key": k, "total_tokens": v} for k, v in items]

    def to_breakdown_cost(items):
        return [{"key": k, "estimated_cost_usd": float(v)} for k, v in items]

    insights = []
    if total_tokens > 0:
        max_role = max(all_role_t, key=lambda x: x[1], default=("n/a", 0))
        max_model = max(all_model_t, key=lambda x: x[1], default=("n/a", 0))
        max_task = max(all_task_t, key=lambda x: x[1], default=("n/a", 0))
        insights.append(f"Top tokens by role: {max_role[0]} ({max_role[1]}).")
        insights.append(f"Top tokens by model: {max_model[0]} ({max_model[1]}).")
        insights.append(f"Top tokens by task: {max_task[0]} ({max_task[1]}).")
        if total_cost_usd > 0:
            max_role_c = max(all_role_c, key=lambda x: x[1], default=("n/a", 0.0))
            max_model_c = max(all_model_c, key=lambda x: x[1], default=("n/a", 0.0))
            insights.append(f"Top cost by role: {max_role_c[0]} (${max_role_c[1]:.4f}).")
            insights.append(f"Top cost by model: {max_model_c[0]} (${max_model_c[1]:.4f}).")
    else:
        insights.append("No events found for this run_id. Ensure token logging is enabled and sources are correct.")

    if unknown_models:
        warnings.append("unknown models for cost estimation: " + ", ".join(sorted(list(unknown_models)))[:300])

    now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    ts_slug = now.replace(":", "").replace("-", "")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write both stable and timestamped files (for history)
    report_json = output_dir / f"{export_prefix}_report.json"
    report_json_ts = output_dir / f"{export_prefix}_report_{ts_slug}.json"
    report_md = output_dir / f"{export_prefix}_report.md"
    report_md_ts = output_dir / f"{export_prefix}_report_{ts_slug}.md"

    charts = []
    if export_charts:
        charts_dir = output_dir / "charts"
        # tokens charts
        chart_role_t = charts_dir / f"{export_prefix}_{ts_slug}_tokens_by_role.png"
        chart_model_t = charts_dir / f"{export_prefix}_{ts_slug}_tokens_by_model.png"
        chart_task_t = charts_dir / f"{export_prefix}_{ts_slug}_tokens_by_task.png"
        _plot_bar([(k, float(v)) for k, v in top_role_t], f"Tokens by role ({run_id})", chart_role_t)
        _plot_bar([(k, float(v)) for k, v in top_model_t], f"Tokens by model ({run_id})", chart_model_t)
        _plot_bar([(k, float(v)) for k, v in top_task_t], f"Tokens by task ({run_id})", chart_task_t)
        charts.extend([str(chart_role_t), str(chart_model_t), str(chart_task_t)])
        # cost charts
        chart_role_c = charts_dir / f"{export_prefix}_{ts_slug}_cost_by_role.png"
        chart_model_c = charts_dir / f"{export_prefix}_{ts_slug}_cost_by_model.png"
        chart_task_c = charts_dir / f"{export_prefix}_{ts_slug}_cost_by_task.png"
        _plot_bar(top_role_c, f"Estimated cost by role ({run_id})", chart_role_c)
        _plot_bar(top_model_c, f"Estimated cost by model ({run_id})", chart_model_c)
        _plot_bar(top_task_c, f"Estimated cost by task ({run_id})", chart_task_c)
        charts.extend([str(chart_role_c), str(chart_model_c), str(chart_task_c)])

    cli_lines = []
    if print_cli:
        cli_lines.append(f"== Budget Report: {run_id} ==")
        cli_lines.append(f"Events: {len(norm)} | Tokens: total={total_tokens} prompt={prompt_tokens} completion={completion_tokens}")
        min_cost = float(sum(x.get("estimated_cost_usd_min",0.0) for x in norm))
        max_cost = float(sum(x.get("estimated_cost_usd_max",0.0) for x in norm))
        if max_cost > 0 and max_cost != min_cost:
            cli_lines.append(f"Estimated cost: ${total_cost_usd:.4f} (range: ${min_cost:.4f}–${max_cost:.4f}) (pricing snapshot: {pricing_path.name})")
        else:
            cli_lines.append(f"Estimated cost: ${total_cost_usd:.4f} (pricing snapshot: {pricing_path.name})")
        cli_lines.append("")
        cli_lines.append("-- Tokens by role (top) --")
        mr = max([v for _, v in top_role_t], default=1)
        for k, v in top_role_t:
            cli_lines.append(_ascii_bar_int(k[:18], v, mr))
        cli_lines.append("")
        cli_lines.append("-- Cost by role (top) --")
        mrc = max([v for _, v in top_role_c], default=1.0)
        for k, v in top_role_c:
            cli_lines.append(_ascii_bar_usd(k[:18], v, mrc))
        cli_lines.append("")
        cli_lines.append("-- Tokens by model (top) --")
        mm = max([v for _, v in top_model_t], default=1)
        for k, v in top_model_t:
            cli_lines.append(_ascii_bar_int(k[:18], v, mm))
        cli_lines.append("")
        cli_lines.append("-- Cost by model (top) --")
        mmc = max([v for _, v in top_model_c], default=1.0)
        for k, v in top_model_c:
            cli_lines.append(_ascii_bar_usd(k[:18], v, mmc))
        cli_lines.append("")
        cli_lines.append("-- Insights --")
        for ins in insights:
            cli_lines.append(f"- {ins}")
        if unknown_models:
            cli_lines.append(f"- WARNING: unknown models for cost estimate: {', '.join(sorted(list(unknown_models)))}")

    report = {
        "type": "budget_report",
        "generated_at": now,
        "run_id": run_id,
        "inputs": {
            "events_sources": sources,
            "output_dir": str(output_dir),
            "export_prefix": export_prefix,
            "top_n": top_n,
            "pricing_path": str(pricing_path),
        },
        "totals": {
            "events": len(norm),
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "estimated_cost_usd": float(total_cost_usd),
            "estimated_cost_usd_min": float(sum(x.get("estimated_cost_usd_min",0.0) for x in norm)),
            "estimated_cost_usd_max": float(sum(x.get("estimated_cost_usd_max",0.0) for x in norm)),
        },
        "breakdowns": {
            "by_role": to_breakdown_int(sorted(by_role_t.items(), key=lambda x: x[1], reverse=True)),
            "by_model": to_breakdown_int(sorted(by_model_t.items(), key=lambda x: x[1], reverse=True)),
            "by_task": to_breakdown_int(sorted(by_task_t.items(), key=lambda x: x[1], reverse=True)),
            "cost_by_role": to_breakdown_cost(sorted(by_role_c.items(), key=lambda x: x[1], reverse=True)),
            "cost_by_model": to_breakdown_cost(sorted(by_model_c.items(), key=lambda x: x[1], reverse=True)),
            "cost_by_task": to_breakdown_cost(sorted(by_task_c.items(), key=lambda x: x[1], reverse=True)),
        },
        "insights": insights,
        "artifacts": {
            "report_json": str(report_json),
            "report_md": str(report_md),
            "report_json_timestamped": str(report_json_ts),
            "report_md_timestamped": str(report_md_ts),
            "charts": charts,
        },
        "limitations": DEFAULT_LIMITATIONS,
    }

    # Write reports (stable + stamped)
    content_json = json.dumps(report, indent=2, ensure_ascii=False)
    report_json.write_text(content_json, encoding="utf-8")
    report_json_ts.write_text(content_json, encoding="utf-8")

    md = []
    md.append(f"# Budget Report — {run_id}")
    md.append(f"- Generated: `{now}`")
    md.append(f"- Events: **{len(norm)}**")
    md.append(f"- Tokens: total **{total_tokens}**, prompt **{prompt_tokens}**, completion **{completion_tokens}**")
    md.append(f"- Estimated cost: **${total_cost_usd:.4f}** (pricing: `{pricing_path}`)")
    md.append("")
    md.append("## Insights")
    for ins in insights:
        md.append(f"- {ins}")
    md.append("")
    def add_table(title, rows, value_label="Tokens"):
        md.append(f"## {title}")
        md.append(f"| Key | {value_label} |")
        md.append("|---|---:|")
        for k, v in rows[:top_n]:
            if value_label.lower().startswith("usd"):
                md.append(f"| `{k}` | ${float(v):.4f} |")
            else:
                md.append(f"| `{k}` | {int(v)} |")
        md.append("")
    add_table("Tokens by role (top)", sorted(by_role_t.items(), key=lambda x: x[1], reverse=True), "Tokens")
    add_table("Estimated cost by role (top)", sorted(by_role_c.items(), key=lambda x: x[1], reverse=True), "USD")
    add_table("Tokens by model (top)", sorted(by_model_t.items(), key=lambda x: x[1], reverse=True), "Tokens")
    add_table("Estimated cost by model (top)", sorted(by_model_c.items(), key=lambda x: x[1], reverse=True), "USD")
    add_table("Tokens by task (top)", sorted(by_task_t.items(), key=lambda x: x[1], reverse=True), "Tokens")
    add_table("Estimated cost by task (top)", sorted(by_task_c.items(), key=lambda x: x[1], reverse=True), "USD")
    if charts:
        md.append("## Charts")
        for c in charts:
            md.append(f"- `{c}`")
        md.append("")
    md.append("## Limitations")
    for lim in DEFAULT_LIMITATIONS:
        md.append(f"- {lim}")

    md_text = "\n".join(md) + "\n"
    report_md.write_text(md_text, encoding="utf-8")
    report_md_ts.write_text(md_text, encoding="utf-8")

    published = publish_files(run_id, "performance", [str(report_json), str(report_md), str(report_json_ts), str(report_md_ts)] + charts, "budget")

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "budget_analyze",
        "status": "ok",
        "outputs": {
            "report": report,
            "cli_summary": "\n".join(cli_lines) + ("\n" if cli_lines else ""),
            "published": published,
        },
        "errors": [],
        "warnings": warnings,
        "metrics": {
            "events": len(norm),
            "total_tokens": total_tokens,
            "estimated_cost_usd": float(total_cost_usd),
            "estimated_cost_usd_min": float(sum(x.get("estimated_cost_usd_min",0.0) for x in norm)),
            "estimated_cost_usd_max": float(sum(x.get("estimated_cost_usd_max",0.0) for x in norm)),
        },
    }
