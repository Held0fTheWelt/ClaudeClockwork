"""Tests for CodePlanRunner."""
import pytest
from claudeclockwork.localai.runners import CodePlanRunner
from claudeclockwork.localai import run_local_capability


def test_code_plan_runner_instantiation():
    """Test CodePlanRunner can be instantiated."""
    runner = CodePlanRunner()
    assert runner is not None
    assert hasattr(runner, "run")


def test_code_plan_runner_valid_input():
    """Test CodePlanRunner accepts valid input."""
    runner = CodePlanRunner()
    result = runner.run({
        "task_id": "test_123",
        "archetype": "reporter",
        "purpose": "Generate documentation",
        "constraints": {}
    })
    assert result["status"] == "ok"
    assert result["capability"] == "code.plan"


def test_run_local_capability_code_plan():
    """Test run_local_capability works with code.plan."""
    result = run_local_capability("code.plan", {
        "task_id": "test_456",
        "archetype": "scanner",
        "purpose": "Scan files",
        "constraints": {}
    })
    assert result["status"] == "ok"
    assert result["capability"] == "code.plan"
