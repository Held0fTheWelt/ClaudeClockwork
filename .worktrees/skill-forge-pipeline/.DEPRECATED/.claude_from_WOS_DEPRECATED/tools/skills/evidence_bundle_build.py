#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 256), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_sha(project_root: Path) -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(project_root), stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return ""


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    run_dir = Path(inputs.get("run_dir", "validation_runs")).resolve()
    project_root = Path(inputs.get("project_root", ".")).resolve()

    out_zip = Path(inputs.get("out_zip", run_dir / "artifacts" / "evidence_bundle.zip")).resolve()
    out_manifest = Path(inputs.get("out_manifest", run_dir / "artifacts" / "evidence_bundle_manifest.json")).resolve()

    if not run_dir.exists():
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": req.get("skill_id", "evidence_bundle_build"),
            "status": "fail",
            "outputs": {},
            "metrics": {},
            "errors": [f"run_dir does not exist: {run_dir}"],
            "warnings": [],
        }

    out_zip.parent.mkdir(parents=True, exist_ok=True)
    out_manifest.parent.mkdir(parents=True, exist_ok=True)

    items = []
    total_size = 0
    for p in sorted(run_dir.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(run_dir)
        size = p.stat().st_size
        total_size += size
        items.append({"path": str(rel), "size": size, "sha256": _sha256(p)})

    manifest = {
        "type": "evidence_bundle_manifest",
        "run_dir": str(run_dir),
        "git_sha": _git_sha(project_root),
        "items": items,
        "total_size": total_size,
    }

    out_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(out_manifest, arcname=str(Path("artifacts") / out_manifest.name))
        for it in items:
            z.write(run_dir / it["path"], arcname=str(Path("run") / it["path"]))

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "evidence_bundle_build"),
        "status": "ok",
        "outputs": {"zip": str(out_zip), "manifest": str(out_manifest), "items": len(items), "total_size": total_size},
        "metrics": {"items": len(items), "total_size": total_size},
        "errors": [],
        "warnings": [],
    }
