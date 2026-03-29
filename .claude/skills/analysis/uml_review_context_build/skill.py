from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from skills.analysis.uml_review_shared import build_review_context, write_context_bundle
from skills.analysis.uml_shared import scan_repository


class UmlReviewContextBuildSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        output_dir = Path(kwargs.get("output_dir") or (repo_root / "Docs" / "uml" / "review_context")).resolve()
        include_tests = bool(kwargs.get("include_tests", False))
        neighbor_depth = int(kwargs.get("neighbor_depth", 1))
        max_neighbors = int(kwargs.get("max_neighbors", 10))

        scan = scan_repository(repo_root, include_tests=include_tests)
        payload = build_review_context(scan, neighbor_depth=neighbor_depth, max_neighbors=max_neighbors)
        written = write_context_bundle(output_dir, payload)

        return SkillResult(
            True,
            "uml_review_context_build",
            data={
                "output_dir": str(output_dir),
                **written,
                "directory_count": len(payload["directories"]),
                "module_count": len(payload["modules"]),
                "symbol_count": len(payload["symbols"]),
            },
            logs=[f"Built UML review context for {len(payload['modules'])} modules and {len(payload['symbols'])} symbols."],
        )
