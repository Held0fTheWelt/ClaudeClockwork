"""
claudeclockwork.mcp.server — STDIO MCP server exposing Clockwork skills.

This module is a thin transport layer over the existing skill system.
All business logic lives in claudeclockwork.core.*; this module only
translates MCP protocol messages into skill executor calls.

MCP is optional: the module can be imported even without the `mcp` package,
but `app` will be None and `run_server()` will raise ImportError.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Resolve project root from package location: claudeclockwork/mcp/server.py → root
# parents[0]=mcp/, parents[1]=claudeclockwork/, parents[2]=project root
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# MCP-independent business-logic handlers (testable without mcp installed)
# ---------------------------------------------------------------------------

from claudeclockwork.runtime import build_executor, build_registry


def _registry():
    return build_registry(_PROJECT_ROOT)


def _executor():
    return build_executor(_PROJECT_ROOT)


# --- Tool handlers (sync wrappers; MCP decorators call async versions) ------

def _do_registry_search(arguments: dict) -> dict:
    query = arguments.get("query", "")
    registry = _registry()
    results = registry.search(query) if query else registry.list_skills()
    return {
        "skills": [{"name": m.name, "category": m.category, "description": m.description} for m in results],
        "count": len(results),
    }


def _do_qa_gate(arguments: dict) -> dict:
    from claudeclockwork.bridge import run_manifest_skill
    result = run_manifest_skill(
        {"request_id": "mcp", "skill_id": "qa_gate", "inputs": arguments},
        _PROJECT_ROOT,
    )
    return result or {"status": "fail", "errors": ["skill not found"]}


def _do_manifest_validate(arguments: dict) -> dict:
    from claudeclockwork.bridge import run_manifest_skill
    result = run_manifest_skill(
        {"request_id": "mcp", "skill_id": "manifest_validate", "inputs": arguments},
        _PROJECT_ROOT,
    )
    return result or {"status": "fail", "errors": ["skill not found"]}


def _do_capability_map(arguments: dict) -> dict:
    from claudeclockwork.bridge import run_manifest_skill
    result = run_manifest_skill(
        {"request_id": "mcp", "skill_id": "capability_map_build", "inputs": arguments},
        _PROJECT_ROOT,
    )
    return result or {"status": "fail", "errors": ["skill not found"]}


def _do_repo_validate(arguments: dict) -> dict:
    from claudeclockwork.bridge import run_manifest_skill
    result = run_manifest_skill(
        {"request_id": "mcp", "skill_id": "repo_validate", "inputs": arguments},
        _PROJECT_ROOT,
    )
    return result or {"status": "fail", "errors": ["skill not found"]}


_TOOL_DISPATCH: dict[str, Any] = {
    "clockwork_registry_search": _do_registry_search,
    "clockwork_qa_gate": _do_qa_gate,
    "clockwork_manifest_validate": _do_manifest_validate,
    "clockwork_capability_map": _do_capability_map,
    "clockwork_repo_validate": _do_repo_validate,
}

# --- Resource handlers -------------------------------------------------------

def _do_read_resource(uri: str) -> str:
    uri_str = str(uri)
    if uri_str == "clockwork://registry":
        result = _do_capability_map({})
        return json.dumps(result.get("outputs", result), indent=2, ensure_ascii=False)

    if uri_str.startswith("clockwork://skills/"):
        skill_id = uri_str[len("clockwork://skills/"):]
        skill_dir = _PROJECT_ROOT / ".claude" / "skills"
        for candidate in skill_dir.rglob(f"{skill_id}/SKILL.md"):
            return candidate.read_text(encoding="utf-8")
        return f"# {skill_id}\n\nNo SKILL.md found for this skill.\n"

    if uri_str.startswith("clockwork://manifests/"):
        skill_id = uri_str[len("clockwork://manifests/"):]
        registry = _registry()
        manifest = registry.get_manifest(skill_id)
        if manifest is None:
            return json.dumps({"error": f"Unknown skill: {skill_id}"})
        return json.dumps({
            "name": manifest.name,
            "version": manifest.version,
            "category": manifest.category,
            "description": manifest.description,
            "entrypoint": manifest.entrypoint,
            "permissions": manifest.permissions,
            "metadata": manifest.metadata,
        }, indent=2, ensure_ascii=False)

    return json.dumps({"error": f"Unknown resource URI: {uri_str}"})


def _list_resources_data() -> list[dict]:
    resources = [
        {
            "uri": "clockwork://registry",
            "name": "Clockwork Skill Registry",
            "description": "Live JSON export of all registered skills and their metadata.",
            "mimeType": "application/json",
        }
    ]
    skill_dir = _PROJECT_ROOT / ".claude" / "skills"
    for skill_md in sorted(skill_dir.rglob("SKILL.md")):
        skill_id = skill_md.parent.name
        resources.append({
            "uri": f"clockwork://skills/{skill_id}",
            "name": f"Skill: {skill_id}",
            "description": f"Reference documentation for skill {skill_id!r}.",
            "mimeType": "text/markdown",
        })
        resources.append({
            "uri": f"clockwork://manifests/{skill_id}",
            "name": f"Manifest: {skill_id}",
            "description": f"Raw manifest.json for skill {skill_id!r}.",
            "mimeType": "application/json",
        })
    return resources


# --- Prompt handlers ----------------------------------------------------------

_PROMPTS: dict[str, dict] = {
    "clockwork_qa_workflow": {
        "name": "clockwork_qa_workflow",
        "description": "Run the full QA gate + manifest validation + repo validate sequence.",
        "text": (
            "Run the Clockwork QA workflow:\n"
            "1. Call `clockwork_qa_gate` with no inputs to run the pre-flight checks.\n"
            "2. Call `clockwork_manifest_validate` to verify all skill manifests are valid.\n"
            "3. Call `clockwork_repo_validate` to verify repository structure.\n"
            "4. Report the combined result — only proceed with implementation if all three pass."
        ),
    },
    "clockwork_evidence_pipeline": {
        "name": "clockwork_evidence_pipeline",
        "description": "Build an evidence bundle from current run artifacts.",
        "text": (
            "Run the Clockwork evidence pipeline:\n"
            "1. Identify the list of artifact paths to include.\n"
            "2. Call the `evidence_bundle_build` skill with the artifact list.\n"
            "3. The skill will produce a SHA256-verified zip bundle.\n"
            "4. Verify the bundle checksum matches the reported SHA256."
        ),
    },
    "clockwork_new_skill": {
        "name": "clockwork_new_skill",
        "description": "Scaffold and validate a new Clockwork skill.",
        "text": (
            "Create a new Clockwork skill:\n"
            "1. Call `clockwork_registry_search` with the proposed skill name to check for duplicates.\n"
            "2. Use the `skill_scaffold` skill to generate the manifest.json and skill.py.\n"
            "3. Call `clockwork_manifest_validate` to verify the new manifest is valid.\n"
            "4. Run the new skill smoke test: inputs={} should return status=ok or a clear error."
        ),
    },
}


def _do_get_prompt(name: str, arguments: dict | None = None) -> dict:
    prompt = _PROMPTS.get(name)
    if prompt is None:
        return {"error": f"Unknown prompt: {name}"}
    return {
        "description": prompt["description"],
        "messages": [{"role": "user", "content": {"type": "text", "text": prompt["text"]}}],
    }


# ---------------------------------------------------------------------------
# MCP server wiring (only built when `mcp` is installed)
# ---------------------------------------------------------------------------

try:
    import mcp.types as types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server

    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False
    app = None  # type: ignore[assignment]


if _MCP_AVAILABLE:
    app = Server("clockwork")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:  # type: ignore[return]
        return [
            types.Tool(
                name="clockwork_registry_search",
                description="Search Clockwork skill registry by keyword.",
                inputSchema={
                    "type": "object",
                    "properties": {"query": {"type": "string", "description": "Search keyword"}},
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="clockwork_qa_gate",
                description="Run the Clockwork QA gate (pre-flight checks).",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": True},
            ),
            types.Tool(
                name="clockwork_manifest_validate",
                description="Validate all skill manifests in the registry.",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": True},
            ),
            types.Tool(
                name="clockwork_capability_map",
                description="Return the full skill capability map (all skills, categories, counts).",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": True},
            ),
            types.Tool(
                name="clockwork_repo_validate",
                description="Validate the Clockwork project repository structure.",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": True},
            ),
        ]

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> dict:  # type: ignore[return]
        handler = _TOOL_DISPATCH.get(name)
        if handler is None:
            return {"error": f"Unknown tool: {name}"}
        return handler(arguments)

    @app.list_resources()
    async def list_resources() -> list[types.Resource]:  # type: ignore[return]
        return [
            types.Resource(
                uri=r["uri"],  # type: ignore[arg-type]
                name=r["name"],
                description=r.get("description"),
                mimeType=r.get("mimeType"),
            )
            for r in _list_resources_data()
        ]

    @app.read_resource()
    async def read_resource(uri) -> str:
        return _do_read_resource(str(uri))

    @app.list_prompts()
    async def list_prompts() -> list[types.Prompt]:  # type: ignore[return]
        return [
            types.Prompt(
                name=p["name"],
                description=p.get("description"),
            )
            for p in _PROMPTS.values()
        ]

    @app.get_prompt()
    async def get_prompt(name: str, arguments: dict | None = None) -> types.GetPromptResult:
        data = _do_get_prompt(name, arguments)
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=msg["content"]["text"]),
            )
            for msg in data.get("messages", [])
        ]
        return types.GetPromptResult(
            description=data.get("description", ""),
            messages=messages,
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def run_server() -> None:
    if not _MCP_AVAILABLE:
        raise ImportError(
            "The 'mcp' package is required to run the MCP server. "
            "Install it with: pip install mcp"
        )
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )
