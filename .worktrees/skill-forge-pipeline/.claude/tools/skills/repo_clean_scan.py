#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")

MARKERS = [
    ("deprecated", re.compile(r"(?i)\bdeprecated\b")),
    ("obsolete", re.compile(r"(?i)\bobsolete\b")),
    ("placeholder", re.compile(r"(?i)\bplaceholder\b")),
    ("todo_remove", re.compile(r"(?i)todo\s*:\s*remove|todo\s+remove")),
]

DEFAULT_LIMITATIONS = [
    "Heuristics cannot prove a file is truly obsolete; treat results as candidates.",
    "Markdown reachability only follows explicit relative links; convention-based usage may be unlinked.",
    "Binary formats are mostly skipped; large files are flagged by size only.",
    "If you use dynamic file loading, this scan will not detect that dependency reliably."
]

def _strip_code(md: str) -> str:
    md = CODE_FENCE_RE.sub("", md)
    md = INLINE_CODE_RE.sub("", md)
    return md

def _is_under_any(path: Path, roots: list[Path]) -> bool:
    for r in roots:
        try:
            path.relative_to(r)
            return True
        except Exception:
            pass
    return False

def _match_any_glob(name: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(name, g) for g in globs)

def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _collect_links(md_path: Path) -> list[str]:
    try:
        text = md_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    text = _strip_code(text)
    out = []
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if "#" in target:
            target = target.split("#", 1)[0]
        if not target:
            continue
        out.append(target.strip())
    return out

def _build_reachability(root: Path, entry_docs: list[str], convention_roots: list[str], exclude_dirs: list[str]) -> tuple[set[Path], dict[str, list[str]]]:
    # Build link graph for markdown files
    graph: dict[Path, list[Path]] = {}
    exclude_set = set(exclude_dirs)
    for p in root.rglob("*.md"):
        if any(part in exclude_set for part in p.parts):
            continue
        targets = []
        for t in _collect_links(p):
            tp = (p.parent / t).resolve()
            if tp.exists():
                targets.append(tp)
        graph[p.resolve()] = targets

    # BFS from entry docs
    start = []
    for ed in entry_docs:
        ep = (root / ed).resolve()
        if ep.exists():
            start.append(ep)

    visited: set[Path] = set()
    q = list(start)
    while q:
        cur = q.pop()
        if cur in visited:
            continue
        visited.add(cur)
        for nxt in graph.get(cur, []):
            if nxt not in visited:
                q.append(nxt)

    # Add convention roots as implicitly used
    conv_paths = []
    for cr in convention_roots:
        conv_paths.append((root / cr).resolve())

    for p in root.rglob("*.md"):
        rp = p.resolve()
        if any(part in exclude_set for part in rp.parts):
            continue
        if _is_under_any(rp, conv_paths):
            visited.add(rp)

    # Produce a small debug summary
    debug = {
        "entry_docs": entry_docs,
        "reachable_count": len(visited),
    }
    return visited, {"reachability": [json.dumps(debug, ensure_ascii=False)]}

