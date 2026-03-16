#!/usr/bin/env python3
"""pattern_detect

Detect recurring patterns in a codebase (heuristic first-pass).

Interface: run(req: dict) -> SkillResultSpec
- Reads req["inputs"]
- Writes optional markdown to inputs["output_path"]

Deterministic local-file tool. No network.
"""

from __future__ import annotations

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()

def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def _list_files(root: Path, include_ext: Optional[List[str]] = None) -> List[Path]:
    out: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {'.git','.svn','.hg','__pycache__','.pytest_cache','node_modules','.venv'}]
        for fn in filenames:
            p = Path(dirpath) / fn
            if include_ext and p.suffix.lower() not in include_ext:
                continue
            out.append(p)
    return out

def _ok(req: dict, outputs: dict, warnings: Optional[List[str]] = None, metrics: Optional[dict] = None) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", ""),
        "status": "ok",
        "outputs": outputs,
        "errors": [],
        "warnings": warnings or [],
        "metrics": metrics or {},
    }

def _fail(req: dict, errors: List[str], warnings: Optional[List[str]] = None, metrics: Optional[dict] = None) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", ""),
        "status": "fail",
        "outputs": {},
        "errors": errors,
        "warnings": warnings or [],
        "metrics": metrics or {},
    }
def run(req: dict) -> dict:
    try:
        inputs = req.get("inputs", {})
        root = Path(inputs.get("root", ".")).resolve()
        if not root.is_dir():
            return _fail(req, [f"inputs.root is not a directory: {root}"])

        heuristics = inputs.get("heuristics") or ["singleton","factory","observer","service_locator","event_bus","dependency_injection","state_machine"]
        max_findings = int(inputs.get("max_findings") or 50)
        output_path = inputs.get("output_path")

        files = _list_files(root, include_ext=[".py",".cpp",".cc",".c",".h",".hpp",".inl",".cs",".js",".ts"])
        findings: List[Dict[str, Any]] = []

        signatures = {
            "singleton": [r"GetInstance\s*\(", r"static\s+.*instance"],
            "factory": [r"\bFactory\b", r"Create\w*\s*\("],
            "observer": [r"AddListener\s*\(", r"Subscribe\s*\(", r"Notify\w*\s*\("],
            "service_locator": [r"ServiceLocator", r"GetService\s*\("],
            "event_bus": [r"EventBus", r"Publish\s*\(", r"Subscribe\s*\("],
            "dependency_injection": [r"@inject", r"\binject\b"],
            "state_machine": [r"enum\s+class\s+State", r"Transition\s*\("],
        }

        for fp in files:
            txt = _read_text(fp)
            for pat in heuristics:
                for sig in signatures.get(pat, []):
                    if re.search(sig, txt, flags=re.IGNORECASE|re.MULTILINE):
                        findings.append({"pattern": pat, "file": str(fp), "signature": sig})
                        break
            if len(findings) >= max_findings:
                break

        counts: Dict[str,int] = {}
        for f in findings:
            counts[f["pattern"]] = counts.get(f["pattern"], 0) + 1

        outputs = {
            "root": str(root),
            "patterns_requested": heuristics,
            "counts": counts,
            "findings": findings,
        }

        if output_path:
            op = Path(output_path)
            lines = ["# Pattern Detection Report", "", f"Root: `{root}`", "", "## Summary", ""]
            for k,v in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
                lines.append(f"- **{k}**: {v}")
            lines += ["", "## Findings (sample)", ""]
            for f in findings[:max_findings]:
                lines.append(f"- `{f['pattern']}` — `{f['file']}` (sig: `{f['signature']}`)")
            _write_text(op, "\n".join(lines) + "\n")
            outputs["output_path"] = str(op)

        return _ok(req, outputs, metrics={"files_scanned": len(files), "findings": len(findings)})
    except Exception as e:
        return _fail(req, [f"Unhandled error: {e!r}"])
