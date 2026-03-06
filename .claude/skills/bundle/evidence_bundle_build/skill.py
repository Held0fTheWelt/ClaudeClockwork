from __future__ import annotations

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(262144), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_sha(project_root: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(project_root), stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except Exception:
        return ""


class EvidenceBundleBuildSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()

        # Accept either artifact list mode or run_dir mode
        artifacts = kwargs.get("artifacts")
        bundle_name = str(kwargs.get("bundle_name") or "evidence_bundle")
        run_dir = kwargs.get("run_dir")

        out_dir = (repo_root / ".llama_runtime" / "artifacts").resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        out_zip = out_dir / f"{bundle_name}.zip"
        out_manifest_path = out_dir / f"{bundle_name}_manifest.json"

        items: list[dict] = []

        if artifacts:
            # explicit artifact list mode
            for rel in artifacts:
                p = (repo_root / rel).resolve() if not Path(rel).is_absolute() else Path(rel)
                if not p.exists():
                    return SkillResult(False, "evidence_bundle_build", error=f"artifact not found: {p}")
                items.append({"path": str(rel), "size": p.stat().st_size, "sha256": _sha256(p)})
        elif run_dir:
            scan_dir = Path(run_dir).resolve()
            if not scan_dir.exists():
                return SkillResult(False, "evidence_bundle_build", error=f"run_dir not found: {scan_dir}")
            for p in sorted(scan_dir.rglob("*")):
                if p.is_dir():
                    continue
                rel = p.relative_to(scan_dir)
                items.append({"path": str(rel), "size": p.stat().st_size, "sha256": _sha256(p)})
        else:
            return SkillResult(False, "evidence_bundle_build", error="either 'artifacts' list or 'run_dir' is required")

        # Build manifest and zip
        manifest_hash_input = json.dumps(items, sort_keys=True).encode()
        manifest_hash = hashlib.sha256(manifest_hash_input).hexdigest()

        bundle_manifest = {
            "type": "evidence_bundle_manifest",
            "bundle_name": bundle_name,
            "git_sha": _git_sha(repo_root),
            "manifest_hash": manifest_hash,
            "artifact_count": len(items),
            "items": items,
        }
        out_manifest_path.write_text(json.dumps(bundle_manifest, indent=2), encoding="utf-8")

        with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(out_manifest_path, arcname=f"{bundle_name}_manifest.json")
            for item in items:
                src = (repo_root / item["path"]).resolve() if not Path(item["path"]).is_absolute() else Path(item["path"])
                if src.exists():
                    zf.write(src, arcname=str(Path("artifacts") / item["path"]))

        return SkillResult(
            True,
            "evidence_bundle_build",
            data={
                "bundle_path": str(out_zip),
                "manifest_path": str(out_manifest_path),
                "manifest_hash": manifest_hash,
                "artifact_count": len(items),
            },
        )
