"""Phase 23 — Redaction rules: patterns and replacements for secrets, paths, PII."""
from __future__ import annotations

import re
from typing import Any

# Pattern list: (regex, replacement). Applied in order.
REDACTION_PATTERNS: list[tuple[Any, str]] = [
    # API keys / tokens (generic)
    (re.compile(r"(?i)(api[_-]?key|token|secret|auth)\s*[:=]\s*['\"]?[\w\-]{20,}['\"]?"), r"\1=***REDACTED***"),
    # Bearer tokens
    (re.compile(r"Bearer\s+[\w\-\.]+", re.I), "Bearer ***REDACTED***"),
    # Windows absolute path (reduce to placeholder)
    (re.compile(r"[A-Za-z]:\\[^\s\"']+"), "[PATH]"),
    # Unix absolute path
    (re.compile(r"/[\w\-./]+(?=\s|$|[\"'])"), "[PATH]"),
    # Email-like
    (re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"), "[EMAIL]"),
]