def _write_reports(report_dir: Path, report_json: dict, report_md: str, plan: dict | None) -> dict:
    report_dir.mkdir(parents=True, exist_ok=True)
    ts = report_json["generated_at"].replace(":", "").replace("-", "")
    json_path = report_dir / f"repo_clean_report_{ts}.json"
    md_path = report_dir / f"repo_clean_report_{ts}.md"
    json_path.write_text(json.dumps(report_json, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(report_md, encoding="utf-8")
    out = {"report_json_path": str(json_path), "report_md_path": str(md_path)}
    if plan:
        plan_path = report_dir / f"cleanup_plan_{ts}.json"
        plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
        out["plan_path"] = str(plan_path)
    return out

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    root = Path(inputs.get("root", ".")).resolve()

    entry_docs = list(inputs.get("entry_docs", []))
    if not entry_docs:
        # sensible defaults for Claude Clockwork
        entry_docs = [
            ".claude/SYSTEM.md",
            ".claude/skills.md",
            ".claude/skills/registry.md",
            ".claude/ROADMAP.md",
            ".claude/ARCHITECTURE.md",
            ".claude/MODEL_POLICY.md",
        ]
    convention_roots = list(inputs.get("convention_roots", [])) or [
        ".claude/agents/",
        ".claude/contracts/",
        ".claude/tools/",
        ".claude/skills/",
    ]
    exclude_dirs = list(inputs.get("exclude_dirs", [])) or [
        ".git", ".hg", ".svn", ".idea", ".vscode", ".venv", "venv", "node_modules"
    ]
    junk_dir_names = list(inputs.get("junk_dir_names", [])) or [
        "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"
    ]
    junk_file_globs = list(inputs.get("junk_file_globs", [])) or [
        "*.pyc", "*.pyo", "*.tmp", "*.log", "*.bak", "*.swp", "*.swo", ".DS_Store", "Thumbs.db"
    ]
    large_file_bytes = int(inputs.get("large_file_bytes", 5_000_000))
    write_reports = bool(inputs.get("write_reports", False))
    report_dir = Path(inputs.get("report_dir", ".clockwork_runtime/knowledge/writes/clean_reports")).resolve()

    warnings: list[str] = []
    reachable_md, debug = _build_reachability(root, entry_docs, convention_roots, exclude_dirs)

    junk_artifacts = []
    unreferenced_docs = []
    large_files = []
    dup_map: dict[str, list[str]] = {}

    exclude_set = set(exclude_dirs)

    # Precompute convention paths for "in use by convention" non-md files (e.g. tools)
    conv_paths = [(root / cr).resolve() for cr in convention_roots]

    def is_excluded(p: Path) -> bool:
        return any(part in exclude_set for part in p.parts)

    for p in root.rglob("*"):
        if is_excluded(p):
            continue

        rel = str(p.relative_to(root))
        if p.is_dir():
            if p.name in junk_dir_names:
                junk_artifacts.append({
                    "path": rel,
                    "kind": "dir",
                    "reason": f"Junk cache dir: {p.name}",
                    "suggested_action": "delete",
                    "confidence": "high",
                })
            continue

        # large files
        try:
            sz = p.stat().st_size
            if sz >= large_file_bytes:
                large_files.append({"path": rel, "bytes": sz})
        except Exception:
            pass

        # junk files by glob
        if _match_any_glob(p.name, junk_file_globs):
            junk_artifacts.append({
                "path": rel,
                "kind": "file",
                "reason": f"Junk artifact: {p.name}",
                "suggested_action": "delete",
                "confidence": "high",
            })
            continue

        # duplicates (only for small-ish text-like files)
        if p.suffix.lower() in {".md",".txt",".json",".yml",".yaml"} and sz <= 1_000_000:
            try:
                digest = _sha256(p)
                dup_map.setdefault(digest, []).append(rel)
            except Exception:
                pass

        # docs reachability (for markdown)
        if p.suffix.lower() == ".md":
            rp = p.resolve()
            if rp not in reachable_md:
                # markers can raise confidence
                reason_bits = ["Not reachable from entry docs (heuristic)"]
                conf = "medium"
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    text = ""
                for name, rx in MARKERS:
                    if rx.search(text):
                        reason_bits.append(f"marker:{name}")
                        conf = "high"
                        break
                # if it's under convention roots, it should have been marked reachable; if not, note
                if _is_under_any(rp, conv_paths):
                    reason_bits.append("NOTE: under convention_root but not marked reachable (check config)")
                    conf = "low"
                unreferenced_docs.append({
                    "path": rel,
                    "reason": "; ".join(reason_bits),
                    "confidence": conf,
                })

    duplicates = []
    for digest, paths in dup_map.items():
        if len(paths) > 1:
            duplicates.append({"sha256": digest, "paths": sorted(paths)})

    # suggest an archive plan (move medium/low confidence candidates and non-high junk) – never delete by default
    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    archive_root = ".claude/_archive/repo_clean/" + datetime.datetime.utcnow().strftime("%Y-%m-%d")
    ops = []
    for item in junk_artifacts:
        # even if suggested delete, we propose archive by default in the plan
        src = item["path"]
        dst = f"{archive_root}/{src.replace(os.sep,'/')}"
        ops.append({"op":"move_to_archive","src":src,"dst":dst,"note":item["reason"]})
    for doc in unreferenced_docs:
        if doc["confidence"] in ("medium","high"):
            src = doc["path"]
            dst = f"{archive_root}/{src.replace(os.sep,'/')}"
            ops.append({"op":"move_to_archive","src":src,"dst":dst,"note":doc["reason"]})

    plan = {
        "type":"cleanup_plan",
        "root": str(root),
        "created_at": now,
        "operations": ops
    }

    report = {
        "type":"repo_clean_report",
        "root": str(root),
        "generated_at": now,
        "junk_artifacts": junk_artifacts,
        "unreferenced_docs": sorted(unreferenced_docs, key=lambda x: (x["confidence"], x["path"])),
        "duplicates": sorted(duplicates, key=lambda x: (-len(x["paths"]), x["sha256"])),
        "large_files": sorted(large_files, key=lambda x: -x["bytes"]),
        "warnings": warnings + debug.get("reachability", []),
        "limitations": DEFAULT_LIMITATIONS,
    }

    # Build a human-readable MD report
    md = []
    md.append("# Repo Clean Report")
    md.append(f"- Root: `{root}`")
    md.append(f"- Generated: `{now}`")
    md.append("")
    md.append("## Junk artifacts")
    md.append(f"Count: **{len(junk_artifacts)}**")
    for it in junk_artifacts[:200]:
        md.append(f"- `{it['path']}` — {it['reason']} (suggest: {it['suggested_action']}, conf: {it['confidence']})")
    if len(junk_artifacts) > 200:
        md.append(f"- ... ({len(junk_artifacts)-200} more)")
    md.append("")
    md.append("## Unreferenced docs (heuristic)")
    md.append(f"Count: **{len(unreferenced_docs)}**")
    for it in unreferenced_docs[:200]:
        md.append(f"- `{it['path']}` — {it['reason']} (conf: {it['confidence']})")
    if len(unreferenced_docs) > 200:
        md.append(f"- ... ({len(unreferenced_docs)-200} more)")
    md.append("")
    md.append("## Duplicates (sha256)")
    md.append(f"Groups: **{len(duplicates)}**")
    for g in duplicates[:50]:
        md.append(f"- `{g['sha256'][:12]}…` — {len(g['paths'])} files")
        for pth in g["paths"][:10]:
            md.append(f"  - `{pth}`")
        if len(g["paths"]) > 10:
            md.append(f"  - ... ({len(g['paths'])-10} more)")
    md.append("")
    md.append("## Large files")
    md.append(f"Count: **{len(large_files)}** (threshold: {large_file_bytes} bytes)")
    for lf in large_files[:50]:
        md.append(f"- `{lf['path']}` — {lf['bytes']} bytes")
    md.append("")
    md.append("## Suggested cleanup plan (archive-first)")
    md.append(f"Operations: **{len(ops)}**")
    md.append(f"Archive root: `{archive_root}`")
    md.append("")
    md.append("## Limitations")
    for lim in DEFAULT_LIMITATIONS:
        md.append(f"- {lim}")
    report_md = "\n".join(md) + "\n"

    outputs = {
        "report": report,
        "plan": plan,
    }

    if write_reports:
        written = _write_reports(report_dir, report, report_md, plan)
        outputs.update(written)

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id": req.get("skill_id","repo_clean_scan"),
        "status":"ok",
        "outputs": outputs,
        "errors": [],
        "warnings": warnings,
        "metrics": {
            "junk_artifacts_count": len(junk_artifacts),
            "unreferenced_docs_count": len(unreferenced_docs),
            "duplicate_groups_count": len(duplicates),
            "large_files_count": len(large_files),
            "plan_ops_count": len(ops),
        }
    }
