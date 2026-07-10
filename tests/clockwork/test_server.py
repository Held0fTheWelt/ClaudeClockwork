import asyncio

EXPECTED_TOOLS = {
    "uml_scope_catalog",
    "uml_repo_bundle",
    "uml_focus_bundle",
    "uml_diagram_generate",
    "review_context_build",
    "review_site_build",
    "how_it_works_build",
    "architecture_gate",
}


def test_server_exposes_all_tools():
    from clockwork.server import mcp

    tools = asyncio.run(mcp.list_tools())
    assert EXPECTED_TOOLS <= {tool.name for tool in tools}


def test_architecture_gate_tool_runs_on_fixture(tmp_path):
    from clockwork.server import architecture_gate

    result = architecture_gate(repo_root=str(tmp_path))
    assert result == {"passed": True, "violations": []}
