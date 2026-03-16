#!/usr/bin/env python3
"""doc_review

Deterministic documentation review helper.

This is a *lint-style* review. It cannot judge prose correctness like a human,
but it can catch common doc quality failures that frequently cause confusion:
- TODO/TBD leftovers
- Missing required sections (tutorial/user guide)
- Broken local links (basic)
- Missing code block language tags
- Heading level jumps

Use it to generate a review pack that a human or LLM can then improve.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)
_CODE_FENCE_RE = re.compile(r"^```([^\n]*)$", re.M)


@dataclass
class Finding:
    severity: str  # info|warn|error
    code: str
    message: str
    path: str
    line: int


def _iter_markdown_files(root: Path, paths: list[str] | None) -> list[Path]:
    if paths:
        out = []
        for p in paths:
            pp = (root / p).resolve() if not Path(p).is_absolute() else Path(p).resolve()
            if pp.exists() and pp.is_file() and pp.suffix.lower() in {".md", ".markdown"}:
                out.append(pp)
        return out
    return sorted([p for p in root.rglob("*.md") if p.is_file()])


def _line_of(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def _check_todos(text: str, path: str) -> list[Finding]:
    findings = []
    for m in re.finditer(r"\b(TODO|TBD|FIXME)\b", text):
        findings.append(Finding("warn", "todo_leftover", f"Found '{m.group(1)}'", path, _line_of(text, m.start())))
    return findings


def _check_heading_jumps(text: str, path: str) -> list[Finding]:
    findings = []
    last = 0
    for m in _HEADING_RE.finditer(text):
        level = len(m.group(1))
        if last and level > last + 1:
            findings.append(Finding("warn", "heading_jump", f"Heading level jumps from H{last} to H{level}", path, _line_of(text, m.start())))
        last = level
    return findings


def _check_code_fence_lang(text: str, path: str) -> list[Finding]:
    findings = []
    for m in _CODE_FENCE_RE.finditer(text):
        lang = m.group(1).strip()
        if lang == "":
            findings.append(Finding("info", "code_fence_no_lang", "Code fence missing language tag", path, _line_of(text, m.start())))
    return findings


def _check_links(text: str, file_path: Path, project_root: Path) -> list[Finding]:
    findings = []
    for m in _LINK_RE.finditer(text):
        target = m.group(1).strip()
        if not target or target.startswith("http://") or target.startswith("https://") or target.startswith("mailto:"):
            continue
        if target.startswith("#"):
            continue
        # strip fragment
        target_path = target.split("#", 1)[0]
        # ignore non-file links
        if any(target_path.startswith(x) for x in ("<", "${", "{{")):
            continue
        ref = (file_path.parent / target_path).resolve()
        try:
            pr = project_root.resolve()
            if pr not in ref.parents and ref != pr:
                continue
        except Exception:
            pass
        if not ref.exists():
            rel = str(file_path.relative_to(project_root)) if file_path.is_relative_to(project_root) else str(file_path)
            findings.append(Finding("warn", "broken_local_link", f"Broken local link: {target}", rel, _line_of(text, m.start())))
    return findings


def _required_sections_for(path: str) -> list[str]:
    lp = path.lower()
    if "tutorial" in lp or "/tutorials/" in lp:
        return ["Prerequisites", "Quickstart", "Walkthrough", "Verification", "Troubleshooting", "Next Steps"]
    if "user" in lp and ("guide" in lp or "handbook" in lp or "manual" in lp):
        return ["Installation", "Usage"]
    if "architecture" in lp:
        return ["Components", "Data Flow"]
    if "security" in lp:
        return ["Threat Model", "Guidelines"]
    return []


def _check_required_sections(text: str, path: str) -> list[Finding]:
    req = _required_sections_for(path)
    if not req:
        return []
    present = set()
    for m in re.finditer(r"^##\s+(.+)$", text, flags=re.M):
        present.add(m.group(1).strip())
    missing = [s for s in req if s not in present]
    if not missing:
        return []
    return [Finding("warn", "missing_sections", "Missing sections: " + ", ".join(missing), path, 1)]


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    project_root = Path(inputs.get("project_root", ".")).resolve()
    scan_root = Path(inputs.get("scan_root", project_root)).resolve()
    paths = inputs.get("paths")
    if paths is not None and not isinstance(paths, list):
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": req.get("skill_id", "doc_review"),
            "status": "fail",
            "outputs": {},
            "metrics": {},
            "errors": ["inputs.paths must be a list of relative markdown paths (or omit to scan)"],
            "warnings": [],
        }

    files = _iter_markdown_files(scan_root, paths)
    findings: list[Finding] = []

    for fp in files:
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = str(fp.relative_to(project_root)) if fp.is_relative_to(project_root) else str(fp)
        findings += _check_todos(txt, rel)
        findings += _check_heading_jumps(txt, rel)
        findings += _check_code_fence_lang(txt, rel)
        findings += _check_links(txt, fp, project_root)
        findings += _check_required_sections(txt, rel)

    # summarize
    err = sum(1 for f in findings if f.severity == "error")
    warn = sum(1 for f in findings if f.severity == "warn")
    info = sum(1 for f in findings if f.severity == "info")

    status = "ok" if err == 0 else "fail"

    out_findings = [
        {
            "severity": f.severity,
            "code": f.code,
            "message": f.message,
            "path": f.path,
            "line": f.line,
        }
        for f in findings
    ]

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "doc_review"),
        "status": status,
        "outputs": {
            "project_root": str(project_root),
            "scan_root": str(scan_root),
            "files_scanned": len(files),
            "findings": out_findings,
        },
        "metrics": {
            "files_scanned": len(files),
            "errors": err,
            "warnings": warn,
            "info": info,
            "findings": len(findings),
        },
        "errors": (["Doc review found errors"] if status == "fail" else []),
        "warnings": [],
    }
