"""
Phase 23 — Deterministic evidence exporter: collect allowed files, redact, write bundle + manifest.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

from claudeclockwork.core.redaction.engine import redact_text


def export_evidence_bundle(
    project_root: Path | str,
    runtime_root: Path | str | None = None,
    redact: bool = True,
    out_dir: Path | str | None = None,
) -> dict[str, Any]:
    """
    Create a redacted evidence bundle under redacted_exports/.
    Returns dict with bundle_path, manifest_path, file_count, redacted.
    """
    root = Path(project_root).resolve()
    run_root = Path(runtime_root or root / ".clockwork_runtime").resolve()
    export_base = Path(out_dir or run_root / "redacted_exports")
    export_base.mkdir(parents=True, exist_ok=True)

    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle_name = f"bundle_{ts}.zip"
    manifest_name = f"bundle_manifest_{ts}.json"
    bundle_path = export_base / bundle_name
    manifest_path = export_base / manifest_name

    # Collect allowed files (small set for minimal impl)
    allowed_rel = ["eval/results", "knowledge/outcome_ledger.jsonl"]
    manifest_entries: list[dict[str, Any]] = []
    seen: set[str] = set()

    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in allowed_rel:
            p = run_root / rel
            if p.is_file():
                name = rel.replace("\\", "/")
                if name in seen:
                    continue
                seen.add(name)
                raw = p.read_text(encoding="utf-8", errors="replace")
                content = redact_text(raw) if redact else raw
                zf.writestr(name, content)
                h = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
                manifest_entries.append({"path": name, "sha256_prefix": h, "size": len(content)})
            elif p.is_dir():
                for f in p.rglob("*"):
                    if f.is_file():
                        name = str(f.relative_to(run_root)).replace("\\", "/")
                        if name in seen:
                            continue
                        seen.add(name)
                        raw = f.read_text(encoding="utf-8", errors="replace")
                        content = redact_text(raw) if redact else raw
                        zf.writestr(name, content)
                        h = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
                        manifest_entries.append({"path": name, "sha256_prefix": h, "size": len(content)})

    version = ""
    vf = root / ".claude" / "VERSION"
    if vf.is_file():
        version = vf.read_text(encoding="utf-8").strip()
    manifest_data = {
        "timestamp": ts,
        "version": version,
        "schema_version": "1",
        "redacted": redact,
        "file_count": len(manifest_entries),
        "files": manifest_entries,
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    return {
        "bundle_path": str(bundle_path),
        "manifest_path": str(manifest_path),
        "file_count": len(manifest_entries),
        "redacted": redact,
    }
