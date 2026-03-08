"""
Phase 63 — Report policy gate: enforce curated-only content in .report/ directory.

Fails when runtime-generated files (JSON, JSONL, PNG) appear in .report/ directory,
ensuring .report/ is reserved exclusively for hand-curated markdown documentation.

Runtime outputs should live in .clockwork_runtime/reports/ instead.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


# File patterns that are allowed in .report/ (curated content only)
ALLOWED_PATTERNS = [
    ".gitkeep",       # Git placeholder
    "README.md",      # Directory README
    # Curated markdown files go here (hand-authored)
]

# File patterns that are forbidden in .report/ (runtime-generated, should be in .clockwork_runtime/)
FORBIDDEN_PATTERNS = [
    "*.json",         # Runtime JSON reports/metrics
    "*.jsonl",        # Runtime JSONL logs
    "*.png",          # Generated charts
    "*.jpg",          # Generated images
    "*.jpeg",
    "*.gif",
    "*.csv",          # Generated data tables
    "*.tsv",
]

# Known runtime-generated filename patterns (includes markdown reports)
RUNTIME_FILENAME_PATTERNS = [
    "budget_budget_run-unknown",
    "model_routing_outcome",
    "model_routing_report",
    "qa_gate_",
    "_cost_by_",
    "_tokens_by_",
]

# Known curated markdown filenames (hand-authored, allowed in .report/)
CURATED_MARKDOWN_PATTERNS = [
    "Report_",        # Curated reports follow Report_* naming
    "CONTRIBUTING",
    "GUIDE",
]


def _project_root() -> Path:
    """Find project root by looking for claudeclockwork package."""
    p = Path(__file__).resolve()
    for _ in range(5):
        if (p / "claudeclockwork" / "__init__.py").is_file():
            return p
        p = p.parent
    return Path.cwd()


def _is_allowed_file(path: Path) -> bool:
    """Check if file matches allowed patterns (curated content)."""
    name = path.name

    # Always allow special files
    if name == ".gitkeep" or name == "README.md":
        return True

    # Allow markdown files matching curated patterns
    if name.endswith(".md"):
        for pattern in CURATED_MARKDOWN_PATTERNS:
            if pattern in name:
                return True

    return False


def _is_forbidden_file(path: Path) -> bool:
    """Check if file matches forbidden patterns (runtime-generated)."""
    name = path.name
    suffix = path.suffix.lower()

    # Check file extensions
    forbidden_extensions = {".json", ".jsonl", ".png", ".jpg", ".jpeg", ".gif", ".csv", ".tsv"}
    if suffix in forbidden_extensions:
        return True

    # Check runtime-generated filename patterns (including markdown)
    for pattern in RUNTIME_FILENAME_PATTERNS:
        if pattern in name:
            return True

    # Check if markdown file looks like auto-generated report
    # (has timestamp pattern like _20260307T113732Z or _20260307-113732)
    if suffix == ".md":
        if "_20260" in name or "_202" in name:  # ISO-8601 date patterns
            return True

    return False


def run_report_policy_gate(project_root: Path | str | None = None) -> dict[str, Any]:
    """
    Run report policy gate.

    Scans .report/ directory and fails if any runtime-generated files are found.
    Returns dict: pass (bool), violations (list of dicts with path and reason).

    Args:
        project_root: Project root path. If None, auto-detected.

    Returns:
        Dict with keys:
        - pass: bool, True if no violations found
        - violations: list of violation dicts with keys: path, reason, file_type
        - report_dir: path to .report/ directory
    """
    root = Path(project_root).resolve() if project_root else _project_root()
    report_dir = root / ".report"
    violations = []

    if not report_dir.is_dir():
        return {
            "pass": True,
            "violations": [],
            "report_dir": str(report_dir),
            "total_violations": 0,
            "message": ".report/ directory not found (ok for bootstrap)",
        }

    # Scan all files in .report/ recursively
    for file_path in report_dir.rglob("*"):
        if not file_path.is_file():
            continue

        # Check if file is forbidden
        if _is_forbidden_file(file_path):
            rel_path = file_path.relative_to(report_dir)
            file_type = "unknown"

            if file_path.suffix.lower() == ".json":
                file_type = "JSON runtime metric/report"
            elif file_path.suffix.lower() == ".jsonl":
                file_type = "JSONL runtime log"
            elif file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
                file_type = "PNG/image generated chart"
            elif file_path.suffix.lower() in {".csv", ".tsv"}:
                file_type = "CSV/TSV data table"

            violations.append({
                "path": str(rel_path),
                "reason": "Runtime-generated files belong in .clockwork_runtime/reports/, not .report/",
                "file_type": file_type,
                "extension": file_path.suffix.lower(),
            })

    return {
        "pass": len(violations) == 0,
        "violations": violations,
        "report_dir": str(report_dir),
        "total_violations": len(violations),
    }


def main() -> int:
    """CLI entry point for report policy gate."""
    result = run_report_policy_gate()

    if not result["pass"]:
        print(f"FAIL: Report policy violations detected in {result['report_dir']}", file=sys.stderr)
        print(f"Total violations: {result['total_violations']}\n", file=sys.stderr)

        for v in result["violations"]:
            print(
                f"  [{v['file_type']}] {v['path']}\n"
                f"    Reason: {v['reason']}",
                file=sys.stderr,
            )
            print()

        return 1

    print(f"PASS: Report policy enforced. No runtime files in {result['report_dir']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
