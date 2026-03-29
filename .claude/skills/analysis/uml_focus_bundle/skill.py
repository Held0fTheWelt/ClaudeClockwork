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


class UmlFocusBundleSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        scope_kind = str(kwargs.get("scope_kind") or "symbol").strip().lower()
        if scope_kind == "repo":
            return SkillResult(False, "uml_focus_bundle", error="uml_focus_bundle is intended for directory/module/symbol scopes, not repo.")
        target = kwargs.get("target")
        if not target:
            return SkillResult(False, "uml_focus_bundle", error="Missing required target for uml_focus_bundle.")

        neighbor_depth = int(kwargs.get("neighbor_depth", 2))
        include_methods = bool(kwargs.get("include_methods", True))
        scan = scan_repository(repo_root, include_tests=bool(kwargs.get("include_tests", False)))

        try:
            base_modules = find_scope_modules(scan, scope_kind, target)
        except UmlSkillError as exc:
            return SkillResult(False, "uml_focus_bundle", error=str(exc))

        if not base_modules:
            return SkillResult(False, "uml_focus_bundle", error=f"No modules found for scope {scope_kind}:{target}")

        scope_modules = expand_focus_modules(scan, base_modules, depth=neighbor_depth)
        alias = sanitize_alias(f"focus_{scope_kind}_{target}")
        output_dir = Path(kwargs.get("output_dir") or (repo_root / "Docs" / "uml" / "focus" / alias)).resolve()

        summary = build_scope_summary(scope_kind, target, scope_modules)
        component_overview = output_dir / f"{alias}_component_overview.puml"
        neighborhood_dependencies = output_dir / f"{alias}_neighborhood.mmd"
        focused_classes = output_dir / f"{alias}_focused_classes.puml"
        bundle_summary = output_dir / f"{alias}_bundle.json"
        bundle_index = output_dir / "README.md"

        write_text(component_overview, render_component_plantuml(f"Focus bundle / {scope_kind}:{target} / components", scope_modules, group_by="directory"))
        write_text(neighborhood_dependencies, render_dependency_mermaid(f"Focus bundle / {scope_kind}:{target} / neighborhood", scope_modules))
        write_text(focused_classes, render_class_plantuml(f"Focus bundle / {scope_kind}:{target} / classes", scope_modules, include_methods=include_methods))
        write_json(bundle_summary, {"summary": summary, "notes": scan.generated_notes})
        write_text(
            bundle_index,
            render_markdown_index(
                title="UML Focus Bundle",
                description="Focused UML bundle with neighborhood expansion around the chosen scope.",
                summary=summary,
                files=[component_overview.name, neighborhood_dependencies.name, focused_classes.name, bundle_summary.name],
                notes=scan.generated_notes,
            ),
        )

        return SkillResult(
            True,
            "uml_focus_bundle",
            data={
                "output_dir": str(output_dir),
                "bundle_index": str(bundle_index),
                "bundle_summary": str(bundle_summary),
                "diagrams": [
                    str(component_overview),
                    str(neighborhood_dependencies),
                    str(focused_classes),
                ],
                "scope": summary,
            },
            logs=[f"Built focused UML bundle for {scope_kind}:{target}."],
        )
