from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from skills.analysis.uml_shared import (
    build_scope_summary,
    rank_directories,
    render_class_plantuml,
    render_component_plantuml,
    render_dependency_mermaid,
    render_markdown_index,
    sanitize_alias,
    scan_repository,
    write_json,
    write_text,
)


class UmlRepoBundleSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        output_dir = Path(kwargs.get("output_dir") or (repo_root / "Docs" / "uml" / "repo_bundle")).resolve()
        include_tests = bool(kwargs.get("include_tests", False))
        max_directory_bundles = int(kwargs.get("max_directory_bundles", 6))

        scan = scan_repository(repo_root, include_tests=include_tests)
        repo_summary = build_scope_summary("repo", None, scan.modules)
        top_directories = rank_directories(scan)[:max_directory_bundles]

        repo_component = output_dir / "repo_component_overview.puml"
        repo_dependencies = output_dir / "repo_dependency_overview.mmd"
        repo_classes = output_dir / "repo_class_overview.puml"
        bundle_summary = output_dir / "repo_bundle_summary.json"
        bundle_index = output_dir / "README.md"

        write_text(repo_component, render_component_plantuml("Repository UML / component overview", scan.modules, group_by="topdir"))
        write_text(repo_dependencies, render_dependency_mermaid("Repository UML / dependency overview", scan.modules))
        write_text(repo_classes, render_class_plantuml("Repository UML / class overview", scan.modules, include_methods=False))

        generated_files = [repo_component.name, repo_dependencies.name, repo_classes.name]
        slices: list[dict[str, str | int]] = []
        for row in top_directories:
            directory = str(row["path"])
            if directory == ".":
                continue
            scope_modules = [module for module in scan.modules if module.file_path.startswith(directory + "/") or module.relative_dir == directory]
            if not scope_modules:
                continue
            alias = sanitize_alias(f"dir_{directory}")
            component_file = output_dir / f"{alias}_component.puml"
            class_file = output_dir / f"{alias}_classes.puml"
            write_text(component_file, render_component_plantuml(f"Directory UML / {directory} / components", scope_modules, group_by="directory"))
            write_text(class_file, render_class_plantuml(f"Directory UML / {directory} / classes", scope_modules, include_methods=False))
            generated_files.extend([component_file.name, class_file.name])
            slices.append(
                {
                    "path": directory,
                    "module_count": int(row["module_count"]),
                    "class_count": int(row["class_count"]),
                    "component_puml": component_file.name,
                    "class_puml": class_file.name,
                }
            )

        summary_payload = {
            "repo_summary": repo_summary,
            "top_directories": top_directories,
            "slices": slices,
            "notes": scan.generated_notes,
        }
        write_json(bundle_summary, summary_payload)
        write_text(
            bundle_index,
            render_markdown_index(
                title="Repository UML Bundle",
                description="Repository-wide UML overview with directory-level slices for the most relevant scopes.",
                summary=repo_summary,
                files=generated_files + [bundle_summary.name],
                notes=scan.generated_notes,
            ),
        )

        return SkillResult(
            True,
            "uml_repo_bundle",
            data={
                "output_dir": str(output_dir),
                "bundle_index": str(bundle_index),
                "bundle_summary": str(bundle_summary),
                "repo_component": str(repo_component),
                "repo_dependencies": str(repo_dependencies),
                "repo_classes": str(repo_classes),
                "slices": slices,
            },
            logs=[f"Generated repository UML bundle with {len(slices)} directory slices."],
        )
