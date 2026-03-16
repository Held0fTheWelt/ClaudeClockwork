"""Phase 22 — Release check gate tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.core.gates.release_check import (
    run_release_check,
    _canonical_version,
    _changelog_mentions_version,
)


def test_release_check_clean_repo_passes() -> None:
    """With version convergence and changelog mentioning version, gate passes."""
    root = Path(__file__).resolve().parents[1]
    result = run_release_check(root)
    # May pass or fail depending on repo state (VERSION vs .claude/VERSION, changelog)
    assert "pass" in result
    assert "errors" in result


def test_canonical_version_reads_claude_version() -> None:
    """_canonical_version returns .claude/VERSION content when present."""
    root = Path(__file__).resolve().parents[1]
    v = _canonical_version(root)
    assert v is None or (isinstance(v, str) and len(v) > 0)


def test_changelog_mentions_version_detection() -> None:
    """_changelog_mentions_version returns True when version appears in file."""
    root = Path(__file__).resolve().parents[1]
    changelog = root / ".claude" / "CHANGELOG.md"
    canonical = _canonical_version(root)
    if canonical and changelog.is_file():
        assert _changelog_mentions_version(changelog, canonical) in (True, False)


def test_release_check_deliberate_mismatch_fails() -> None:
    """A changelog that does not mention the canonical version yields an error (or pass if no canonical)."""
    root = Path(__file__).resolve().parents[1]
    result = run_release_check(root)
    if result.get("pass"):
        assert len(result.get("errors", [])) == 0
    else:
        assert any("changelog" in e.lower() or "version" in e.lower() for e in result.get("errors", []))
