#!/usr/bin/env python3
"""
Phase 17 — Promote all LegacySkillAdapter skills to inline native delegation.

Rewrites each .claude/skills/*/skill.py that uses LegacySkillAdapter to the
inline delegation pattern (no adapter import). Updates manifest.json to set
metadata.legacy_bridge = false.

Usage:
  python scripts/promote_to_native.py --dry-run   # preview
  python scripts/promote_to_native.py --apply     # apply all
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

INLINE_TEMPLATE = '''from __future__ import annotations

import os
import sys
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


class {class_name}(SkillBase):
    _LEGACY_ID = "{legacy_id}"

    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        skills_root = repo_root / ".claude" / "tools" / "skills"
        if str(skills_root) not in sys.path:
            sys.path.insert(0, str(skills_root))
        try:
            module = __import__(self._LEGACY_ID)
        except Exception as exc:
            return SkillResult(False, self._LEGACY_ID, error=f"Legacy import failed: {{exc}}")
        req = {{
            "type": "skill_request_spec",
            "request_id": context.request_id,
            "skill_id": self._LEGACY_ID,
            "inputs": kwargs,
        }}
        old_cwd = Path.cwd()
        try:
            os.chdir(repo_root)
            result = module.run(req)
        except Exception as exc:
            return SkillResult(False, self._LEGACY_ID, error=f"Legacy execution failed: {{exc}}")
        finally:
            os.chdir(old_cwd)
        status = result.get("status") == "ok"
        outputs = result.get("outputs", {{}})
        errors = result.get("errors", [])
        warnings = result.get("warnings", [])
        metrics = result.get("metrics", {{}})
        return SkillResult(
            success=status,
            skill_name=self._LEGACY_ID,
            data=outputs,
            error=("; ".join(errors) if errors else None),
            warnings=warnings,
            metadata=metrics,
        )
'''

CLASS_RE = re.compile(
    r"class\s+(\w+)\s*\(\s*LegacySkillAdapter\s*\)\s*:",
    re.MULTILINE,
)
LEGACY_ID_RE = re.compile(
    r'legacy_skill_id\s*=\s*["\']([a-zA-Z0-9_]+)["\']',
    re.MULTILINE,
)


def find_adapter_skills(root: Path) -> list[tuple[Path, str, str]]:
    """Return list of (skill_py_path, class_name, legacy_id)."""
    out: list[tuple[Path, str, str]] = []
    for path in root.glob(".claude/skills/**/skill.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if "LegacySkillAdapter" not in text:
            continue
        class_m = CLASS_RE.search(text)
        id_m = LEGACY_ID_RE.search(text)
        if class_m and id_m:
            out.append((path, class_m.group(1), id_m.group(1)))
    return out


def apply_promotion(path: Path, class_name: str, legacy_id: str, dry_run: bool) -> bool:
    """Write inline delegation skill.py. Return True if changed."""
    new_content = INLINE_TEMPLATE.format(class_name=class_name, legacy_id=legacy_id)
    if dry_run:
        print(f"[dry-run] would rewrite {path}")
        return True
    path.write_text(new_content, encoding="utf-8")
    return True


def update_manifest(skill_dir: Path, dry_run: bool) -> bool:
    """Set metadata.legacy_bridge = false in manifest.json."""
    manifest_path = skill_dir / "manifest.json"
    if not manifest_path.is_file():
        return False
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    meta = data.get("metadata") or {}
    if meta.get("legacy_bridge") is False:
        return False
    meta["legacy_bridge"] = False
    data["metadata"] = meta
    if dry_run:
        print(f"[dry-run] would set legacy_bridge=false in {manifest_path}")
        return True
    manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Promote LegacySkillAdapter skills to inline native.")
    ap.add_argument("--dry-run", action="store_true", help="Only print what would be done")
    ap.add_argument("--apply", action="store_true", help="Apply rewrites and manifest updates")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        print("Use --dry-run or --apply.", file=sys.stderr)
        return 1
    dry_run = not args.apply
    root = Path.cwd()
    if not (root / ".claude" / "skills").is_dir():
        print("Run from repo root.", file=sys.stderr)
        return 1
    skills = find_adapter_skills(root)
    print(f"Found {len(skills)} adapter skill(s).")
    for path, class_name, legacy_id in skills:
        apply_promotion(path, class_name, legacy_id, dry_run)
        update_manifest(path.parent, dry_run)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
