r"""
Phase 64 — Report redaction gate: ensure curated content contains no absolute host paths or secrets.

Scans .report/**/*.md for violations of redaction rules:
1. Windows drive paths (D:\, C:\, etc.)
2. Unix home paths (/Users/, /home/)
3. Generic absolute paths (/opt/, /mnt/, /var/, /workspace/, etc.)
4. Secret patterns (api_key, token, password, etc.)

Fails with detailed violation reports including file, line number, pattern, and matched text.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any


# Redaction patterns: (name, regex, severity)
# severity: "high" = always fail gate, "medium" = log but configurable
REDACTION_PATTERNS = [
    # Windows drive paths: D:\, C:\, etc. (case-insensitive)
    (
        "windows_drive_path",
        r"[A-Za-z]:\\",
        "high",
    ),
    # Unix home paths: /Users/, /home/
    (
        "unix_home_path",
        r"(/Users/|/home/)",
        "high",
    ),
    # WSL mount paths: /mnt/[a-z]/
    (
        "wsl_mount_path",
        r"/mnt/[a-z]/",
        "high",
    ),
    # System absolute paths: /opt/, /srv/, /var/, /workspace/, /work/, /project/, /app/
    # (but NOT relative paths like ./data/ or ../data/)
    # Match only when preceded by whitespace or start of string
    (
        "system_absolute_path",
        r"(?:^|\s)/(opt|srv|var|workspace|work|project|app)/",
        "high",
    ),
    # API key patterns (api_key=value)
    (
        "api_key_pattern",
        r"api[_-]?key\s*[:=]\s*\S",
        "high",
    ),
    # Bearer token patterns
    (
        "bearer_token",
        r"bearer\s+[A-Za-z0-9._\-]+",
        "high",
    ),
    # Secret keyword with assignment (secret=value or secret: value)
    (
        "secret_keyword",
        r"\bsecret\s*[:=]\s*\S",
        "high",
    ),
    # Token keyword with assignment (token=value or token: value, but not token: Bearer...)
    (
        "token_keyword",
        r"\btoken\s*[:=]\s*(?!Bearer\b|bearer\b)\S",
        "high",
    ),
    # Password keyword with assignment (password=value or password: value)
    (
        "password_keyword",
        r"\bpassword\s*[:=]\s*\S",
        "high",
    ),
    # Credentials keyword with assignment (credentials=value or credential=value)
    (
        "credentials_keyword",
        r"\bcredentials?\s*[:=]\s*\S",
        "high",
    ),
]


def _project_root() -> Path:
    """Find project root by looking for claudeclockwork package."""
    p = Path(__file__).resolve()
    for _ in range(5):
        if (p / "claudeclockwork" / "__init__.py").is_file():
            return p
        p = p.parent
    return Path.cwd()


def _extract_context(line: str, match_start: int, match_end: int, width: int = 80) -> str:
    """
    Extract context around matched text.

    Args:
        line: Full line of text
        match_start: Start index of match
        match_end: End index of match
        width: Total context width to display

    Returns:
        Context string with ellipsis if truncated
    """
    # Try to center match in output
    context_half = width // 2
    start = max(0, match_start - context_half)
    end = min(len(line), match_end + context_half)

    # Adjust if at boundaries
    if start == 0:
        end = min(len(line), width)
    elif end == len(line):
        start = max(0, len(line) - width)

    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(line) else ""
    context = line[start:end].strip()

    return f"{prefix}{context}{suffix}"


def scan_markdown_file(file_path: Path) -> list[dict[str, Any]]:
    """
    Scan a single markdown file for redaction violations.

    Args:
        file_path: Path to markdown file

    Returns:
        List of violation dicts with keys:
        - line_number: int
        - pattern: str
        - matched_text: str
        - context: str
    """
    violations = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as e:
        # Skip files we can't read
        return violations

    lines = content.split("\n")

    for line_num, line in enumerate(lines, start=1):
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith("#"):
            continue

        # Check each redaction pattern
        for pattern_name, regex, severity in REDACTION_PATTERNS:
            # Find all matches on this line (there may be multiple)
            for match in re.finditer(regex, line, re.IGNORECASE):
                matched_text = match.group(0)
                context = _extract_context(line, match.start(), match.end())

                violations.append({
                    "line_number": line_num,
                    "pattern": pattern_name,
                    "matched_text": matched_text,
                    "context": context,
                    "severity": severity,
                })

    return violations


def run_report_redaction_gate(project_root: Path | str | None = None) -> dict[str, Any]:
    """
    Run report redaction gate.

    Scans .report/**/*.md for absolute paths and secret patterns.

    Args:
        project_root: Project root path. If None, auto-detected.

    Returns:
        Dict with keys:
        - pass: bool, True if no violations found
        - violations: list of violation dicts
        - total_violations: int
        - scanned_files: int
        - report_dir: str, path to .report/ directory
        - message: str, human-readable summary
    """
    root = Path(project_root).resolve() if project_root else _project_root()
    report_dir = root / ".report"
    violations_by_file = {}
    scanned_count = 0

    if not report_dir.is_dir():
        return {
            "pass": True,
            "violations": [],
            "total_violations": 0,
            "scanned_files": 0,
            "report_dir": str(report_dir),
            "message": ".report/ directory not found (ok for bootstrap)",
        }

    # Scan all .md files in .report/ recursively
    for md_file in report_dir.rglob("*.md"):
        if not md_file.is_file():
            continue

        scanned_count += 1
        file_violations = scan_markdown_file(md_file)

        if file_violations:
            rel_path = str(md_file.relative_to(report_dir))
            violations_by_file[rel_path] = file_violations

    # Flatten violations list with file path added
    violations = []
    for file_path, file_vios in violations_by_file.items():
        for vio in file_vios:
            violations.append({
                "file": file_path,
                **vio,
            })

    # Sort violations by file, then by line number
    violations.sort(key=lambda v: (v["file"], v["line_number"]))

    total_violations = len(violations)
    is_pass = total_violations == 0

    message = f"PASS: .report/ is redaction-safe ({scanned_count} files, 0 violations)"
    if not is_pass:
        message = f"FAIL: {total_violations} violations detected in {len(violations_by_file)} files"

    return {
        "pass": is_pass,
        "violations": violations,
        "total_violations": total_violations,
        "scanned_files": scanned_count,
        "report_dir": str(report_dir),
        "message": message,
    }


def main() -> int:
    """CLI entry point for report redaction gate."""
    result = run_report_redaction_gate()

    if not result["pass"]:
        print(f"FAIL: Report redaction violations detected", file=sys.stderr)
        print(f"Scanned {result['scanned_files']} files, found {result['total_violations']} violations\n", file=sys.stderr)

        # Group violations by file for readability
        files_with_violations = {}
        for v in result["violations"]:
            file = v["file"]
            if file not in files_with_violations:
                files_with_violations[file] = []
            files_with_violations[file].append(v)

        for file_path in sorted(files_with_violations.keys()):
            print(f"{file_path}:", file=sys.stderr)
            for v in files_with_violations[file_path]:
                print(
                    f"  Line {v['line_number']}: [{v['pattern']}] {v['matched_text']!r}",
                    file=sys.stderr,
                )
                print(f"    Context: {v['context']}", file=sys.stderr)
            print()

        return 1

    print(result["message"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
