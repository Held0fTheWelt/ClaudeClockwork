#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

DEFAULT_LIMITATIONS = [
    "Python static analysis cannot see dynamic imports, reflection, plugin loading, or runtime exec().",
    "Reachability is computed from configured entrypoints only; if you have multiple entrypoints, include them.",
    "Markers are heuristic; a TODO does not necessarily mean the file is obsolete."
]

MARKER_RX = [
    ("deprecated", re.compile(r"(?i)\bdeprecated\b")),
    ("obsolete", re.compile(r"(?i)\bobsolete\b")),
    ("placeholder", re.compile(r"(?i)\bplaceholder\b")),
    ("legacy", re.compile(r"(?i)\blegacy\b")),
    ("todo", re.compile(r"(?i)\btodo\b")),
    ("fixme", re.compile(r"(?i)\bfixme\b")),
]
PATH_DRIFT_RX = re.compile(r"(?i)\.claude/|\.clockwork_runtime/validation_runs|\.claude_runtime|\.claude/\.claude")

def _parse_imports(py_path: Path) -> set[str]:
    try:
        tree = ast.parse(py_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return set()
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                if n.name:
                    mods.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module.split(".")[0])
    return mods

def _scan_markers(py_path: Path) -> list[dict]:
    try:
        text = py_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    out = []
    # marker words
    for kind, rx in MARKER_RX:
        m = rx.search(text)
        if m:
            snippet = text[max(0, m.start()-60): m.end()+60].replace("\n"," ").strip()
            out.append({"path": str(py_path), "kind": kind, "snippet": snippet[:220]})
    # path drift
    m = PATH_DRIFT_RX.search(text)
    if m:
        snippet = text[max(0, m.start()-60): m.end()+60].replace("\n"," ").strip()
        out.append({"path": str(py_path), "kind": "path_drift", "snippet": snippet[:220]})
    return out

def _write_reports(report_dir: Path, report_json: dict, report_md: str) -> dict:
    report_dir.mkdir(parents=True, exist_ok=True)
    ts = report_json["generated_at"].replace(":", "").replace("-", "")
    json_path = report_dir / f"code_clean_report_{ts}.json"
    md_path = report_dir / f"code_clean_report_{ts}.md"
    json_path.write_text(json.dumps(report_json, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(report_md, encoding="utf-8")
    return {"report_json_path": str(json_path), "report_md_path": str(md_path)}

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    root = Path(inputs.get("root", ".")).resolve()
    code_roots = [ (root / p).resolve() for p in (inputs.get("code_roots") or [".claude/tools/skills"]) ]
    entrypoints = [ (root / p).resolve() for p in (inputs.get("entrypoints") or [".claude/tools/skills/skill_runner.py"]) ]
    write_reports = bool(inputs.get("write_reports", False))
    report_dir = (root / (inputs.get("report_dir") or ".clockwork_runtime/knowledge/writes/clean_reports")).resolve()

    # Map local module stems
    module_files: dict[str, Path] = {}
    all_py: list[Path] = []
    for cr in code_roots:
        if not cr.exists():
            continue
        for p in cr.rglob("*.py"):
            all_py.append(p.resolve())
            module_files[p.stem] = p.resolve()

    # Build import graph
    edges: dict[Path, set[Path]] = {p: set() for p in all_py}
    for p in all_py:
        for mod in _parse_imports(p):
            if mod in module_files:
                edges[p].add(module_files[mod])

    # Reachability from entrypoints
    reachable: set[Path] = set()
    stack = [ep for ep in entrypoints if ep.exists()]
    while stack:
        cur = stack.pop()
        if cur in reachable:
            continue
        reachable.add(cur)
        for nxt in edges.get(cur, set()):
            if nxt not in reachable:
                stack.append(nxt)

    orphan = sorted([str(p.relative_to(root)) for p in all_py if p not in reachable])

    # For the skills folder: detect modules not registered in skill_runner
    unregistered = []
    skill_runner = (root / ".claude/tools/skills/skill_runner.py").resolve()
    registered_names = set()
    if skill_runner.exists():
        txt = skill_runner.read_text(encoding="utf-8", errors="ignore")
        # SKILLS mapping uses keys like "pdf_render": pdf_render,
        for m in re.finditer(r'"\w+"\s*:\s*(\w+)\s*,', txt):
            registered_names.add(m.group(1))
    for p in all_py:
        if p.parent == skill_runner.parent:
            if p.stem not in registered_names and p.name != "skill_runner.py":
                unregistered.append(str(p.relative_to(root)))

    markers = []
    for p in all_py:
        markers.extend(_scan_markers(p))

    now = __import__("datetime").datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    report = {
        "type":"code_clean_report",
        "root": str(root),
        "generated_at": now,
        "orphan_modules": orphan,
        "unregistered_modules": sorted(unregistered),
        "markers": markers,
        "warnings": [],
        "limitations": DEFAULT_LIMITATIONS,
    }

    md = []
    md.append("# Code Clean Report")
    md.append(f"- Root: `{root}`")
    md.append(f"- Generated: `{now}`")
    md.append("")
    md.append("## Orphan modules (not reachable from entrypoints)")
    md.append(f"Count: **{len(orphan)}**")
    for pth in orphan[:200]:
        md.append(f"- `{pth}`")
    if len(orphan) > 200:
        md.append(f"- ... ({len(orphan)-200} more)")
    md.append("")
    md.append("## Unregistered modules (skills folder)")
    md.append(f"Count: **{len(unregistered)}**")
    for pth in unregistered[:200]:
        md.append(f"- `{pth}`")
    md.append("")
    md.append("## Markers")
    md.append(f"Count: **{len(markers)}**")
    for it in markers[:200]:
        md.append(f"- `{Path(it['path']).relative_to(root)}` — {it['kind']}: `{it['snippet']}`")
    md.append("")
    md.append("## Limitations")
    for lim in DEFAULT_LIMITATIONS:
        md.append(f"- {lim}")
    report_md = "\n".join(md) + "\n"

    outputs = {"report": report}
    if write_reports:
        outputs.update(_write_reports(report_dir, report, report_md))

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id": req.get("skill_id","code_clean_scan"),
        "status":"ok",
        "outputs": outputs,
        "errors": [],
        "warnings": [],
        "metrics": {
            "py_files_count": len(all_py),
            "reachable_count": len(reachable),
            "orphan_count": len(orphan),
            "unregistered_count": len(unregistered),
            "markers_count": len(markers),
        }
    }
