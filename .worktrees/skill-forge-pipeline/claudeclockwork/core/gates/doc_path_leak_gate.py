"""
doc_path_leak_gate — Phase 70

Scans curated documentation directories for absolute host path leaks.
Fails if any Windows drive paths, Unix home paths, or project-specific
absolute paths appear outside runtime roots.

Scoped dirs:
  - Docs/
  - .project/Docs/
  - .claude/governance/
  - .claude/agents/
  - mvps/

Excluded:
  - .clockwork_runtime/  (runtime — paths expected there)
  - .llama_runtime/      (legacy stub)
  - .claude-performance/ (runtime telemetry)
"""

from __future__ import annotations
import re
from pathlib import Path

# Patterns that indicate absolute host paths
LEAK_PATTERNS = [
    # Windows drive letters (C:\, D:\, E:\, etc.)
    # Use negative lookbehind to avoid false-positives like "code:\n" (drive letter must
    # not be preceded by a word character — real drive letters start paths, not words)
    re.compile(r'(?<![A-Za-z0-9_])[A-Z]:\\[A-Za-z0-9_.\-]', re.IGNORECASE),
    # Unix home dirs
    re.compile(r'/home/[a-zA-Z_][a-zA-Z0-9_\-]*(?:/|$)'),
    re.compile(r'/Users/[a-zA-Z_][a-zA-Z0-9_\-]*(?:/|$)'),
    # WSL Windows mounts with specific usernames or paths
    re.compile(r'/mnt/[a-z]/(?!\.\.)[A-Za-z]'),
]

# Curated directories to scan
CURATED_DIRS = [
    "Docs",
    ".project/Docs",
    ".claude/governance",
    ".claude/agents",
    "mvps",
]

# Placeholder patterns that are explicitly allowed (not real paths)
PLACEHOLDER_PATTERN = re.compile(r'<[A-Z_]+>')


def _line_has_leak(line: str) -> list[str]:
    """Return list of matched leak patterns on a line."""
    matches = []
    for pattern in LEAK_PATTERNS:
        for match in pattern.finditer(line):
            matched_text = match.group(0)
            # Skip if surrounded by placeholder markers
            context_start = max(0, match.start() - 1)
            context_end = min(len(line), match.end() + 5)
            context = line[context_start:context_end]
            if "<" in context or ">" in context:
                continue
            # Skip generic username placeholders like /Users/<username>/
            if "<username>" in line[match.start():match.end() + 20]:
                continue
            matches.append(matched_text)
    return matches


def run_doc_path_leak_gate(project_root: Path | str = ".") -> dict:
    """
    Scan curated docs for absolute host path leaks.
    Returns {"pass": bool, "errors": list[str], "warnings": list[str]}.
    """
    root = Path(project_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for curated_dir in CURATED_DIRS:
        scan_dir = root / curated_dir
        if not scan_dir.exists():
            continue

        for md_file in scan_dir.rglob("*.md"):
            try:
                lines = md_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception:
                continue

            rel = md_file.relative_to(root)
            for lineno, line in enumerate(lines, 1):
                leaks = _line_has_leak(line)
                for leak in leaks:
                    errors.append(f"{rel}:{lineno}: {leak!r}")

    passed = len(errors) == 0
    return {"pass": passed, "errors": errors, "warnings": warnings}
