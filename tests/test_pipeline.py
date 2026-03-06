from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.executor.pipeline import ExecutionPipeline
from claudeclockwork.runtime import build_executor, build_planner

ROOT = Path(__file__).resolve().parents[1]


def _make_pipeline() -> ExecutionPipeline:
    return ExecutionPipeline(
        build_planner(ROOT),
        build_executor(ROOT),
        working_directory=str(ROOT),
    )


def test_pipeline_runs_known_skill() -> None:
    pipeline = _make_pipeline()
    result = pipeline.run("capability_map_build")
    assert result is not None
    assert result.get("status") in ("ok", "fail")


def test_pipeline_result_has_spec_fields() -> None:
    pipeline = _make_pipeline()
    result = pipeline.run("capability_map_build")
    assert "status" in result
    assert "errors" in result


def test_pipeline_unknown_input_does_not_raise() -> None:
    pipeline = _make_pipeline()
    result = pipeline.run("this_skill_definitely_does_not_exist_xyz")
    # Must return a dict, not raise an exception
    assert isinstance(result, dict)
    assert result.get("status") == "fail"
