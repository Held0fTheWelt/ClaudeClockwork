"""Phase 52 — Circular dependency gate."""
from pathlib import Path

from claudeclockwork.core.gates.circular_deps_gate import run_circular_deps_gate

ROOT = Path(__file__).resolve().parents[1]


def test_circular_deps_gate_passes() -> None:
    result = run_circular_deps_gate(ROOT)
    assert result["pass"] is True, result.get("errors")
