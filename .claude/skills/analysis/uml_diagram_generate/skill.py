from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from skills.analysis.uml_shared import (
    UmlSkillError,
    build_scope_summary,
    expand_focus_modules,
    find_scope_modules,
    render_class_plantuml,
    render_component_plantuml,
    render_dependency_mermaid,
    render_markdown_index,
    sanitize_alias,
    scan_repository,
    write_json,
    write_text,
)


class UmlDiagramGenerateSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        scope_kind = str(kwargs.get("scope_kind") or "repo").strip().lower()
        target = kwargs.get("target")
        include_methods = bool(kwargs.get("include_methods", scope_kind == "symbol"))
        neighbor_depth = int(kwargs.get("neighbor_depth", 1 if scope_kind in {"module", "symbol"} else 0))
        scan = scan_repository(repo_root, include_tests=bool(kwargs.get("include_tests", False)))

        try:
            base_modules = find_scope_modules(scan, scope_kind, target)
        except UmlSkillError as exc:
            return SkillResult(False, "uml_diagram_generate", error=str(exc))

        if not base_modules:
            return SkillResult(False, "uml_diagram_generate", error=f"No modules found for scope {scope_kind}:{target}")

        scope_modules = expand_focus_modules(scan, base_modules, depth=neighbor_depth)
        alias = sanitize_alias(f"{scope_kind}_{target or 'repo'}")
        output_dir = Path(kwargs.get("output_dir") or (repo_root / "Docs" / "uml" / "scopes" / alias)).resolve()

        component_puml = output_dir / f"{alias}_component.puml"
        dependency_mmd = output_dir / f"{alias}_dependencies.mmd"
        class_puml = output_dir / f"{alias}_classes.puml"
        summary_json = output_dir / f"{alias}_summary.json"
        index_md = output_dir / "README.md"

        scope_title = f"UML scope: {scope_kind}::{target or 'repo'}"
        summary = build_scope_summary(scope_kind, target, scope_modules)

        write_text(component_puml, render_component_plantuml(f"{scope_title} / component overview", scope_modules, group_by="directory"))
        write_text(dependency_mmd, render_dependency_mermaid(f"{scope_title} / dependencies", scope_modules))
        write_text(class_puml, render_class_plantuml(f"{scope_title} / classes", scope_modules, include_methods=include_methods))
        write_json(summary_json, summary)
        write_text(
            index_md,
            render_markdown_index(
                title="UML Scope Diagram Set",
                description="Generated diagrams for a focused repository scope.",
                summary=summary,
                files=[component_puml.name, dependency_mmd.name, class_puml.name, summary_json.name],
                notes=scan.generated_notes,
            ),
        )

        return SkillResult(
            True,
            "uml_diagram_generate",
            data={
                "output_dir": str(output_dir),
                "scope": summary,
                "component_puml": str(component_puml),
                "dependency_mmd": str(dependency_mmd),
                "class_puml": str(class_puml),
                "summary_json": str(summary_json),
                "index_md": str(index_md),
            },
            logs=[f"Generated focused UML diagrams for {scope_kind}:{target or 'repo'}."],
        )
