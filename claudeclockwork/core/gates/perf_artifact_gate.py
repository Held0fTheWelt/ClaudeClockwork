"""
perf_artifact_gate — Phase 69

Enforces that .claude-performance/ contains only curated files.
Fails if machine-generated runtime patterns appear under .claude-performance/.

Allowed:
  - README.md
  - reviews/  (example stubs only)
  - charts/.gitkeep

Blocked:
  - reports/  (any file — machine-generated budget/perf reports)
  - events/   (any file — raw JSONL telemetry)
  - Any file matching timestamped or run-id patterns
"""

from __future__ import annotations
import re
from pathlib import Path

# Directories that must not contain any files (runtime output sinks)
BLOCKED_SUBDIRS = {"reports", "events"}

# Filename patterns that indicate machine-generated output
MACHINE_PATTERNS = [
    re.compile(r"run[-_]"),          # run-unknown, run-20260301
    re.compile(r"\d{8}T\d{6}Z"),     # ISO timestamps
    re.compile(r"_report_"),          # budget_report_*
    re.compile(r"performance_toggle"), # performance_toggle_*
]

# Subdirectories explicitly allowed (example/template stubs, not runtime output)
ALLOWED_SUBDIRS = {"reviews", "charts"}

# Allowed files at the root of .claude-performance/
ALLOWED_ROOT = {"README.md", ".gitkeep"}


def run_perf_artifact_gate(project_root: Path | str = ".") -> dict:
    """
    Check .claude-performance/ for machine-generated runtime artifacts.
    Returns {"pass": bool, "errors": list[str], "warnings": list[str]}.
    """
    root = Path(project_root).resolve()
    perf_dir = root / ".claude-performance"

    errors: list[str] = []
    warnings: list[str] = []

    if not perf_dir.exists():
        return {"pass": True, "errors": [], "warnings": [".claude-performance/ does not exist (skipped)"]}

    for path in perf_dir.rglob("*"):
        if not path.is_file():
            continue

        rel = path.relative_to(perf_dir)
        parts = rel.parts

        # Check blocked subdirectory
        if parts[0] in BLOCKED_SUBDIRS:
            errors.append(
                f"Runtime artifact in blocked subdir: .claude-performance/{rel}"
            )
            continue

        # Skip allowed subdirs (reviews/, charts/ are example stubs)
        if parts[0] in ALLOWED_SUBDIRS:
            continue

        # Check machine-generated filename patterns at root level
        name = path.name
        for pattern in MACHINE_PATTERNS:
            if pattern.search(name):
                errors.append(
                    f"Machine-generated filename: .claude-performance/{rel}"
                )
                break

    passed = len(errors) == 0
    return {"pass": passed, "errors": errors, "warnings": warnings}
