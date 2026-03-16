# MVP Phase 5 — MCP Layer

**Goal:** Expose Clockwork skills and resources via the Model Context Protocol (MCP). MCP is additive — removing it must not break the core CLI or plugin system.

---

## Definition of Done

- [X] `python3 -m claudeclockwork.mcp` starts a working STDIO MCP server
- [X] At least 3 native skills are callable as MCP Tools from an MCP client
- [X] Reference skills (`SKILL.md` assets) are accessible as MCP Resources
- [X] The core CLI (`claudeclockwork.cli`) works identically with MCP server stopped
- [X] All existing tests pass; 18 new MCP-specific tests added

---

## Architecture Decision

MCP is a **thin transport layer** over the existing skill system. It does not contain business logic.

```
MCP Client (Claude, cursor, etc.)
        │  STDIO (JSON-RPC)
        ▼
claudeclockwork.mcp.server
        │
        ▼
claudeclockwork.core.registry   ←  same registry as CLI
        │
        ▼
SkillExecutor                   ←  same executor as CLI
```

The MCP server imports and reuses `build_registry()`, `build_executor()`, `build_planner()` from `runtime.py`. No separate runtime path.

---

## Deliverables

### D5.1 — MCP Server Entry Point

**File:** `claudeclockwork/mcp/__init__.py`, `claudeclockwork/mcp/server.py`

```python
# claudeclockwork/mcp/server.py
# STDIO MCP server using fastmcp or the official MCP Python SDK

from mcp.server import Server
from claudeclockwork.runtime import build_registry, build_executor, build_planner

app = Server("clockwork")

@app.list_tools()
async def list_tools(): ...

@app.call_tool()
async def call_tool(name: str, arguments: dict): ...

@app.list_resources()
async def list_resources(): ...

@app.read_resource()
async def read_resource(uri: str): ...
```

Launch command: `python3 -m claudeclockwork.mcp`

---

### D5.2 — MCP Tool Export

Export the following skills as MCP Tools (Phase 3 native skills, stable interface):

| MCP Tool name | Clockwork skill | Description |
|---|---|---|
| `clockwork_registry_search` | `skill_registry_search` | Search available skills |
| `clockwork_qa_gate` | `qa_gate` | Run QA gate |
| `clockwork_manifest_validate` | `manifest_validate` | Validate a manifest |
| `clockwork_capability_map` | `capability_map_build` | Get full skill inventory |
| `clockwork_repo_validate` | `repo_validate` | Validate project structure |

Tool input schema is derived from skill manifest `inputs` field (if present) or accepts arbitrary JSON.

---

### D5.3 — MCP Resources

Expose reference skills as MCP Resources. Each `SKILL.md` in `.claude/skills/` becomes a readable resource:

```
clockwork://skills/<skill_id>   →  contents of <skill_id>/SKILL.md
clockwork://registry             →  live JSON from capability_map_build
clockwork://manifests/<skill_id> →  raw manifest.json content
```

---

### D5.4 — MCP Prompts

Expose key workflow playbooks as MCP Prompts:

| Prompt name | Source |
|---|---|
| `clockwork_qa_workflow` | `.claude/skills/playbooks/` |
| `clockwork_evidence_pipeline` | `.claude/skills/playbooks/` |
| `clockwork_new_skill` | Standard scaffold + validate sequence |

---

### D5.5 — Local STDIO Plugin MCPs

Wire `plugins/filesystem/plugin.json` and `plugins/git/plugin.json` to actual STDIO MCP servers (e.g. `@modelcontextprotocol/server-filesystem`, `@modelcontextprotocol/server-git`). These run as child processes managed by the plugin lifecycle hooks from Phase 4.

Optional in Phase 5 — can be deferred to a Phase 5.1 if external MCP server installation is not yet set up.

---

### D5.6 — MCP Client Adapter

**File:** `claudeclockwork/mcp/client.py`

Thin wrapper so Clockwork skills can call external MCP servers as tool sources:

```python
class MCPClientAdapter:
    def call_tool(self, server_name: str, tool_name: str, arguments: dict) -> dict: ...
    def list_tools(self, server_name: str) -> list[dict]: ...
```

Used by future skills that delegate to external MCP tools.

---

## Tests

```python
# tests/test_mcp_server.py

import asyncio
from claudeclockwork.mcp.server import app

async def test_mcp_lists_clockwork_tools():
    tools = await app.list_tools_handler()
    tool_names = {t.name for t in tools}
    assert "clockwork_registry_search" in tool_names
    assert "clockwork_qa_gate" in tool_names

async def test_mcp_calls_registry_search():
    result = await app.call_tool_handler("clockwork_registry_search", {"query": "qa"})
    assert result is not None
    assert len(result) > 0

async def test_mcp_reads_skill_resource():
    content = await app.read_resource_handler("clockwork://registry")
    import json
    data = json.loads(content)
    assert "manifest_skill_count" in data
```

---

## Dependencies

- Phase 3 (native skills) — MCP tools wrap native skills directly
- Phase 4 (plugin runtime) — local STDIO MCPs use plugin lifecycle hooks
- External dependency: `mcp` Python SDK (`pip install mcp`) or `fastmcp`

## Notes

- MCP is optional at import time — guard with `try: import mcp` so the core package installs without MCP
- `pyproject.toml` (when created): MCP as optional extra — `pip install claudeclockwork[mcp]`
- The STDIO MCP server is stateless per request — it builds registry fresh each call or caches with TTL

## Files Changed / Created

| File | Change |
|------|--------|
| `claudeclockwork/mcp/__init__.py` | New MCP package |
| `claudeclockwork/mcp/server.py` | New STDIO MCP server |
| `claudeclockwork/mcp/client.py` | New MCP client adapter |
| `claudeclockwork/mcp/__main__.py` | Entry point for `python3 -m claudeclockwork.mcp` |
| `tests/test_mcp_server.py` | New test file |
