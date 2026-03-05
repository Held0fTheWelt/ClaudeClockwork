#!/usr/bin/env python3
"""
repo_clean — CCW-MVP13 Cleaning Suite skill.

Scans the repository for common clutter: cache dirs, temp files, system files,
empty directories, and duplicate filenames.  Never modifies the filesystem
(scan_only=True by default).

Usage (standalone):
    python repo_clean.py '{"skill_id":"repo_clean","inputs":{"root":".","scan_only":true}}'
    echo '{"inputs":{"root":"."}}' | python repo_clean.py

Usage (via skill_runner):
    The run(req) interface is called with a SkillRequestSpec dict.

Inputs:
    root       (str)       — directory to scan; default "."
    scan_only  (bool)      — default True; must be set to False explicitly to allow any
                             future write mode (not yet implemented)
    patterns   (list[str]) — additional glob patterns to flag as clutter (merged with defaults)

Default clutter patterns:
    Dirs:  __pycache__, .pytest_cache, .mypy_cache, .ruff_cache
    Files: *.pyc, *.pyo, *.tmp, *.log, *.bak, *.swp, *.swo, .DS_Store, Thumbs.db

Output (skill_result_spec):
    {
      "type": "skill_result_spec",
      "status": "ok",
      "outputs": {
        "findings": [
          {"category": "cache"|"temp"|"system"|"empty_dir", "path": str, "size_bytes": int}
        ],
        "summary": {"files_found": N, "total_size_bytes": N, "categories": {...}}
      }
    }
"""

from __future__ import annotations

import collections
import fnmatch
import json
import os
import sys
from pathlib import Path

_LIMITATIONS = [
    "scan_only=True by default — this skill never modifies the filesystem.",
    "Empty-dir detection walks the full tree; large repos may take a few seconds.",
    "Duplicate detection matches filenames only (not content); different files can share a name.",
    "Patterns apply to filenames only, not full paths.",
]

_DEFAULT_JUNK_DIRS = {
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".hypothesis", ".tox", "dist", "build", ".eggs",
}

_DEFAULT_JUNK_GLOBS = [
    "*.pyc", "*.pyo", "*.tmp", "*.log", "*.bak",
    "*.swp", "*.swo", ".DS_Store", "Thumbs.db",
]

_DEFAULT_EXCLUDE_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules",
}

# Category assignment
_DIR_CATEGORY = {
    "__pycache__": "cache", ".pytest_cache": "cache", ".mypy_cache": "cache",
    ".ruff_cache": "cache", ".hypothesis": "cache", ".tox": "cache",
    "dist": "temp", "build": "temp", ".eggs": "temp",
}
_GLOB_CATEGORY: list[tuple[str, str]] = [
    ("*.pyc", "cache"), ("*.pyo", "cache"),
    ("*.tmp", "temp"), ("*.bak", "temp"), ("*.swp", "temp"), ("*.swo", "temp"),
    ("*.log", "temp"),
    (".DS_Store", "system"), ("Thumbs.db", "system"),
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_category_for_glob(name: str) -> str:
    for pattern, cat in _GLOB_CATEGORY:
        if fnmatch.fnmatch(name, pattern):
            return cat
    return "temp"


def _is_empty_dir(path: Path) -> bool:
    try:
        return not any(True for _ in path.iterdir())
    except PermissionError:
        return False


def _safe_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _dir_size(path: Path) -> int:
    total = 0
    try:
        for entry in path.rglob("*"):
            try:
                if entry.is_file():
                    total += entry.stat().st_size
            except OSError:
                pass
    except PermissionError:
        pass
    return total


# ---------------------------------------------------------------------------
# skill_runner interface
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    """Called by skill_runner.py with a full SkillRequestSpec."""
    inputs = req.get("inputs", {}) or {}
    root = Path(inputs.get("root", ".")).resolve()
    scan_only: bool = bool(inputs.get("scan_only", True))
    extra_patterns: list[str] = list(inputs.get("patterns") or [])

    if not root.exists():
        return _error(req, f"root does not exist: {root}")

    # Merge extra patterns into glob list
    active_globs = list(_DEFAULT_JUNK_GLOBS) + extra_patterns

    findings: list[dict] = []
    # Track filenames → paths for duplicate detection
    name_map: dict[str, list[str]] = collections.defaultdict(list)

    exclude_dirs = set(_DEFAULT_EXCLUDE_DIRS)

    def _is_excluded(p: Path) -> bool:
        return any(part in exclude_dirs for part in p.relative_to(root).parts)

    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        current = Path(dirpath)
        try:
            rel_current = current.relative_to(root)
        except ValueError:
            continue

        # Prune excluded dirs in-place so os.walk skips them
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for dname in list(dirnames):
            dpath = current / dname
            rel = str(dpath.relative_to(root))

            if dname in _DEFAULT_JUNK_DIRS:
                cat = _DIR_CATEGORY.get(dname, "cache")
                sz = _dir_size(dpath)
                findings.append({"category": cat, "path": rel, "size_bytes": sz})
                # Remove from dirnames so we don't recurse into it
                dirnames.remove(dname)
                continue

        for fname in filenames:
            fpath = current / fname
            rel = str(fpath.relative_to(root))

            # Track for duplicate detection
            name_map[fname].append(rel)

            # Match against junk globs
            matched = False
            for pat in active_globs:
                if fnmatch.fnmatch(fname, pat):
                    findings.append({
                        "category": _get_category_for_glob(fname),
                        "path": rel,
                        "size_bytes": _safe_size(fpath),
                    })
                    matched = True
                    break

        # Check for empty dirs (after file processing)
        for dname in dirnames:
            dpath = current / dname
            if _is_empty_dir(dpath):
                rel = str(dpath.relative_to(root))
                findings.append({"category": "empty_dir", "path": rel, "size_bytes": 0})

    # Duplicate filenames (same name in multiple places)
    duplicates: list[dict] = []
    for fname, paths in name_map.items():
        if len(paths) > 1:
            duplicates.append({"filename": fname, "count": len(paths), "paths": sorted(paths)})
    duplicates.sort(key=lambda x: -x["count"])

    # Summary
    total_size = sum(f["size_bytes"] for f in findings)
    cat_counts: dict[str, int] = collections.Counter(f["category"] for f in findings)

    summary = {
        "files_found": len(findings),
        "total_size_bytes": total_size,
        "categories": dict(cat_counts),
        "duplicate_name_groups": len(duplicates),
    }

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "repo_clean",
        "status": "ok",
        "outputs": {
            "findings": findings,
            "duplicates": duplicates,
            "summary": summary,
            "scan_only": scan_only,
        },
        "errors": [],
        "warnings": (["scan_only=False passed but write mode is not yet implemented; treated as scan_only."]
                     if not scan_only else []),
        "metrics": summary,
    }


def _error(req: dict, msg: str) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "repo_clean",
        "status": "error",
        "outputs": {},
        "errors": [msg],
        "warnings": [],
        "metrics": {},
    }


# ---------------------------------------------------------------------------
# Standalone entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) >= 2:
        raw = sys.argv[1]
    else:
        raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Invalid JSON input: {exc}\n")
        return 1

    if data.get("type") == "skill_request_spec" or data.get("skill_id") == "repo_clean":
        result = run(data)
    else:
        result = run({"skill_id": "repo_clean", "inputs": data})

    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
