"""Plain-function bundle builders ported from the v17 skill wrappers."""

from __future__ import annotations

from pathlib import Path

from clockwork.tools.how_it_works_shared import (
    build_how_it_works_payload,
    write_how_it_works_bundle,
)
from clockwork.tools.uml_review_shared import (
    build_review_context,
    write_context_bundle,
    write_review_site,
)
from clockwork.tools.uml_shared import (
    UmlSkillError,
    build_catalog,
    build_scope_summary,
    expand_focus_modules,
    find_scope_modules,
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

GENERATED_ROOT = Path("UML") / "generated"


def _resolve_out(repo_root: Path, output_dir: str | Path | None, default_leaf: str) -> Path:
    if output_dir:
        return Path(output_dir).resolve()
    return (repo_root / GENERATED_ROOT / default_leaf).resolve()


def build_scope_catalog(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    include_tests: bool = False,
) -> dict:
    repo_root = Path(repo_root).resolve()
    out = _resolve_out(repo_root, output_dir, "catalog")
    scan = scan_repository(repo_root, include_tests=include_tests)
    payload = build_catalog(scan)
    catalog_json = out / "uml_scope_catalog.json"
    catalog_md = out / "uml_scope_catalog.md"
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
    return {
        "output_dir": str(out),
        "catalog_json": str(catalog_json),
        "catalog_md": str(catalog_md),
        "module_count": scan.module_count,
        "class_count": scan.class_count,
        "languages": scan.languages,
    }


def build_repo_bundle(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    include_tests: bool = False,
    max_directory_bundles: int = 6,
) -> dict:
    repo_root = Path(repo_root).resolve()
    out = _resolve_out(repo_root, output_dir, "repo_bundle")
    scan = scan_repository(repo_root, include_tests=include_tests)
    repo_summary = build_scope_summary("repo", None, scan.modules)
    top_directories = rank_directories(scan)[:max_directory_bundles]

    repo_component = out / "repo_component_overview.puml"
    repo_dependencies = out / "repo_dependency_overview.mmd"
    repo_classes = out / "repo_class_overview.puml"
    bundle_summary = out / "repo_bundle_summary.json"
    bundle_index = out / "README.md"

    write_text(
        repo_component,
        render_component_plantuml(
            "Repository UML / component overview", scan.modules, group_by="topdir"
        ),
    )
    write_text(
        repo_dependencies,
        render_dependency_mermaid("Repository UML / dependency overview", scan.modules),
    )
    write_text(
        repo_classes,
        render_class_plantuml(
            "Repository UML / class overview", scan.modules, include_methods=False
        ),
    )

    generated_files = [repo_component.name, repo_dependencies.name, repo_classes.name]
    slices: list[dict] = []
    for row in top_directories:
        directory = str(row["path"])
        if directory == ".":
            continue
        scope_modules = [
            m
            for m in scan.modules
            if m.file_path.startswith(directory + "/") or m.relative_dir == directory
        ]
        if not scope_modules:
            continue
        alias = sanitize_alias(f"dir_{directory}")
        component_file = out / f"{alias}_component.puml"
        class_file = out / f"{alias}_classes.puml"
        write_text(
            component_file,
            render_component_plantuml(
                f"Directory UML / {directory} / components",
                scope_modules,
                group_by="directory",
            ),
        )
        write_text(
            class_file,
            render_class_plantuml(
                f"Directory UML / {directory} / classes",
                scope_modules,
                include_methods=False,
            ),
        )
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

    write_json(
        bundle_summary,
        {
            "repo_summary": repo_summary,
            "top_directories": top_directories,
            "slices": slices,
            "notes": scan.generated_notes,
        },
    )
    write_text(
        bundle_index,
        render_markdown_index(
            title="Repository UML Bundle",
            description="Repository-wide UML overview with directory-level slices.",
            summary=repo_summary,
            files=generated_files + [bundle_summary.name],
            notes=scan.generated_notes,
        ),
    )
    return {
        "output_dir": str(out),
        "bundle_index": str(bundle_index),
        "module_count": scan.module_count,
        "class_count": scan.class_count,
        "repo_component": str(repo_component),
        "repo_dependencies": str(repo_dependencies),
        "repo_classes": str(repo_classes),
        "summary_json": str(bundle_summary),
    }


def build_focus_bundle(
    repo_root: str | Path,
    scope_kind: str,
    target: str,
    neighbor_depth: int = 2,
    include_methods: bool = True,
    include_tests: bool = False,
    output_dir: str | Path | None = None,
) -> dict:
    if scope_kind == "repo":
        raise UmlSkillError("Focused bundles require directory, module, or symbol scope.")
    repo_root = Path(repo_root).resolve()
    out = _resolve_out(repo_root, output_dir, f"focus_{sanitize_alias(scope_kind)}_{sanitize_alias(target)}")
    scan = scan_repository(repo_root, include_tests=include_tests)
    base_modules = find_scope_modules(scan, scope_kind, target)
    if not base_modules:
        raise UmlSkillError(f"No modules found for {scope_kind} scope: {target}")
    modules = expand_focus_modules(scan, base_modules, depth=neighbor_depth)
    summary = build_scope_summary(scope_kind, target, modules)

    component_file = out / "focus_component_overview.puml"
    dependency_file = out / "focus_dependency_overview.mmd"
    class_file = out / "focus_class_overview.puml"
    summary_file = out / "focus_summary.json"
    index_file = out / "README.md"
    write_text(component_file, render_component_plantuml("Focused component overview", modules))
    write_text(dependency_file, render_dependency_mermaid("Focused dependency overview", modules))
    write_text(
        class_file,
        render_class_plantuml("Focused class overview", modules, include_methods=include_methods),
    )
    write_json(summary_file, {"scope": summary, "notes": scan.generated_notes})
    write_text(
        index_file,
        render_markdown_index(
            title="Focused UML Bundle",
            description="Focused UML bundle with neighbor expansion.",
            summary=summary,
            files=[
                component_file.name,
                dependency_file.name,
                class_file.name,
                summary_file.name,
            ],
            notes=scan.generated_notes,
        ),
    )
    return {
        "output_dir": str(out),
        "scope": summary,
        "component_puml": str(component_file),
        "dependency_mmd": str(dependency_file),
        "class_puml": str(class_file),
        "summary_json": str(summary_file),
    }


def generate_diagrams(
    repo_root: str | Path,
    scope_kind: str = "repo",
    target: str | None = None,
    include_methods: bool | None = None,
    neighbor_depth: int | None = None,
    include_tests: bool = False,
    output_dir: str | Path | None = None,
) -> dict:
    repo_root = Path(repo_root).resolve()
    out = _resolve_out(repo_root, output_dir, f"diagrams_{sanitize_alias(scope_kind)}")
    scan = scan_repository(repo_root, include_tests=include_tests)
    if scope_kind == "repo":
        modules = list(scan.modules)
    else:
        modules = find_scope_modules(scan, scope_kind, target)
        if not modules:
            raise UmlSkillError(f"No modules found for {scope_kind} scope: {target}")
        modules = expand_focus_modules(scan, modules, depth=neighbor_depth or 0)
    summary = build_scope_summary(scope_kind, target, modules)
    component_file = out / "component_overview.puml"
    dependency_file = out / "dependency_overview.mmd"
    class_file = out / "class_overview.puml"
    index_file = out / "README.md"
    write_text(component_file, render_component_plantuml("Component overview", modules))
    write_text(dependency_file, render_dependency_mermaid("Dependency overview", modules))
    write_text(
        class_file,
        render_class_plantuml(
            "Class overview", modules, include_methods=bool(include_methods)
        ),
    )
    write_text(
        index_file,
        render_markdown_index(
            title="UML Diagram Set",
            description="Generated component, dependency, and class diagrams.",
            summary=summary,
            files=[component_file.name, dependency_file.name, class_file.name],
            notes=scan.generated_notes,
        ),
    )
    return {
        "output_dir": str(out),
        "scope": summary,
        "component_puml": str(component_file),
        "dependency_mmd": str(dependency_file),
        "class_puml": str(class_file),
        "index_md": str(index_file),
    }


def build_review_context_bundle(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    include_tests: bool = False,
    neighbor_depth: int = 1,
    max_neighbors: int = 10,
) -> dict:
    repo_root = Path(repo_root).resolve()
    out = _resolve_out(repo_root, output_dir, "review_context")
    scan = scan_repository(repo_root, include_tests=include_tests)
    payload = build_review_context(
        scan, neighbor_depth=neighbor_depth, max_neighbors=max_neighbors
    )
    files = write_context_bundle(out, payload)
    return {
        "output_dir": str(out),
        "module_count": scan.module_count,
        "class_count": scan.class_count,
        **files,
    }


def build_review_site_bundle(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    site_title: str = "UML Review Explorer",
    include_tests: bool = False,
    neighbor_depth: int = 1,
    max_neighbors: int = 10,
    include_guides: bool = True,
) -> dict:
    repo_root = Path(repo_root).resolve()
    out = _resolve_out(repo_root, output_dir, "review_site")
    scan = scan_repository(repo_root, include_tests=include_tests)
    context = build_review_context(
        scan, neighbor_depth=neighbor_depth, max_neighbors=max_neighbors
    )
    guide = (
        build_how_it_works_payload(scan, context_payload=context, repo_root=repo_root)
        if include_guides
        else None
    )
    files = write_review_site(out, context, site_title=site_title, guide_payload=guide)
    return {
        "output_dir": str(out),
        "module_count": scan.module_count,
        "class_count": scan.class_count,
        **files,
    }


def build_how_it_works_bundle(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    include_tests: bool = False,
    neighbor_depth: int = 1,
    max_neighbors: int = 10,
) -> dict:
    repo_root = Path(repo_root).resolve()
    out = _resolve_out(repo_root, output_dir, "how_it_works")
    scan = scan_repository(repo_root, include_tests=include_tests)
    context = build_review_context(
        scan, neighbor_depth=neighbor_depth, max_neighbors=max_neighbors
    )
    payload = build_how_it_works_payload(scan, context_payload=context, repo_root=repo_root)
    files = write_how_it_works_bundle(out, payload)
    return {
        "output_dir": str(out),
        "module_count": scan.module_count,
        "class_count": scan.class_count,
        **files,
    }
