#!/usr/bin/env python3
"""screencast_script

Deterministic screencast script renderer + writer.

Purpose:
- Produce **video-ready** scripts (chapters, on-screen actions, narration cues)
- Store them as Markdown for iteration and review.

This skill renders from `inputs.script_spec` (structured) or accepts raw
`inputs.content` markdown.
"""

from __future__ import annotations

import datetime
from doc_write import run as doc_write_run


def _render(spec: dict) -> str:
    title = (spec.get("title") or "Screencast").strip()
    goal = (spec.get("goal") or "").strip()
    audience = (spec.get("audience") or "").strip()
    duration = spec.get("duration") or ""
    chapters = spec.get("chapters") or []
    notes = spec.get("notes") or ""

    lines = [f"# {title}", ""]
    meta = []
    if audience:
        meta.append(f"**Audience:** {audience}")
    if goal:
        meta.append(f"**Goal:** {goal}")
    if duration:
        meta.append(f"**Duration:** {duration}")
    meta.append(f"**Generated:** {datetime.datetime.utcnow().isoformat()}Z")
    lines += meta + [""]

    lines.append("## Chapters")
    if not chapters:
        lines.append("- (fill)")
        lines.append("")
    else:
        for ch in chapters:
            if isinstance(ch, str):
                lines.append(f"- {ch}")
            elif isinstance(ch, dict):
                ts = ch.get("timestamp") or ""
                name = ch.get("title") or ch.get("chapter") or "Chapter"
                lines.append(f"- {ts} — {name}" if ts else f"- {name}")
        lines.append("")

    lines.append("## Shot List")
    lines.append("")
    lines.append("| Time | On screen | Narration |")
    lines.append("|---|---|---|")
    if not chapters:
        lines.append("| 00:00 | (fill) | (fill) |")
    else:
        for ch in chapters:
            if not isinstance(ch, dict):
                continue
            ts = ch.get("timestamp") or ""
            on_screen = (ch.get("on_screen") or "(fill)").replace("\n", " ")
            narration = (ch.get("narration") or "(fill)").replace("\n", " ")
            lines.append(f"| {ts} | {on_screen} | {narration} |")

    if notes:
        lines.append("")
        lines.append("## Notes")
        lines.append(notes)

    lines.append("")
    lines.append("## Checklist")
    lines.append("- [ ] No private keys/secrets on screen")
    lines.append("- [ ] Commands are copy-pasteable")
    lines.append("- [ ] Expected outputs are shown")
    lines.append("- [ ] Troubleshooting mention (if relevant)")

    return "\n".join(lines).rstrip() + "\n"


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    project_root = inputs.get("project_root", ".")
    path = inputs.get("path")
    if not isinstance(path, str) or not path.strip():
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": req.get("skill_id", "screencast_script"),
            "status": "fail",
            "outputs": {},
            "metrics": {},
            "errors": ["Provide inputs.path"],
            "warnings": [],
        }

    content = inputs.get("content")
    spec = inputs.get("script_spec")
    if isinstance(spec, dict):
        content = _render(spec)
    if not isinstance(content, str) or not content.strip():
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": req.get("skill_id", "screencast_script"),
            "status": "fail",
            "outputs": {},
            "metrics": {},
            "errors": ["Provide inputs.script_spec (object) or inputs.content (markdown)"],
            "warnings": [],
        }

    res = doc_write_run({
        "type": "skill_request_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "doc_write",
        "inputs": {
            "project_root": project_root,
            "path": path,
            "content": content,
            "overwrite": bool(inputs.get("overwrite", True)),
            "dry_run": bool(inputs.get("dry_run", False)),
            "max_diff_chars": int(inputs.get("max_diff_chars", 50_000)),
        },
    })

    status = "ok" if res.get("status") == "ok" else "fail"
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "screencast_script"),
        "status": status,
        "outputs": res.get("outputs", {}),
        "metrics": res.get("metrics", {}),
        "errors": res.get("errors", []) if status == "fail" else [],
        "warnings": res.get("warnings", []),
    }
