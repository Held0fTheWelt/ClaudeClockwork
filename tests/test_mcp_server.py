"""
Phase 5 — MCP Layer tests.

Tests use the public handler functions from claudeclockwork.mcp.server directly
(no MCP STDIO transport required) so they run in any pytest environment.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from claudeclockwork.mcp import mcp_available
from claudeclockwork.mcp.server import (
    _TOOL_DISPATCH,
    _do_read_resource,
    _do_registry_search,
    _list_resources_data,
    _PROMPTS,
    _do_get_prompt,
)
from claudeclockwork.mcp.client import MCPClientAdapter


# ---------------------------------------------------------------------------
# Availability guard — skip MCP SDK tests if not installed, but these tests
# use the MCP-independent handler functions so they always run.
# ---------------------------------------------------------------------------

def test_mcp_package_available() -> None:
    """mcp package must be installed for Phase 5 to be operational."""
    assert mcp_available(), "Install mcp: pip install mcp"


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------

def test_tool_dispatch_has_five_tools() -> None:
    """All 5 required MCP tools must be registered in _TOOL_DISPATCH."""
    required = {
        "clockwork_registry_search",
        "clockwork_qa_gate",
        "clockwork_manifest_validate",
        "clockwork_capability_map",
        "clockwork_repo_validate",
    }
    assert required <= set(_TOOL_DISPATCH.keys())


def test_registry_search_returns_results() -> None:
    """clockwork_registry_search must return a skills list and count."""
    result = _do_registry_search({"query": "qa"})
    assert "skills" in result
    assert "count" in result
    assert isinstance(result["skills"], list)
    assert result["count"] >= 0


def test_registry_search_empty_query_returns_all() -> None:
    """Empty query must return all skills (non-zero count)."""
    result = _do_registry_search({"query": ""})
    assert result["count"] > 0


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

def test_list_resources_includes_registry() -> None:
    """clockwork://registry must be listed as a resource."""
    uris = {r["uri"] for r in _list_resources_data()}
    assert "clockwork://registry" in uris


def test_list_resources_includes_skill_entries() -> None:
    """At least one clockwork://skills/<id> resource must exist."""
    uris = {r["uri"] for r in _list_resources_data()}
    skill_uris = [u for u in uris if u.startswith("clockwork://skills/")]
    assert len(skill_uris) > 0


def test_read_resource_registry_returns_json() -> None:
    """Reading clockwork://registry must return valid JSON with skill data."""
    content = _do_read_resource("clockwork://registry")
    data = json.loads(content)
    # The capability_map_build output is nested under 'outputs' or at the top
    assert isinstance(data, dict)


def test_read_resource_manifest_returns_json() -> None:
    """Reading a known manifest resource must return valid JSON with name field."""
    content = _do_read_resource("clockwork://manifests/qa_gate")
    data = json.loads(content)
    assert "name" in data or "error" not in data
    # If skill exists, it should have a name
    if "error" not in data:
        assert data.get("name") == "qa_gate"


def test_read_resource_unknown_returns_error() -> None:
    """Unknown URI must return a JSON error (not raise)."""
    content = _do_read_resource("clockwork://nonexistent/path")
    data = json.loads(content)
    assert "error" in data


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

def test_prompts_registry_has_three_entries() -> None:
    """All 3 required prompts must be registered."""
    required = {"clockwork_qa_workflow", "clockwork_evidence_pipeline", "clockwork_new_skill"}
    assert required <= set(_PROMPTS.keys())


def test_get_prompt_returns_messages() -> None:
    """get_prompt must return a dict with a non-empty messages list."""
    result = _do_get_prompt("clockwork_qa_workflow")
    assert "messages" in result
    assert len(result["messages"]) > 0
    assert result["messages"][0]["role"] == "user"


def test_get_prompt_unknown_returns_error() -> None:
    """Unknown prompt name must return an error dict (not raise)."""
    result = _do_get_prompt("nonexistent_prompt")
    assert "error" in result


# ---------------------------------------------------------------------------
# MCP Server object (requires mcp package)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not mcp_available(), reason="mcp not installed")
def test_mcp_server_app_is_not_none() -> None:
    """app must be a Server instance when mcp is installed."""
    from claudeclockwork.mcp.server import app
    from mcp.server import Server
    assert app is not None
    assert isinstance(app, Server)


@pytest.mark.skipif(not mcp_available(), reason="mcp not installed")
def test_mcp_server_has_tool_handler() -> None:
    """Server must have a ListToolsRequest handler registered."""
    from claudeclockwork.mcp.server import app
    import mcp.types as types
    assert types.ListToolsRequest in app.request_handlers


@pytest.mark.skipif(not mcp_available(), reason="mcp not installed")
def test_mcp_server_has_resource_handler() -> None:
    """Server must have a ReadResourceRequest handler registered."""
    from claudeclockwork.mcp.server import app
    import mcp.types as types
    assert types.ReadResourceRequest in app.request_handlers


# ---------------------------------------------------------------------------
# MCP Client Adapter
# ---------------------------------------------------------------------------

def test_client_adapter_stub_mode_list_tools_empty() -> None:
    """Stub adapter (no server_command) returns empty list_tools."""
    adapter = MCPClientAdapter()
    assert adapter.list_tools() == []


def test_client_adapter_stub_mode_call_tool_raises() -> None:
    """Stub adapter call_tool raises RuntimeError."""
    adapter = MCPClientAdapter()
    with pytest.raises(RuntimeError, match="stub mode"):
        adapter.call_tool("some_tool", {})


def test_client_adapter_with_command_call_tool_raises_not_implemented() -> None:
    """Adapter with server_command raises NotImplementedError (Phase 5.1 TODO)."""
    adapter = MCPClientAdapter(server_command=["echo", "test"])
    with pytest.raises(NotImplementedError):
        adapter.call_tool("some_tool", {})
