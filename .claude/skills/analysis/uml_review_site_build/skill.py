from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from skills.analysis.repo_how_it_works_shared import build_how_it_works_payload
from skills.analysis.uml_review_shared import build_review_context, write_review_site
from skills.analysis.uml_shared import scan_repository


class UmlReviewSiteBuildSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        output_dir = Path(kwargs.get('output_dir') or (repo_root / 'Docs' / 'uml' / 'review_site')).resolve()
        site_title = str(kwargs.get('site_title') or 'UML Review Explorer')
        include_tests = bool(kwargs.get('include_tests', False))
        neighbor_depth = int(kwargs.get('neighbor_depth', 1))
        max_neighbors = int(kwargs.get('max_neighbors', 10))
        include_guides = bool(kwargs.get('include_guides', True))

        scan = scan_repository(repo_root, include_tests=include_tests)
        payload = build_review_context(scan, neighbor_depth=neighbor_depth, max_neighbors=max_neighbors)
        guide_payload = build_how_it_works_payload(scan, context_payload=payload, repo_root=repo_root) if include_guides else None
        written = write_review_site(output_dir, payload, site_title=site_title, guide_payload=guide_payload)

        return SkillResult(
            True,
            'uml_review_site_build',
            data={
                'output_dir': str(output_dir),
                **written,
            },
            logs=[f"Generated UML review site at {output_dir}."],
        )
