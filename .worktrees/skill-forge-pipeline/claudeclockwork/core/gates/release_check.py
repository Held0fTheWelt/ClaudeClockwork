"""
Phase 22 — Release check gate.

Fails on: version marker drift, missing changelog entry for current version,
optional migration notes when breaking.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from claudeclockwork.core.gates.planning_drift import run_planning_drift_scan


def _canonical_version(project_root: Path) -> str | None:
    vf = project_root / ".claude" / "VERSION"
    if not vf.is_file():
        return None
    try:
        return vf.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _changelog_mentions_version(changelog_path: Path, version: str) -> bool:
    if not changelog_path.is_file() or not version:
        return False
    try:
        text = changelog_path.read_text(encoding="utf-8")
    except OSError:
        return False
    # Support: ## 17.7.83, <!-- current-version: 17.7.83 -->, or plain 17.7.83 in first 2K
    if version in text[:2048]:
        return True
    if re.search(rf"current-version:\s*{re.escape(version)}", text, re.I):
        return True
    if re.search(rf"^#+\s*{re.escape(version)}\b", text, re.M):
        return True
    return False


def run_release_check(project_root: Path | str) -> dict[str, Any]:
    """
    Run release discipline checks. Returns result dict: pass (bool), errors (list), warnings (list).

    - Version convergence (via planning_drift_scan)
    - Changelog must mention canonical version
    """
    root = Path(project_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    # 1) Version drift
    drift = run_planning_drift_scan(root)
    if not drift.get("pass"):
        errors.extend(drift.get("errors", []))

    # 2) Changelog entry for current version
    canonical = _canonical_version(root)
    if canonical:
        changelog = root / ".claude" / "CHANGELOG.md"
        if not _changelog_mentions_version(changelog, canonical):
            errors.append(
                f"Missing changelog entry for version {canonical!r}: "
                ".claude/CHANGELOG.md must mention the canonical version (e.g. <!-- current-version: X.Y.Z --> or ## X.Y.Z)"
            )

    return {
        "pass": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
