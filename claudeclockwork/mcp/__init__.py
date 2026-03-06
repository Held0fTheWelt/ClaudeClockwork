"""
claudeclockwork.mcp — optional MCP transport layer.

Import-safe: if the `mcp` package is not installed, importing this module
succeeds but `server.app` will be None and `mcp_available()` returns False.
"""

from __future__ import annotations


def mcp_available() -> bool:
    try:
        import mcp  # noqa: F401
        return True
    except ImportError:
        return False
