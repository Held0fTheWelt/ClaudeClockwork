#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
import hashlib
import io
import json
import os
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

DEFAULT_IGNORE = [
    "**/__pycache__/**", "**/*.pyc", "**/.pytest_cache/**",
    "**/.mypy_cache/**", "**/.ruff_cache/**", "**/.DS_Store", "**/Thumbs.db",
]

DEFAULT_LIMITATIONS = [
    "Evolution vs loss is heuristic: it scores file presence and counts, not semantic behavior.",
    "Zip order matters; provide zip_paths oldest -> newest.",
    "Binary assets are compared by sha256 only (no semantic diff).",
]

def _matches_any(path: str, globs: List[str]) -> bool:
    norm = path.replace("\\", "/")
    for g in globs:
        if fnmatch.fnmatch(norm, g):
            return True
        # common: treat **/name/** patterns
        if g.startswith("**/") and fnmatch.fnmatch(norm, g[3:]):
            return True
    return False

def _sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def _zip_fingerprint(zpath: Path) -> Tuple[int, str]:
    h = hashlib.sha256()
    count = 0
    with zpath.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    with zipfile.ZipFile(zpath, "r") as z:
        count = len(z.infolist())
    return count, h.hexdigest()

def _read_zip_manifest(zpath: Path, ignore_globs: List[str]) -> Tuple[Dict[str, dict], int, int]:
    """
    Returns: (manifest[path] = {sha256,size}, ignored_files_count, total_bytes)
    """
    manifest: Dict[str, dict] = {}
    ignored = 0
    total_bytes = 0
    with zipfile.ZipFile(zpath, "r") as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            p = info.filename.replace("\\", "/")
            if _matches_any(p, ignore_globs):
                ignored += 1
                continue
            total_bytes += info.file_size
            data = z.read(info)
            manifest[p] = {"sha256": _sha256_bytes(data), "size": info.file_size}
    return manifest, ignored, total_bytes

def _critical_presence(manifest: Dict[str, dict], critical_paths: List[str]) -> Tuple[int, List[str]]:
    missing = []
    present = 0
    paths = [cp.strip().rstrip("/").replace("\\","/") for cp in critical_paths]
    keys = set(manifest.keys())
    for cp in paths:
        if cp.endswith("/"):
            cp = cp[:-1]
        # directory match
        if cp in keys:
            present += 1
            continue
        if any(k.startswith(cp + "/") for k in keys):
            present += 1
            continue
        missing.append(cp)
    return present, missing

def _diff(a: Dict[str, dict], b: Dict[str, dict]) -> Tuple[List[str], List[str], List[str]]:
    a_keys = set(a.keys())
    b_keys = set(b.keys())
    added = sorted(list(b_keys - a_keys))
    removed = sorted(list(a_keys - b_keys))
    changed = sorted([k for k in (a_keys & b_keys) if a[k]["sha256"] != b[k]["sha256"]])
    return added, removed, changed

def _verdict(added: int, removed: int, changed: int, critical_removed: List[str], critical_added: List[str]) -> Tuple[str, str, List[str]]:
    reasons = []
    if critical_removed:
        reasons.append(f"Critical paths missing vs previous: {len(critical_removed)}")
    if added:
        reasons.append(f"Added files: {added}")
    if changed:
        reasons.append(f"Changed files: {changed}")
    if removed:
        reasons.append(f"Removed files: {removed}")

    if critical_removed and (added + changed) < max(5, removed):
        return "loss", "high", reasons + ["Critical removal dominates."]
    if critical_removed and (added + changed) >= removed:
        return "mixed", "medium", reasons + ["Improvements exist, but critical removals require review."]
    if removed > (added + changed) and removed > 20:
        return "loss", "medium", reasons + ["Large net removal."]
    if (added + changed) >= removed and not critical_removed:
        return "evolution", "high", reasons + ["No critical regressions detected."]
    if (added + changed) > 0 and removed > 0:
        return "mixed", "low", reasons + ["Both improvements and regressions."]
    return "unknown", "low", reasons + ["Insufficient signals."]

