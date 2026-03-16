"""
Tests for Phase 74 — doc_policy_consistency_gate.

Verifies that:
- The gate passes on a clean repo with consistent policy docs.
- The gate fails when a doc says "go into .report/performance/".
- The gate fails on various contradiction patterns.
- Negation/prohibition phrases are NOT flagged.
- A conflicting phrase triggers deterministic failure.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from claudeclockwork.core.gates.doc_policy_consistency_gate import (
    run_doc_policy_consistency_gate,
    _line_is_contradiction,
)


# ---------------------------------------------------------------------------
# Unit tests for _line_is_contradiction
# ---------------------------------------------------------------------------

class TestLineIsContradiction:
    """Unit tests for the line-level contradiction detector."""

    def test_go_into_report(self):
        assert _line_is_contradiction(
            "Human-readable summaries go into `.report/performance/`."
        ) is True

    def test_go_to_report(self):
        assert _line_is_contradiction(
            "All outputs go to .report/performance."
        ) is True

    def test_write_into_report(self):
        assert _line_is_contradiction(
            "The skill writes results into .report/performance/"
        ) is True

    def test_saved_in_report(self):
        assert _line_is_contradiction(
            "Reports are saved in `.report/routing/`."
        ) is True

    def test_negation_not_flagged(self):
        """'Do NOT write into .report/' should not be flagged."""
        assert _line_is_contradiction(
            "Do NOT write runtime outputs into .report/performance/."
        ) is False

    def test_never_not_flagged(self):
        assert _line_is_contradiction(
            "Never write machine-generated outputs to .report/."
        ) is False

    def test_forbidden_not_flagged(self):
        assert _line_is_contradiction(
            "FORBIDDEN: writing runtime files into .report/."
        ) is False

    def test_irrelevant_line_not_flagged(self):
        assert _line_is_contradiction("This is a normal sentence.") is False

    def test_clockwork_runtime_not_flagged(self):
        assert _line_is_contradiction(
            "Runtime outputs go into .clockwork_runtime/performance/."
        ) is False


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

class TestDocPolicyConsistencyGateCleanRepo:
    """Gate passes on clean policy docs."""

    def test_actual_repo_passes(self):
        """The actual project repo must pass the gate."""
        project_root = Path(__file__).resolve().parent.parent
        result = run_doc_policy_consistency_gate(project_root)
        assert result["pass"] is True, f"Gate failed: {result['errors'][:3]}"

    def test_empty_dir_passes(self, tmp_path):
        """Pass when policy docs don't exist (nothing to fail on)."""
        result = run_doc_policy_consistency_gate(tmp_path)
        assert result["pass"] is True


class TestDocPolicyConsistencyGateContradiction:
    """Gate fails when a policy doc contains a contradictory instruction."""

    def test_fails_on_go_into_report(self, tmp_path):
        """Fail when README says summaries go into .report/performance/."""
        perf_dir = tmp_path / ".claude-performance"
        perf_dir.mkdir()
        readme = perf_dir / "README.md"
        readme.write_text(
            "# Performance\n\n"
            "Human-readable summaries derived from this data go into `.report/performance/`.\n",
            encoding="utf-8",
        )
        result = run_doc_policy_consistency_gate(tmp_path)
        assert result["pass"] is False
        assert any(".claude-performance/README.md" in e for e in result["errors"])

    def test_fails_on_write_to_report(self, tmp_path):
        """Fail when a doc says to write outputs to .report/."""
        docs_dir = tmp_path / "Docs"
        docs_dir.mkdir()
        policy = docs_dir / "report_vs_runtime_policy.md"
        policy.write_text(
            "# Policy\n\nSkills write telemetry to .report/routing/.\n",
            encoding="utf-8",
        )
        result = run_doc_policy_consistency_gate(tmp_path)
        assert result["pass"] is False
        assert any("report_vs_runtime_policy.md" in e for e in result["errors"])

    def test_deterministic_on_same_input(self, tmp_path):
        """Gate result is deterministic across two runs."""
        r1 = run_doc_policy_consistency_gate(tmp_path)
        r2 = run_doc_policy_consistency_gate(tmp_path)
        assert r1["pass"] == r2["pass"]
        assert r1["errors"] == r2["errors"]
