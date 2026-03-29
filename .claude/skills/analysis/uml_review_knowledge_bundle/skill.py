from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from skills.analysis.repo_how_it_works_shared import build_how_it_works_payload, write_how_it_works_bundle
from skills.analysis.uml_review_shared import build_review_context, write_context_bundle, write_review_site
from skills.analysis.uml_shared import scan_repository


class UmlReviewKnowledgeBundleSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        context_output_dir = Path(kwargs.get('context_output_dir') or (repo_root / 'Docs' / 'uml' / 'review_context')).resolve()
        guide_output_dir = Path(kwargs.get('guide_output_dir') or (repo_root / 'Docs' / 'uml' / 'how_it_works')).resolve()
        site_output_dir = Path(kwargs.get('site_output_dir') or (repo_root / 'Docs' / 'uml' / 'review_site')).resolve()
        site_title = str(kwargs.get('site_title') or 'UML Review Explorer')
        include_tests = bool(kwargs.get('include_tests', False))
        neighbor_depth = int(kwargs.get('neighbor_depth', 1))
        max_neighbors = int(kwargs.get('max_neighbors', 10))

        scan = scan_repository(repo_root, include_tests=include_tests)
        context_payload = build_review_context(scan, neighbor_depth=neighbor_depth, max_neighbors=max_neighbors)
        guide_payload = build_how_it_works_payload(scan, context_payload=context_payload, repo_root=repo_root)

        context_written = write_context_bundle(context_output_dir, context_payload)
        guide_written = write_how_it_works_bundle(guide_output_dir, guide_payload)
        site_written = write_review_site(site_output_dir, context_payload, site_title=site_title, guide_payload=guide_payload)

        return SkillResult(
            True,
            'uml_review_knowledge_bundle',
            data={
                'context': {'output_dir': str(context_output_dir), **context_written},
                'guides': {'output_dir': str(guide_output_dir), **guide_written},
                'site': {'output_dir': str(site_output_dir), **site_written},
            },
            logs=[f"Built review knowledge bundle with {len(guide_payload['guides'])} guide(s)."],
        )