def _write_report_md(report: dict) -> str:
    lines = []
    lines.append("# Last-Train Report")
    lines.append(f"- Generated: `{report['generated_at']}`")
    lines.append(f"- Combined zip: `{report['combined_zip_path']}`")
    lines.append("")
    for step in report["timeline"]:
        lines.append(f"## {step['index']}: {step['zip_path']}")
        v = step["verdict"]
        lines.append(f"- Verdict: **{v['classification']}** (conf: {v['confidence']})")
        for r in v["reasons"]:
            lines.append(f"  - {r}")
        d = step.get("diff_vs_prev") or {}
        if d:
            lines.append(f"- Diff vs prev: +{d.get('added',0)} / -{d.get('removed',0)} / ~{d.get('changed',0)}")
            if d.get("critical_removed"):
                lines.append("  - Critical removed:")
                for p in d["critical_removed"]:
                    lines.append(f"    - `{p}`")
            if d.get("critical_added"):
                lines.append("  - Critical added:")
                for p in d["critical_added"]:
                    lines.append(f"    - `{p}`")
        lines.append("")
    lines.append("## Limitations")
    for lim in report["limitations"]:
        lines.append(f"- {lim}")
    lines.append("")
    return "\n".join(lines)

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    zip_paths = inputs.get("zip_paths") or []
    if not zip_paths:
        return {
            "type":"skill_result_spec",
            "request_id": req.get("request_id",""),
            "skill_id":"last_train_merge",
            "status":"error",
            "outputs": {},
            "errors": ["zip_paths is required"],
            "warnings": [],
            "metrics": {}
        }

    root_out_dir = Path(inputs.get("root_out_dir", ".llama_runtime/knowledge/writes/last_train")).resolve()
    combined_zip_name = inputs.get("combined_zip_name", "combined_last_train.zip")
    ignore_globs = inputs.get("ignore_globs") or DEFAULT_IGNORE
    critical_paths = inputs.get("critical_paths") or [
        ".claude/SYSTEM.md",
        ".claude/skills/registry.md",
        ".claude/tools/skills/skill_runner.py",
        ".claude/agents",
        ".claude/contracts",
        ".claude/skills",
    ]

    root_out_dir.mkdir(parents=True, exist_ok=True)
    now = __import__("datetime").datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    warnings = []
    timeline = []

    prev_manifest = None
    prev_critical_missing = []

    # For combined archive: path -> (zip_index, bytes)
    combined_content: Dict[str, Tuple[int, bytes]] = {}

    for i, zp in enumerate(zip_paths):
        zpath = Path(zp).expanduser().resolve()
        if not zpath.exists():
            warnings.append(f"Missing zip: {zp}")
            continue

        file_count, zsha = _zip_fingerprint(zpath)
        manifest, ignored_cnt, total_bytes = _read_zip_manifest(zpath, ignore_globs)
        crit_present, crit_missing = _critical_presence(manifest, critical_paths)

        # merge content: latest wins
        with zipfile.ZipFile(zpath, "r") as z:
            for info in z.infolist():
                if info.is_dir():
                    continue
                p = info.filename.replace("\\", "/")
                if _matches_any(p, ignore_globs):
                    continue
                data = z.read(info)
                combined_content[p] = (i, data)

        diff_obj = None
        verdict = {"classification":"unknown","confidence":"low","reasons":["First item."]}

        if prev_manifest is not None:
            added, removed, changed = _diff(prev_manifest, manifest)
            # critical removed/added measured by missing lists
            prev_missing = set(prev_critical_missing)
            cur_missing = set(crit_missing)
            critical_removed = sorted(list(cur_missing - prev_missing))
            critical_added = sorted(list(prev_missing - cur_missing))

            cls, conf, reasons = _verdict(len(added), len(removed), len(changed), critical_removed, critical_added)
            verdict = {"classification": cls, "confidence": conf, "reasons": reasons}
            diff_obj = {
                "added": len(added),
                "removed": len(removed),
                "changed": len(changed),
                "critical_removed": critical_removed,
                "critical_added": critical_added,
            }

        timeline.append({
            "index": i,
            "zip_path": str(zpath),
            "fingerprint": {"file_count": file_count, "sha256": zsha},
            "stats": {
                "files_total": len(manifest),
                "files_ignored": ignored_cnt,
                "bytes_total": total_bytes,
                "critical_present": crit_present,
                "critical_missing": len(crit_missing),
            },
            "diff_vs_prev": diff_obj,
            "verdict": verdict,
        })

        prev_manifest = manifest
        prev_critical_missing = crit_missing

    # Write combined zip (ignore globs already applied)
    combined_zip_path = (root_out_dir / combined_zip_name).resolve()
    with zipfile.ZipFile(combined_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for path, (idx, data) in sorted(combined_content.items(), key=lambda x: x[0]):
            zout.writestr(path, data)

    report = {
        "type":"last_train_report",
        "generated_at": now,
        "inputs":{
            "zip_paths": zip_paths,
            "root_out_dir": str(root_out_dir),
            "ignore_globs": ignore_globs,
            "critical_paths": critical_paths,
        },
        "combined_zip_path": str(combined_zip_path),
        "timeline": timeline,
        "warnings": warnings,
        "limitations": DEFAULT_LIMITATIONS,
    }

    # Write report files
    report_json_path = root_out_dir / f"last_train_report_{now.replace(':','').replace('-','')}.json"
    report_md_path = root_out_dir / f"last_train_report_{now.replace(':','').replace('-','')}.md"
    report_json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    report_md_path.write_text(_write_report_md(report), encoding="utf-8")

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"last_train_merge",
        "status":"ok",
        "outputs":{
            "report": report,
            "report_json_path": str(report_json_path),
            "report_md_path": str(report_md_path),
            "combined_zip_path": str(combined_zip_path),
        },
        "errors": [],
        "warnings": warnings,
        "metrics":{
            "zips_seen": len(timeline),
            "combined_files": len(combined_content),
        }
    }
