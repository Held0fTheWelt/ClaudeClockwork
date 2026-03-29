from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from skills.analysis.repo_how_it_works_shared import build_how_it_works_payload, write_how_it_works_bundle
from skills.analysis.uml_review_shared import build_review_context, write_context_bundle, write_review_site
from skills.analysis.uml_shared import scan_repository


class UmlReviewBundleSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        context_output_dir = Path(kwargs.get('context_output_dir') or (repo_root / 'Docs' / 'uml' / 'review_context')).resolve()
        site_output_dir = Path(kwargs.get('site_output_dir') or (repo_root / 'Docs' / 'uml' / 'review_site')).resolve()
        guide_output_dir = Path(kwargs.get('guide_output_dir') or (repo_root / 'Docs' / 'uml' / 'how_it_works')).resolve()
        site_title = str(kwargs.get('site_title') or 'UML Review Explorer')
        include_tests = bool(kwargs.get('include_tests', False))
        neighbor_depth = int(kwargs.get('neighbor_depth', 1))
        max_neighbors = int(kwargs.get('max_neighbors', 10))
        include_guides = bool(kwargs.get('include_guides', True))

        scan = scan_repository(repo_root, include_tests=include_tests)
        payload = build_review_context(scan, neighbor_depth=neighbor_depth, max_neighbors=max_neighbors)
        guide_payload = build_how_it_works_payload(scan, context_payload=payload, repo_root=repo_root) if include_guides else None
        context_written = write_context_bundle(context_output_dir, payload)
        guide_written = write_how_it_works_bundle(guide_output_dir, guide_payload) if guide_payload else None
        site_written = write_review_site(site_output_dir, payload, site_title=site_title, guide_payload=guide_payload)

        data = {
            'context': {
                'output_dir': str(context_output_dir),
                **context_written,
            },
            'site': {
                'output_dir': str(site_output_dir),
                **site_written,
            },
            'directory_count': len(payload['directories']),
            'module_count': len(payload['modules']),
            'symbol_count': len(payload['symbols']),
        }
        if guide_written:
            data['guides'] = {
                'output_dir': str(guide_output_dir),
                **guide_written,
            }

        return SkillResult(
            True,
            'uml_review_bundle',
            data=data,
            logs=[f"Built UML review context, site, and {len(guide_payload['guides']) if guide_payload else 0} guide(s)."],
        )
