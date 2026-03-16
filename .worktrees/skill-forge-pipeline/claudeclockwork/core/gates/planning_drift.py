"""
Phase 18 — Planning drift scan.

Deterministic check: version consistency, broken links in key docs,
milestone index link existence, roadmap phase list vs mvps/MVP_Phase*.md.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def _canonical_version_path(project_root: Path) -> Path:
    return project_root / ".claude" / "VERSION"


def _read_version(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _check_version_convergence(project_root: Path) -> tuple[bool, list[str]]:
    """Canonical version is .claude/VERSION. Root VERSION (if present) must match."""
    canonical = _canonical_version_path(project_root)
    canonical_val = _read_version(canonical)
    errors: list[str] = []
    if canonical_val is None:
        errors.append("Canonical version file .claude/VERSION missing or unreadable")
        return False, errors
    root_version = project_root / "VERSION"
    if root_version.is_file():
        root_val = _read_version(root_version)
        if root_val != canonical_val:
            errors.append(
                f"Version mismatch: .claude/VERSION={canonical_val!r} vs VERSION={root_val!r}"
            )
            return False, errors
    return True, []


def _check_milestone_links(project_root: Path) -> tuple[bool, list[str]]:
    """All links in .claude-development/milestones/index.md must resolve."""
    index_path = project_root / ".claude-development" / "milestones" / "index.md"
    if not index_path.is_file():
        return True, []  # no index to check
    errors: list[str] = []
    try:
        text = index_path.read_text(encoding="utf-8")
    except OSError:
        errors.append("Cannot read milestone index")
        return False, errors
    # Match markdown links: [text](path)
    link_re = re.compile(r"\]\s*\(\s*([^)\s]+)\s*\)")
    base_dir = index_path.parent
    for m in link_re.finditer(text):
        target = m.group(1).strip()
        if target.startswith("http") or target.startswith("#"):
            continue
        # Resolve relative to index dir
        resolved = (base_dir / target).resolve()
        if not resolved.exists():
            errors.append(f"Milestone index broken link: {target} -> {resolved}")
    return len(errors) == 0, errors


def _check_roadmap_phase_files(project_root: Path) -> tuple[bool, list[str]]:
    """Roadmap should not reference phase files that do not exist in mvps/."""
    mvps_dir = project_root / "mvps"
    if not mvps_dir.is_dir():
        return True, []
    phase_files = set(
        f.name for f in mvps_dir.glob("MVP_Phase*.md") if not f.name.startswith(".")
    )
    # Optional: check roadmaps/Roadmap_ClockworkV18.md for linked phases
    roadmap_path = project_root / "roadmaps" / "Roadmap_ClockworkV18.md"
    if not roadmap_path.is_file():
        return True, []
    errors: list[str] = []
    try:
        text = roadmap_path.read_text(encoding="utf-8")
    except OSError:
        return True, []
    # Links like [MVP_Phase0](../mvps/MVP_Phase0_FoundationCleanup.md)
    phase_link_re = re.compile(r"\(\.\./mvps/(MVP_Phase\d+[^)]*\.md)\)")
    for m in phase_link_re.finditer(text):
        ref_name = m.group(1)
        if ref_name not in phase_files:
            errors.append(f"Roadmap links to missing MVP file: {ref_name}")
    return len(errors) == 0, errors


def run_planning_drift_scan(project_root: Path | str) -> dict[str, Any]:
    """
    Run all planning drift checks. Returns a result dict suitable for qa_gate.

    Keys: pass (bool), errors (list[str]), warnings (list[str]).
    """
    root = Path(project_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    ok_version, version_errors = _check_version_convergence(root)
    if not ok_version:
        errors.extend(version_errors)

    ok_milestone, milestone_errors = _check_milestone_links(root)
    if not ok_milestone:
        errors.extend(milestone_errors)

    ok_roadmap, roadmap_errors = _check_roadmap_phase_files(root)
    if not ok_roadmap:
        errors.extend(roadmap_errors)

    return {
        "pass": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
