"""Clockwork MCP server - deterministic architecture tooling over stdio."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from clockwork.tools import bundles
from clockwork.tools.gates import check_architecture_docs

mcp = FastMCP("clockwork")


@mcp.tool()
def uml_scope_catalog(
    repo_root: str = ".", output_dir: str | None = None, include_tests: bool = False
) -> dict:
    """Scan a repository and write the UML scope catalog."""
    return bundles.build_scope_catalog(
        repo_root, output_dir=output_dir, include_tests=include_tests
    )


@mcp.tool()
def uml_repo_bundle(
    repo_root: str = ".",
    output_dir: str | None = None,
    include_tests: bool = False,
    max_directory_bundles: int = 6,
) -> dict:
    """Repository-wide UML overview with directory-level slices."""
    return bundles.build_repo_bundle(
        repo_root,
        output_dir=output_dir,
        include_tests=include_tests,
        max_directory_bundles=max_directory_bundles,
    )


@mcp.tool()
def uml_focus_bundle(
    repo_root: str,
    scope_kind: str,
    target: str,
    neighbor_depth: int = 2,
    include_methods: bool = True,
    include_tests: bool = False,
    output_dir: str | None = None,
) -> dict:
    """Focused UML bundle around a directory, module, or symbol."""
    return bundles.build_focus_bundle(
        repo_root,
        scope_kind,
        target,
        neighbor_depth=neighbor_depth,
        include_methods=include_methods,
        include_tests=include_tests,
        output_dir=output_dir,
    )


@mcp.tool()
def uml_diagram_generate(
    repo_root: str = ".",
    scope_kind: str = "repo",
    target: str | None = None,
    include_methods: bool | None = None,
    neighbor_depth: int | None = None,
    include_tests: bool = False,
    output_dir: str | None = None,
) -> dict:
    """Generate component/dependency/class diagrams for a scope."""
    return bundles.generate_diagrams(
        repo_root,
        scope_kind=scope_kind,
        target=target,
        include_methods=include_methods,
        neighbor_depth=neighbor_depth,
        include_tests=include_tests,
        output_dir=output_dir,
    )


@mcp.tool()
def review_context_build(
    repo_root: str = ".",
    output_dir: str | None = None,
    include_tests: bool = False,
    neighbor_depth: int = 1,
    max_neighbors: int = 10,
) -> dict:
    """Build the machine-readable review context bundle."""
    return bundles.build_review_context_bundle(
        repo_root,
        output_dir=output_dir,
        include_tests=include_tests,
        neighbor_depth=neighbor_depth,
        max_neighbors=max_neighbors,
    )


@mcp.tool()
def review_site_build(
    repo_root: str = ".",
    output_dir: str | None = None,
    site_title: str = "UML Review Explorer",
    include_tests: bool = False,
    neighbor_depth: int = 1,
    max_neighbors: int = 10,
    include_guides: bool = True,
) -> dict:
    """Build the static HTML review explorer site."""
    return bundles.build_review_site_bundle(
        repo_root,
        output_dir=output_dir,
        site_title=site_title,
        include_tests=include_tests,
        neighbor_depth=neighbor_depth,
        max_neighbors=max_neighbors,
        include_guides=include_guides,
    )


@mcp.tool()
def how_it_works_build(
    repo_root: str = ".",
    output_dir: str | None = None,
    include_tests: bool = False,
    neighbor_depth: int = 1,
    max_neighbors: int = 10,
) -> dict:
    """Build the how-it-works guide bundle for a repository."""
    return bundles.build_how_it_works_bundle(
        repo_root,
        output_dir=output_dir,
        include_tests=include_tests,
        neighbor_depth=neighbor_depth,
        max_neighbors=max_neighbors,
    )


@mcp.tool()
def architecture_gate(repo_root: str = ".") -> dict:
    """Run the architecture documentation gate; normative run is pytest."""
    violations = check_architecture_docs(repo_root)
    return {"passed": not violations, "violations": violations}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
