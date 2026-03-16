#!/usr/bin/env python3
"""tutorial_write

Deterministic tutorial renderer + writer.

Supports two modes:
1) Provide `inputs.tutorial_spec` (structured) → tool renders Markdown.
2) Provide `inputs.content` (already-rendered Markdown) → tool validates sections.

Then it writes via the same safety rules as doc_write (no path traversal) and
returns a unified diff.
"""

from __future__ import annotations

import re
from pathlib import Path

from doc_write import run as doc_write_run


REQUIRED_SECTIONS = [
    "Prerequisites",
    "Quickstart",
    "Walkthrough",
    "Verification",
    "Troubleshooting",
    "Next Steps",
]


def _render_from_spec(spec: dict) -> str:
    title = (spec.get("title") or "Tutorial").strip()
    audience = (spec.get("audience") or "").strip()
    goal = (spec.get("goal") or "").strip()
    prereq = spec.get("prerequisites") or []
    quick = spec.get("quickstart") or []
    steps = spec.get("steps") or []
    verify = spec.get("verification") or []
    trouble = spec.get("troubleshooting") or []
    nexts = spec.get("next_steps") or []

    def bullets(xs):
        return "\n".join([f"- {x}" for x in xs]) if xs else "- (fill)"

    def step_block(items):
        if not items:
            return "1. (fill)"
        out = []
        for i, s in enumerate(items, 1):
            if isinstance(s, str):
                out.append(f"{i}. {s}")
            elif isinstance(s, dict):
                st = (s.get("step") or s.get("title") or f"Step {i}").strip()
                action = (s.get("action") or "").strip()
                expected = (s.get("expected") or "").strip()
                out.append(f"{i}. **{st}**")
                if action:
                    out.append(f"   - Action: {action}")
                if expected:
                    out.append(f"   - Expected: {expected}")
            else:
                out.append(f"{i}. (fill)")
        return "\n".join(out)

    header = [f"# {title}"]
    if audience:
        header.append(f"**Audience:** {audience}")
    if goal:
        header.append(f"**Goal:** {goal}")
    header.append("")

    md = "\n".join(header)
    md += "## Prerequisites\n" + bullets(prereq) + "\n\n"
    md += "## Quickstart\n" + step_block(quick) + "\n\n"
    md += "## Walkthrough\n" + step_block(steps) + "\n\n"
    md += "## Verification\n" + step_block(verify) + "\n\n"
    md += "## Troubleshooting\n" + bullets(trouble) + "\n\n"
    md += "## Next Steps\n" + bullets(nexts) + "\n"
    return md


def _missing_sections(md: str) -> list[str]:
    present = set()
    for m in re.finditer(r"^##\s+(.+)$", md, flags=re.M):
        present.add(m.group(1).strip())
    return [s for s in REQUIRED_SECTIONS if s not in present]


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    project_root = inputs.get("project_root", ".")

    tutorial_spec = inputs.get("tutorial_spec")
    content = inputs.get("content")
    if tutorial_spec and isinstance(tutorial_spec, dict):
        content = _render_from_spec(tutorial_spec)

    if not isinstance(content, str) or not content.strip():
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": req.get("skill_id", "tutorial_write"),
            "status": "fail",
            "outputs": {},
            "metrics": {},
            "errors": ["Provide inputs.tutorial_spec (object) or inputs.content (non-empty markdown string)"],
            "warnings": [],
        }

    path = inputs.get("path")
    if not isinstance(path, str) or not path.strip():
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": req.get("skill_id", "tutorial_write"),
            "status": "fail",
            "outputs": {},
            "metrics": {},
            "errors": ["Provide inputs.path (relative file path)"],
            "warnings": [],
        }

    missing = _missing_sections(content)
    warnings = []
    if missing:
        warnings.append("Missing tutorial sections: " + ", ".join(missing))

    # Write via doc_write (reuse diff + safety)
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
    out = dict(res.get("outputs", {}))
    out.update({"missing_sections": missing, "required_sections": REQUIRED_SECTIONS})

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "tutorial_write"),
        "status": status,
        "outputs": out,
        "metrics": dict(res.get("metrics", {})),
        "errors": res.get("errors", []) if status == "fail" else [],
        "warnings": (res.get("warnings", []) or []) + warnings,
    }
