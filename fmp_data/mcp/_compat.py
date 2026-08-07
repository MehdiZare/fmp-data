"""Compatibility layer across MCP SDK major versions.

The MCP Python SDK renamed its high-level server class in 2.0:
``mcp.server.fastmcp.FastMCP`` became ``mcp.server.MCPServer``. The parts of
the API this package relies on — the constructor's ``name`` argument,
``add_tool(fn, name=..., description=...)`` and ``run(transport=...)`` — are
identical across both, so resolving the class at import time is enough to
support either SDK.
"""

from __future__ import annotations

from typing import Any, cast

# The concrete class differs per SDK major, so the public surface is typed as
# Any rather than pinning callers to one SDK's symbol.
MCPServerType = Any

__all__ = ["MCPServerType", "import_mcp_server_class", "mcp_server_available"]


def import_mcp_server_class() -> type[Any]:
    """Return the installed SDK's high-level server class.

    Raises:
        ImportError: if no supported MCP SDK is installed.
    """
    # Both branches are cast: mypy runs without the mcp extra installed, so
    # neither symbol resolves to a real class there.
    try:  # MCP SDK >= 2.0
        from mcp.server import MCPServer
    except ImportError:
        pass
    else:
        return cast(type[Any], MCPServer)

    # MCP SDK 1.x
    from mcp.server.fastmcp import FastMCP

    return cast(type[Any], FastMCP)


def mcp_server_available() -> bool:
    """Return True when a supported MCP SDK is importable."""
    try:
        import_mcp_server_class()
    except ImportError:
        return False
    return True
