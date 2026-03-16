"""Entry point: python3 -m claudeclockwork.mcp"""

from __future__ import annotations

import asyncio

from claudeclockwork.mcp.server import run_server

if __name__ == "__main__":
    asyncio.run(run_server())
