"""
Phase 15 — dead_file_scan skill tests.

Six tests verifying the scan skill's registry presence, native implementation,
dry-run enforcement, output contract, confidence values, and false-positive avoidance.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.runtime import build_registry
from claudeclockwork.legacy.adapter import LegacySkillAdapter

ROOT = Path(__file__).resolve().parents[1]


def _registry():
    return build_registry(ROOT)


def test_dead_file_scan_in_registry() -> None:
    """dead_file_scan must be discoverable in the manifest registry."""
    registry = _registry()
    manifest = registry.get_manifest("dead_file_scan")
    assert manifest is not None, "dead_file_scan not found in registry"
    assert manifest.metadata.get("legacy_bridge") is False, (
        "dead_file_scan must be a native skill (legacy_bridge=false)"
    )


def test_dead_file_scan_is_native() -> None:
    """dead_file_scan must not be a LegacySkillAdapter subclass."""
    registry = _registry()
    # Force class load by building registry with strict=True
    registry_strict = build_registry(ROOT, strict=True)
    cls = registry_strict._classes.get("dead_file_scan")
    assert cls is not None, "dead_file_scan class not loaded"
    assert not issubclass(cls, LegacySkillAdapter), (
        f"dead_file_scan must be native SkillBase, not LegacySkillAdapter; got {cls}"
    )


def test_dead_file_scan_dry_run_only() -> None:
    """Passing dry_run=false must return status=fail (safety guard — skill never deletes)."""
    result = run_manifest_skill(
        {
            "request_id": "p15-dry-run-guard",
            "skill_id": "dead_file_scan",
            "inputs": {"dry_run": False},
        },
        ROOT,
    )
    assert result is not None
    assert result.get("status") == "fail", (
        "dry_run=false must be rejected with status=fail"
    )
    errors = result.get("errors", [])
    assert any("dry_run" in str(e).lower() for e in errors), (
        "Error message must mention dry_run"
    )


def test_dead_file_scan_returns_candidates() -> None:
    """Scan with dry_run=true must return a well-formed output dict."""
    result = run_manifest_skill(
        {
            "request_id": "p15-output-contract",
            "skill_id": "dead_file_scan",
            "inputs": {"dry_run": True, "scan_paths": ["Docs/", "roadmaps/"]},
        },
        ROOT,
    )
    assert result is not None
    assert result.get("status") == "ok", f"Expected ok, got: {result}"
    outputs = result.get("outputs", {})
    assert "candidates" in outputs, "Output must contain 'candidates'"
    assert "candidate_count" in outputs, "Output must contain 'candidate_count'"
    assert "high_confidence_count" in outputs, "Output must contain 'high_confidence_count'"
    assert isinstance(outputs["candidates"], list)
    assert isinstance(outputs["candidate_count"], int)
    assert isinstance(outputs["high_confidence_count"], int)
    assert outputs["candidate_count"] == len(outputs["candidates"])


def test_dead_file_scan_confidence_values() -> None:
    """Every candidate returned must have confidence in {high, medium, low}."""
    result = run_manifest_skill(
        {
            "request_id": "p15-confidence",
            "skill_id": "dead_file_scan",
            "inputs": {"dry_run": True, "scan_paths": ["Docs/", "roadmaps/", "mvps/"]},
        },
        ROOT,
    )
    assert result is not None
    assert result.get("status") == "ok"
    candidates = result.get("outputs", {}).get("candidates", [])
    valid_confidence = {"high", "medium", "low"}
    for c in candidates:
        assert "confidence" in c, f"Candidate missing 'confidence' key: {c}"
        assert c["confidence"] in valid_confidence, (
            f"Invalid confidence value {c['confidence']!r} for {c.get('path')}"
        )
        assert "path" in c, f"Candidate missing 'path' key: {c}"
        assert "reason" in c, f"Candidate missing 'reason' key: {c}"


def test_dead_file_scan_no_false_positive_on_active_files() -> None:
    """Active governance files must never be flagged as candidates."""
    result = run_manifest_skill(
        {
            "request_id": "p15-no-false-positive",
            "skill_id": "dead_file_scan",
            "inputs": {
                "dry_run": True,
                "scan_paths": [".claude/governance/", "mvps/"],
            },
        },
        ROOT,
    )
    assert result is not None
    assert result.get("status") == "ok"
    candidates = result.get("outputs", {}).get("candidates", [])
    flagged_paths = {c["path"] for c in candidates}
    # These files must never be flagged
    protected = [
        "CLAUDE.md",
        ".claude/governance/execution_protocol.md",
        ".claude/governance/file_lifecycle.md",
    ]
    for protected_path in protected:
        assert not any(protected_path in fp for fp in flagged_paths), (
            f"Active file {protected_path!r} was incorrectly flagged as a dead file candidate"
        )
