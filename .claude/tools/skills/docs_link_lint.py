#!/usr/bin/env python3
"""
docs_link_lint — Check for broken links in documentation files.

Scans all .md files in project documentation directories and verifies
that all referenced file paths exist.

Usage (via skill_runner):
    echo '{"type":"skill_request_spec","skill_id":"docs_link_lint","inputs":{}}' | python3 skill_runner.py

Output:
    {"status": "ok|fail|warn", "broken_links": [...], "checked_files": N, ...}
"""

from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from collections import defaultdict


def find_doc_files(root: Path, scope: str = "critical") -> list[Path]:
    """
    Find .md files in documentation directories.

    Scope:
    - "critical" — only mvps/, roadmaps/, Docs/, .project/Docs/
    - "full" — includes .claude/agents/, governance/, skills/
    """
    if scope == "critical":
        doc_dirs = [
            root / "Docs",
            root / "mvps",
            root / "roadmaps",
            root / ".project" / "Docs" if (root / ".project" / "Docs").exists() else None,
        ]
    else:
        doc_dirs = [
            root / "Docs",
            root / "mvps",
            root / "roadmaps",
            root / ".project" / "Docs" if (root / ".project" / "Docs").exists() else None,
            root / ".claude" / "skills",
            root / ".claude" / "agents",
            root / ".claude" / "governance",
            root / ".claude" / "knowledge",
        ]

    files = []
    for doc_dir in doc_dirs:
        if doc_dir and doc_dir.exists():
            files.extend(doc_dir.rglob("*.md"))

    return sorted(set(files))


def extract_links(file_path: Path, root: Path) -> list[tuple[str, str | None]]:
    """
    Extract all links from a markdown file.
    Returns list of (target_path, link_type) tuples.

    Detects:
    - [text](path) — markdown links
    - → ./path or → ../path — arrow references (must have / or .)
    """
    links = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return links

    # Pattern 1: Markdown links [text](path)
    for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content):
        target = match.group(2).strip()
        # Skip URLs, anchors, and bare words
        if target.startswith(('http://', 'https://', '#', 'mailto:')):
            continue
        # Must contain a path separator or file extension
        if '/' not in target and '.' not in target:
            continue
        links.append((target, "markdown"))

    # Pattern 2: Arrow references → path (must have / or . to be a path)
    for match in re.finditer(r'→\s+([./a-zA-Z0-9_\-\.]+(?:/[a-zA-Z0-9_\-\.]+)*)', content):
        target = match.group(1).strip()
        # Only paths with / or .md extension
        if '/' in target or target.endswith(('.md', '.py', '.json', '.yaml', '.yml')):
            links.append((target, "arrow"))

    return links


def resolve_link(link: str, file_path: Path, root: Path) -> Path | None:
    """
    Resolve a link target to an actual file path.

    Handles:
    - Relative paths: ../path/file.md → resolved relative to file_path
    - Absolute paths: /path/file.md → resolved relative to root
    - Project paths: path/file.md → resolved relative to root
    """
    link = link.rstrip('/')  # Remove trailing slashes

    if link.startswith('/'):
        # Absolute path from root
        target = root / link.lstrip('/')
    elif link.startswith('./') or link.startswith('../'):
        # Relative path from file location
        target = (file_path.parent / link).resolve()
    else:
        # Try project-relative first, then file-relative
        target1 = root / link
        target2 = (file_path.parent / link).resolve()

        if target1.exists():
            target = target1
        else:
            target = target2

    # Verify path is under root (security: prevent escaping)
    try:
        target.resolve().relative_to(root)
    except ValueError:
        return None  # Path escapes root

    return target.resolve() if target.exists() else None


def run(req: dict) -> dict:
    """Called by skill_runner.py with a full SkillRequestSpec."""
    inputs = req.get("inputs") or {}
    root = Path(inputs.get("root", ".")).resolve()
    scope = inputs.get("scope", "critical")  # "critical" or "full"

    doc_files = find_doc_files(root, scope)
    broken_links = []
    checked_files = 0
    checked_links = 0
    resolved_ok = 0

    for file_path in doc_files:
        checked_files += 1
        links = extract_links(file_path, root)

        for link_target, link_type in links:
            checked_links += 1
            resolved = resolve_link(link_target, file_path, root)

            if resolved is None:
                rel_file = file_path.relative_to(root)
                broken_links.append({
                    "file": str(rel_file),
                    "link": link_target,
                    "type": link_type,
                })
            else:
                resolved_ok += 1

    has_broken = len(broken_links) > 0
    status = "fail" if has_broken else "ok"
    severity = "blocker" if has_broken else "none"

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "docs_link_lint",
        "status": status,
        "outputs": {
            "checked_files": checked_files,
            "checked_links": checked_links,
            "resolved_ok": resolved_ok,
            "broken_count": len(broken_links),
            "broken_links": broken_links[:50],  # Limit output
            "severity": severity,
        },
        "errors": [f"{len(broken_links)} broken link(s) in documentation"] if has_broken else [],
        "warnings": [],
        "metrics": {
            "link_resolution_rate": round(resolved_ok / checked_links, 3) if checked_links > 0 else 1.0,
        },
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
        req = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": f"invalid JSON: {exc}"}))
        return 2

    result = run(req)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
