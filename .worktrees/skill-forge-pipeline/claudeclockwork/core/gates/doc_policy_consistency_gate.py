"""
doc_policy_consistency_gate — Phase 74

Scans a curated set of policy docs for contradictory instructions about
where runtime outputs should be written. Specifically enforces:

  Rule: .report/ is curated-only; runtime/perf outputs must NOT be written there.

Fails with file + line when a document instructs writing runtime outputs into .report/*.

Checked documents:
  - .claude-performance/README.md
  - Docs/report_vs_runtime_policy.md
  - Any *.md under .claude/ that references .report/performance/
"""

from __future__ import annotations

import re
from pathlib import Path

# Phrases that contradict ".report/ is curated-only" when they instruct
# writing runtime/machine-generated outputs into .report/ as a default behavior.
CONTRADICTION_PATTERNS = [
    # "go into .report/" or "go to .report/" — default routing statement
    re.compile(r'\bgo\s+(?:into|to)\s+[`\'"]?\.report/', re.IGNORECASE),
    # "write(s).*into .report/" or "write(s).*to .report/"
    re.compile(r'\bwrit\w*\s+(?:\w+\s+){0,5}(?:into|to)\s+[`\'"]?\.report/', re.IGNORECASE),
    # "stored/saved in .report/"
    re.compile(r'\b(?:stored?|saved?)\s+(?:\w+\s+){0,3}in\s+[`\'"]?\.report/', re.IGNORECASE),
    # "defaulted to writing into .report/"
    re.compile(r'\bdefaulted?\s+to\s+writ\w+\s+(?:into|to)\s+[`\'"]?\.report/', re.IGNORECASE),
]

# Documents to check for policy contradictions
POLICY_DOCS = [
    ".claude-performance/README.md",
    "Docs/report_vs_runtime_policy.md",
]

# Extra scan: any .md under .claude/ mentioning .report/performance
EXTRA_SCAN_DIR = ".claude"
EXTRA_SCAN_GLOB = "*.md"

# Phrases that mark a line as a known-OK context (negation/prohibition/restriction)
ALLOWED_CONTEXTS = [
    re.compile(r'\bdo\s+not\b', re.IGNORECASE),
    re.compile(r'\bnot\s+(?:allowed|permitted|recommended|instructed)\b', re.IGNORECASE),
    re.compile(r'\bnever\b', re.IGNORECASE),
    re.compile(r'\bforbidden\b', re.IGNORECASE),
    re.compile(r'\bviolation\b', re.IGNORECASE),
    re.compile(r'\bremov\w+\b', re.IGNORECASE),       # "Remove ..."
    re.compile(r'\bdeleted?\b', re.IGNORECASE),
    # "Only a/an/the <qualifier> ... should/may ..." — restricted to explicit actor
    re.compile(r'^\s*only\s+(?:a\s+|an\s+|the\s+)?\w', re.IGNORECASE),
    re.compile(r'\bonly\s+(?:when|if|via|through|by)\s+explicit', re.IGNORECASE),
    re.compile(r'\bmust\s+not\b', re.IGNORECASE),
    re.compile(r'\bshould\s+not\b', re.IGNORECASE),
]


def _line_is_contradiction(line: str) -> bool:
    """Return True if the line contains a policy contradiction."""
    # Skip markdown headings — they name sections, not instructions
    stripped = line.strip()
    if stripped.startswith("#"):
        return False
    # First check if this is an allowed-context line (negation/prohibition)
    for allowed in ALLOWED_CONTEXTS:
        if allowed.search(line):
            return False
    # Check contradiction patterns
    for pattern in CONTRADICTION_PATTERNS:
        if pattern.search(line):
            return True
    return False


def _scan_file(path: Path, project_root: Path) -> list[str]:
    """Scan a single file for policy contradictions. Return list of error strings."""
    if not path.is_file():
        return []
    errors = []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []
    rel = path.relative_to(project_root)
    for lineno, line in enumerate(lines, 1):
        if _line_is_contradiction(line):
            errors.append(f"{rel}:{lineno}: policy contradiction: {line.strip()[:120]!r}")
    return errors


def run_doc_policy_consistency_gate(project_root: Path | str = ".") -> dict:
    """
    Scan policy docs for contradictory instructions about .report/ write paths.

    Returns {"pass": bool, "errors": list[str], "warnings": list[str]}.
    """
    root = Path(project_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    # Check declared policy documents
    for rel in POLICY_DOCS:
        doc_path = root / rel
        errors.extend(_scan_file(doc_path, root))

    # Extra scan: .claude/**/*.md files mentioning .report/performance/
    claude_dir = root / EXTRA_SCAN_DIR
    if claude_dir.is_dir():
        for md_file in sorted(claude_dir.rglob(EXTRA_SCAN_GLOB)):
            try:
                text = md_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            # Only scan files that mention .report/performance to limit scope
            if ".report/performance" not in text:
                continue
            errors.extend(_scan_file(md_file, root))

    return {"pass": len(errors) == 0, "errors": errors, "warnings": warnings}
