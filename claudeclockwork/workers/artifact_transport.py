"""Phase 35 — Artifact shipping: bundles with manifest and hashes; redact where required."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

from claudeclockwork.core.redaction.engine import redact_text


def hash_content(content: bytes) -> str:
    """SHA-256 hex digest."""
    return hashlib.sha256(content).hexdigest()


def pack_bundle(source_dir: Path | str, out_path: Path | str, redact: bool = True) -> dict[str, Any]:
    """Pack directory into zip with manifest (path -> hash). Optionally redact file contents."""
    source_dir = Path(source_dir).resolve()
    out_path = Path(out_path).resolve()
    manifest: dict[str, str] = {}
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in source_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(source_dir)
                raw = f.read_bytes()
                if redact:
                    raw = redact_text(raw.decode("utf-8", errors="replace")).encode("utf-8", errors="replace")
                h = hash_content(raw)
                manifest[str(rel)] = h
                z.writestr(str(rel), raw)
    manifest_path = out_path.with_name(out_path.name + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"bundle": str(out_path), "manifest": str(manifest_path), "hashes": manifest}


def unpack_bundle(bundle_path: Path | str, dest_dir: Path | str, verify_hashes: bool = True) -> dict[str, Any]:
    """Unpack zip to dest_dir; optionally verify hashes against manifest."""
    bundle_path = Path(bundle_path).resolve()
    dest_dir = Path(dest_dir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = bundle_path.with_name(bundle_path.name + ".manifest.json")
    manifest: dict[str, str] = {}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mismatches: list[str] = []
    with zipfile.ZipFile(bundle_path, "r") as z:
        for name in z.namelist():
            data = z.read(name)
            if verify_hashes and name in manifest and hash_content(data) != manifest[name]:
                mismatches.append(name)
            (dest_dir / name).parent.mkdir(parents=True, exist_ok=True)
            (dest_dir / name).write_bytes(data)
    return {"dest": str(dest_dir), "verified": len(mismatches) == 0, "mismatches": mismatches}
