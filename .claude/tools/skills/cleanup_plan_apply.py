#!/usr/bin/env python3
from __future__ import annotations

import glob
import json
import os
import shutil
from pathlib import Path

DEFAULT_LIMITATIONS = [
    "This applies filesystem operations; always start with dry_run=true and review the plan.",
    "Deletion is disabled by default; enable allow_delete explicitly if you really need it.",
    "If destination already exists, behavior depends on on_conflict (default: skip).",
    "Operations are executed in order; if earlier moves change later paths, adjust your plan."
]

def _resolve_plan_path(root: Path, plan_path_pattern: str) -> Path:
    # support glob patterns, pick the newest match
    p = Path(plan_path_pattern)
    if p.exists():
        return p.resolve()
    matches = glob.glob(str((root / plan_path_pattern).resolve()))
    if not matches:
        # try pattern as-is
        matches = glob.glob(plan_path_pattern)
    if not matches:
        raise FileNotFoundError(f"No cleanup plan matches: {plan_path_pattern}")
    matches_paths = [Path(m) for m in matches]
    matches_paths.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return matches_paths[0].resolve()

def _within_root(root: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False

def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    root = Path(inputs.get("root", ".")).resolve()

    plan_obj = inputs.get("plan")
    plan_path_pattern = inputs.get("plan_path")

    if plan_obj is None and not plan_path_pattern:
        return {
            "type":"skill_result_spec",
            "request_id": req.get("request_id",""),
            "skill_id":"cleanup_plan_apply",
            "status":"error",
            "outputs": {},
            "errors": ["Provide either inputs.plan or inputs.plan_path"],
            "warnings": [],
            "metrics": {}
        }

    warnings = []
    try:
        if plan_obj is None:
            plan_path = _resolve_plan_path(root, str(plan_path_pattern))
            plan_obj = json.loads(plan_path.read_text(encoding="utf-8"))
        else:
            plan_path = None
    except Exception as e:
        return {
            "type":"skill_result_spec",
            "request_id": req.get("request_id",""),
            "skill_id":"cleanup_plan_apply",
            "status":"error",
            "outputs": {},
            "errors": [f"Failed to load plan: {e}"],
            "warnings": [],
            "metrics": {}
        }

    dry_run = bool(inputs.get("dry_run", True))
    allow_delete = bool(inputs.get("allow_delete", False))
    on_conflict = str(inputs.get("on_conflict", "skip")).lower()  # skip|overwrite|rename
    write_report = bool(inputs.get("write_report", True))
    report_dir = (root / (inputs.get("report_dir") or ".llama_runtime/knowledge/writes/clean_reports")).resolve()

    ops = plan_obj.get("operations", []) or []
    results = []
    moved = deleted = skipped = missing = errors = 0

    for op in ops:
        kind = op.get("op")
        src = Path(op.get("src",""))
        dst = Path(op.get("dst","")) if op.get("dst") else Path("")
        src_abs = (root / src).resolve() if not src.is_absolute() else src.resolve()
        dst_abs = (root / dst).resolve() if dst and not dst.is_absolute() else (dst.resolve() if dst else None)

        # security: keep operations within root (unless explicitly disabled)
        if not _within_root(root, src_abs):
            results.append({"op": kind, "src": str(src), "dst": str(dst), "status":"skipped",
                            "message":"src is outside root; skipped"})
            skipped += 1
            continue
        if dst_abs and not _within_root(root, dst_abs):
            results.append({"op": kind, "src": str(src), "dst": str(dst), "status":"skipped",
                            "message":"dst is outside root; skipped"})
            skipped += 1
            continue

        if not src_abs.exists():
            results.append({"op": kind, "src": str(src), "dst": str(dst), "status":"missing",
                            "message":"source does not exist"})
            missing += 1
            continue

        if kind == "move_to_archive":
            # conflict handling
            final_dst = dst_abs
            if final_dst is None:
                results.append({"op": kind, "src": str(src), "dst": str(dst), "status":"error",
                                "message":"dst missing for move"})
                errors += 1
                continue

            if final_dst.exists():
                if on_conflict == "skip":
                    results.append({"op": kind, "src": str(src), "dst": str(dst), "status":"skipped",
                                    "message":"destination exists; skipped"})
                    skipped += 1
                    continue
                elif on_conflict == "overwrite":
                    if not dry_run:
                        if final_dst.is_dir():
                            shutil.rmtree(final_dst)
                        else:
                            final_dst.unlink()
                elif on_conflict == "rename":
                    # add suffix
                    base = final_dst
                    k = 1
                    while final_dst.exists():
                        final_dst = base.with_name(base.name + f".{k}")
                        k += 1
                else:
                    results.append({"op": kind, "src": str(src), "dst": str(dst), "status":"skipped",
                                    "message":f"unknown on_conflict={on_conflict}; skipped"})
                    skipped += 1
                    continue

            if dry_run:
                results.append({"op": kind, "src": str(src), "dst": str(final_dst.relative_to(root) if _within_root(root, final_dst) else final_dst),
                                "status":"planned", "message":"dry_run"})
            else:
                _ensure_parent(final_dst)
                shutil.move(str(src_abs), str(final_dst))
                results.append({"op": kind, "src": str(src), "dst": str(final_dst.relative_to(root) if _within_root(root, final_dst) else final_dst),
                                "status":"moved", "message":"moved"})
                moved += 1

        elif kind == "delete":
            if not allow_delete:
                results.append({"op": kind, "src": str(src), "dst": str(dst), "status":"skipped",
                                "message":"delete not allowed (allow_delete=false)"})
                skipped += 1
                continue
            if dry_run:
                results.append({"op": kind, "src": str(src), "dst": "", "status":"planned", "message":"dry_run delete"})
            else:
                try:
                    if src_abs.is_dir():
                        shutil.rmtree(src_abs)
                    else:
                        src_abs.unlink()
                    results.append({"op": kind, "src": str(src), "dst":"", "status":"deleted", "message":"deleted"})
                    deleted += 1
                except Exception as e:
                    results.append({"op": kind, "src": str(src), "dst":"", "status":"error", "message":str(e)})
                    errors += 1
        else:
            results.append({"op": kind, "src": str(src), "dst": str(dst), "status":"skipped",
                            "message":"unsupported op"})
            skipped += 1

    total = len(results)
    # in dry_run, moved/deleted stay 0; planned operations show as planned
    if dry_run:
        moved = deleted = 0

    now = __import__("datetime").datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    report = {
        "type":"cleanup_apply_report",
        "generated_at": now,
        "dry_run": dry_run,
        "operations": results,
        "summary": {
            "total": total,
            "moved": moved,
            "deleted": deleted,
            "skipped": skipped,
            "missing": missing,
            "errors": errors
        },
        "warnings": warnings + ([f"plan_path={plan_path}"] if plan_path else []),
        "limitations": DEFAULT_LIMITATIONS,
    }

    # write report
    report_json_path = None
    if write_report:
        report_dir.mkdir(parents=True, exist_ok=True)
        ts = now.replace(":","").replace("-","")
        report_json_path = report_dir / f"cleanup_apply_report_{ts}.json"
        report_json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"cleanup_plan_apply",
        "status":"ok",
        "outputs":{
            "report": report,
            "report_json_path": str(report_json_path) if report_json_path else None
        },
        "errors": [],
        "warnings": warnings,
        "metrics": report["summary"]
    }
