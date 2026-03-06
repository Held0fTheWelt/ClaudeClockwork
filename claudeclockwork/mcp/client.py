"""
claudeclockwork.mcp.client — thin adapter for calling external MCP servers.

This stub is the foundation for future skills that delegate to external MCP
tools. The implementation uses subprocess STDIO transport matching the MCP spec.
"""

from __future__ import annotations

from typing import Any


class MCPClientAdapter:
    """
    Thin wrapper so Clockwork skills can call external MCP servers as tool sources.

    The adapter is intentionally lightweight — it does not maintain a persistent
    connection. Each `call_tool` / `list_tools` call may start a fresh STDIO
    subprocess or reuse an existing one depending on the server implementation.
    """

    def __init__(self, server_command: list[str] | None = None) -> None:
        """
        Args:
            server_command: Command to launch the MCP server process
                            (e.g. ["npx", "@modelcontextprotocol/server-filesystem", "."]).
                            When None, the adapter is in stub mode and returns empty results.
        """
        self._server_command = server_command

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Call a tool on the remote MCP server.

        Returns the tool result dict. Raises RuntimeError if the server is
        not configured or the call fails.
        """
        if self._server_command is None:
            raise RuntimeError(
                "MCPClientAdapter is in stub mode (no server_command). "
                "Provide a server_command to enable real MCP calls."
            )
        # Full STDIO transport implementation is a Phase 5.1 deliverable.
        # For now, raise to make the missing implementation explicit.
        raise NotImplementedError(
            f"STDIO transport for tool {tool_name!r} not yet implemented. "
            "See Phase 5.1 in the roadmap."
        )

    def list_tools(self) -> list[dict[str, Any]]:
        """
        List tools available on the remote MCP server.

        Returns empty list in stub mode.
        """
        if self._server_command is None:
            return []
        raise NotImplementedError(
            "STDIO transport list_tools not yet implemented. See Phase 5.1."
        )
