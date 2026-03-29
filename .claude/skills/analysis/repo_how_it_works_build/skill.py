from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from skills.analysis.repo_how_it_works_shared import build_how_it_works_payload, write_how_it_works_bundle
from skills.analysis.uml_review_shared import build_review_context
from skills.analysis.uml_shared import scan_repository


class RepoHowItWorksBuildSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        output_dir = Path(kwargs.get('output_dir') or (repo_root / 'Docs' / 'uml' / 'how_it_works')).resolve()
        include_tests = bool(kwargs.get('include_tests', False))
        neighbor_depth = int(kwargs.get('neighbor_depth', 1))
        max_neighbors = int(kwargs.get('max_neighbors', 10))

        scan = scan_repository(repo_root, include_tests=include_tests)
        context_payload = build_review_context(scan, neighbor_depth=neighbor_depth, max_neighbors=max_neighbors)
        payload = build_how_it_works_payload(scan, context_payload=context_payload, repo_root=repo_root)
        written = write_how_it_works_bundle(output_dir, payload)

        return SkillResult(
            True,
            'repo_how_it_works_build',
            data={
                'output_dir': str(output_dir),
                **written,
            },
            logs=[f"Generated {len(payload['guides'])} how-it-works guide(s) at {output_dir}."],
        )
