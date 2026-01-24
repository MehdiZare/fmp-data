# fmp_data/mcp/server.py
from __future__ import annotations

from collections.abc import Iterable, Sequence
import os
from pathlib import Path
from typing import TYPE_CHECKING

from fmp_data.exceptions import DependencyError

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

from fmp_data.client import FMPDataClient
from fmp_data.mcp.tool_loader import register_from_manifest
from fmp_data.mcp.utils import load_manifest_tools

# Accept either a single spec or an iterable of specs
ToolIterable = str | Sequence[str] | Iterable[str]


def create_app(tools: ToolIterable | None = None) -> FastMCP:
    """
    Build and return a :class:`FastMCP` server instance.

    Parameters
    ----------
    tools
        * **None** (default)    - look for env-var ``FMP_MCP_MANIFEST`` or use defaults.
        * **str | Path**        - path to a *.py* manifest that defines ``TOOLS``.
        * **Iterable[str]**     - already-constructed list/tuple/etc. of tool specs.

    Returns
    -------
    FastMCP
        Configured with the requested tools and a ready-made FMPDataClient.

    Notes
    -----
    * A *tool spec string* can be in two formats:
      - Full format: ``"<client>.<semantics_key>"`` (e.g., ``"company.profile"``)
      - Key-only format: ``"<semantics_key>"`` (e.g., ``"profile"``)
    * Key-only format will auto-discover the correct client module.
    * Full validation (non-existent mapping keys, non-callable methods, …) happens
      inside :func:`register_from_manifest`.
    """

    # ------------------------------------------------------------------ #
    # 1) Resolve the source of our tool spec list
    # ------------------------------------------------------------------ #
    if tools is None:
        manifest_path = os.getenv("FMP_MCP_MANIFEST")
        tool_specs = load_manifest_tools(manifest_path)
    elif isinstance(tools, str | Path):
        tool_specs = load_manifest_tools(tools)
    else:  # assume iterable of str
        tool_specs = list(tools)

    # ------------------------------------------------------------------ #
    # 2) Underlying FMP client (reads FMP_API_KEY from env)
    # ------------------------------------------------------------------ #
    fmp_client = FMPDataClient.from_env()

    # ------------------------------------------------------------------ #
    # 3) FastMCP skeleton (lazy import for runtime use)
    # ------------------------------------------------------------------ #
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as e:
        raise DependencyError(
            feature="MCP server", install_command="pip install fmp-data[mcp]"
        ) from e

    app = FastMCP("fmp-data")

    # ------------------------------------------------------------------ #
    # 4) Register our tools
    # ------------------------------------------------------------------ #
    register_from_manifest(app, fmp_client, tool_specs)

    return app
