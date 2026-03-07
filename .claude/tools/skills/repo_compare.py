#!/usr/bin/env python3
"""repo_compare

Deterministic repository/folder comparison.

Primary use:
- Compare Claude Code vs Llama Code setups (policies, skills, tasks, runtime roots)

This tool compares two directory trees and reports:
- added/removed files
- changed files (sha256)
- size deltas

It can also emit a Markdown report into `.clockwork_runtime/knowledge/writes/compare_reports/`.
"""

from __future__ import annotations

import datetime
import hashlib
import os
from pathlib import Path
from typing import Iterable


TEXT_EXTS = {".md", ".markdown", ".txt", ".json", ".yaml", ".yml", ".toml", ".ini", ".py", ".js", ".ts", ".sh"}


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_files(root: Path, exclude: list[str]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(rel.startswith(x) for x in exclude):
            continue
        out[rel] = p
    return out


def _write_report(path: Path, lines: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    project_root = Path(inputs.get("project_root", ".")).resolve()

    left_root = Path(inputs.get("left_root", ".")).resolve()
    right_root = Path(inputs.get("right_root", ".")).resolve()

    if not left_root.exists() or not right_root.exists():
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": req.get("skill_id", "repo_compare"),
            "status": "fail",
            "outputs": {},
            "metrics": {},
            "errors": ["left_root/right_root must exist"],
            "warnings": [],
        }

    exclude = inputs.get("exclude_prefixes") or [".git/", ".pytest_cache/", "__pycache__/", ".venv/"]
    if not isinstance(exclude, list):
        exclude = [".git/", ".pytest_cache/", "__pycache__/", ".venv/"]

    left_files = _iter_files(left_root, exclude)
    right_files = _iter_files(right_root, exclude)

    left_set = set(left_files.keys())
    right_set = set(right_files.keys())

    added = sorted(list(right_set - left_set))
    removed = sorted(list(left_set - right_set))

    changed = []
    same = 0
    bytes_left = 0
    bytes_right = 0

    # Compare intersection
    for rel in sorted(list(left_set & right_set)):
        lp = left_files[rel]
        rp = right_files[rel]
        try:
            ls = lp.stat().st_size
            rs = rp.stat().st_size
            bytes_left += ls
            bytes_right += rs
        except Exception:
            pass
        try:
            lh = _sha256_file(lp)
            rh = _sha256_file(rp)
        except Exception:
            continue
        if lh != rh:
            changed.append({
                "path": rel,
                "sha256_left": lh,
                "sha256_right": rh,
                "size_left": lp.stat().st_size if lp.exists() else 0,
                "size_right": rp.stat().st_size if rp.exists() else 0,
            })
        else:
            same += 1

    # Report output
    write_report = bool(inputs.get("write_report", True))
    report_path = inputs.get("report_path")
    if not isinstance(report_path, str) or not report_path.strip():
        ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = f".clockwork_runtime/knowledge/writes/compare_reports/repo_compare_{ts}.md"

    report_abs = (project_root / report_path).resolve() if not Path(report_path).is_absolute() else Path(report_path).resolve()

    if write_report:
        lines = []
        lines.append("# Repo Compare Report")
        lines.append("")
        lines.append(f"- Left: `{left_root}`")
        lines.append(f"- Right: `{right_root}`")
        lines.append(f"- Exclude prefixes: `{', '.join(exclude)}`")
        lines.append("")
        lines.append("## Summary")
        lines.append(f"- Added: {len(added)}")
        lines.append(f"- Removed: {len(removed)}")
        lines.append(f"- Changed: {len(changed)}")
        lines.append(f"- Same (by sha): {same}")
        lines.append("")
        if added:
            lines.append("## Added")
            lines += [f"- `{p}`" for p in added[:200]]
            if len(added) > 200:
                lines.append(f"- ... ({len(added)-200} more)")
            lines.append("")
        if removed:
            lines.append("## Removed")
            lines += [f"- `{p}`" for p in removed[:200]]
            if len(removed) > 200:
                lines.append(f"- ... ({len(removed)-200} more)")
            lines.append("")
        if changed:
            lines.append("## Changed")
            for it in changed[:200]:
                lines.append(f"- `{it['path']}` (L:{it['size_left']} B, R:{it['size_right']} B)")
            if len(changed) > 200:
                lines.append(f"- ... ({len(changed)-200} more)")
            lines.append("")
        _write_report(report_abs, lines)

    delta = bytes_right - bytes_left
    status = "ok"

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "repo_compare"),
        "status": status,
        "outputs": {
            "left_root": str(left_root),
            "right_root": str(right_root),
            "added": added,
            "removed": removed,
            "changed": changed,
            "same": same,
            "report_path": str(report_abs),
        },
        "metrics": {
            "files_left": len(left_files),
            "files_right": len(right_files),
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "same": same,
            "bytes_left": bytes_left,
            "bytes_right": bytes_right,
            "bytes_delta": delta,
        },
        "errors": [],
        "warnings": [],
    }
