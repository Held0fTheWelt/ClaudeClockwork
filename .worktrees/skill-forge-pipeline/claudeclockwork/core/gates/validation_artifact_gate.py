"""
validation_artifact_gate — Phase 73

Enforces that validation run directories stay runtime-only and never leak into the repo.

Policy (Docs/report_vs_runtime_policy.md — Phase 73):
  - validation_runs/           → runtime-only; must be gitignored, never committed
  - validation_runs_redacted/  → runtime-only; must be gitignored, never committed

Gate checks:
  1. Both directories are listed in .gitignore (or do not exist at all)
  2. Neither directory has any files tracked by git
  3. Any on-disk redacted manifests contain no absolute host path leaks
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

# Directories that must stay runtime-only
RUNTIME_DIRS = ["validation_runs", "validation_runs_redacted"]

# Patterns for absolute host path leaks.
# Note: JSON-encoded Windows paths use double backslash (D:\\path), so we match both.
LEAK_PATTERNS = [
    # Windows drive paths: D:\path or D:\\path (JSON-encoded)
    re.compile(r'(?<![<A-Za-z0-9_])[A-Z]:\\{1,2}[A-Za-z0-9_.\-]', re.IGNORECASE),
    re.compile(r'/home/[a-zA-Z_][a-zA-Z0-9_\-]*(?:/|$)'),
    re.compile(r'/Users/[a-zA-Z_][a-zA-Z0-9_\-]*(?:/|$)'),
    re.compile(r'/mnt/[a-z]/(?!\.\.)[A-Za-z]'),
]


def _is_gitignored(project_root: Path, rel_dir: str) -> bool:
    """Return True if the directory pattern appears in .gitignore."""
    gitignore = project_root / ".gitignore"
    if not gitignore.is_file():
        return False
    text = gitignore.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        # Match exact name or trailing-slash variant
        if line.rstrip("/") == rel_dir or line == rel_dir + "/":
            return True
    return False


def _git_tracked_files(project_root: Path, rel_dir: str) -> list[str]:
    """Return list of files under rel_dir that are tracked by git."""
    try:
        result = subprocess.run(
            ["git", "ls-files", rel_dir],
            capture_output=True, text=True, timeout=15,
            cwd=str(project_root),
        )
        if result.returncode != 0:
            return []
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        return lines
    except Exception:
        return []


def _scan_for_path_leaks(scan_dir: Path) -> list[str]:
    """Scan all files in scan_dir for absolute host path patterns."""
    errors = []
    if not scan_dir.is_dir():
        return errors
    for f in sorted(scan_dir.rglob("*")):
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern in LEAK_PATTERNS:
                for m in pattern.finditer(line):
                    matched = m.group(0)
                    # Skip if surrounded by placeholder markers
                    context = line[max(0, m.start() - 1): m.end() + 5]
                    if "<" in context or ">" in context:
                        continue
                    errors.append(
                        f"{f.relative_to(scan_dir.parent)}:{lineno}: path leak {matched!r}"
                    )
                    break  # one error per line per file
    return errors


def run_validation_artifact_gate(project_root: Path | str = ".") -> dict:
    """
    Validate that validation artifact directories stay runtime-only.

    Returns {"pass": bool, "errors": list[str], "warnings": list[str]}.
    """
    root = Path(project_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for rel_dir in RUNTIME_DIRS:
        dir_path = root / rel_dir

        # Check 1: must be gitignored (if directory exists)
        if dir_path.exists():
            if not _is_gitignored(root, rel_dir):
                errors.append(
                    f"{rel_dir}/ exists but is not listed in .gitignore — "
                    "add it to prevent accidental commits"
                )

        # Check 2: must not have any git-tracked files
        tracked = _git_tracked_files(root, rel_dir)
        if tracked:
            errors.append(
                f"{rel_dir}/ has {len(tracked)} git-tracked file(s): "
                f"{', '.join(tracked[:5])}"
            )

        # Check 3: scan for path leaks in redacted dirs
        if "redacted" in rel_dir and dir_path.is_dir():
            leak_errors = _scan_for_path_leaks(dir_path)
            if leak_errors:
                errors.extend(leak_errors[:10])
                if len(leak_errors) > 10:
                    warnings.append(
                        f"{rel_dir}/: {len(leak_errors) - 10} additional path leaks not shown"
                    )

    return {"pass": len(errors) == 0, "errors": errors, "warnings": warnings}
