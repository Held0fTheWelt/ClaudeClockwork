"""Phase 25 — Scoreboard generator (JSON + Markdown summary)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def generate_scoreboard(
    results: list[dict[str, Any]],
    project_root: Path | str | None = None,
    out_dir: Path | str | None = None,
) -> dict[str, Any]:
    """
    Generate scoreboard.json and scoreboard.md. Returns paths and summary.
    results: list of {name, status, duration_ms, quality_proxy?}
    """
    root = Path(project_root or Path.cwd()).resolve()
    run_root = root / ".clockwork_runtime"
    base = Path(out_dir or run_root / "eval")
    base.mkdir(parents=True, exist_ok=True)

    json_path = base / "scoreboard.json"
    md_path = base / "scoreboard.md"

    # Stable ordering
    ordered = sorted(results, key=lambda x: (x.get("name", ""), x.get("status", "")))
    payload = {"runs": ordered, "total": len(ordered), "pass_count": sum(1 for r in ordered if r.get("status") == "pass")}
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = ["# Eval Scoreboard", "", f"- Total: {payload['total']}", f"- Pass: {payload['pass_count']}", ""]
    for r in ordered:
        lines.append(f"- {r.get('name', '?')}: {r.get('status', '?')} ({r.get('duration_ms', 0)} ms)")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {"scoreboard_json": str(json_path), "scoreboard_md": str(md_path), "pass_count": payload["pass_count"]}
