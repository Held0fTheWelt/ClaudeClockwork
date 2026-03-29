from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from skills.analysis.uml_shared import build_catalog, render_markdown_index, scan_repository, write_json, write_text


class UmlScopeCatalogSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        output_dir = Path(kwargs.get("output_dir") or (repo_root / "Docs" / "uml" / "catalog")).resolve()
        include_tests = bool(kwargs.get("include_tests", False))

        scan = scan_repository(repo_root, include_tests=include_tests)
        payload = build_catalog(scan)
        catalog_json = output_dir / "uml_scope_catalog.json"
        catalog_md = output_dir / "uml_scope_catalog.md"

        write_json(catalog_json, payload)
        write_text(
            catalog_md,
            render_markdown_index(
                title="UML Scope Catalog",
                description="Repository inventory for UML-friendly analysis and scope selection.",
                summary=payload["summary"],
                files=[catalog_json.name],
                notes=payload.get("notes", []),
            ),
        )

        return SkillResult(
            True,
            "uml_scope_catalog",
            data={
                "output_dir": str(output_dir),
                "catalog_json": str(catalog_json),
                "catalog_md": str(catalog_md),
                "module_count": scan.module_count,
                "class_count": scan.class_count,
                "languages": scan.languages,
            },
            logs=[f"Scanned {scan.module_count} modules and {scan.class_count} classes."],
        )
