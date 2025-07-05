# fmp_data/mcp/server.py
from __future__ import annotations

from collections.abc import Iterable, Sequence
import importlib.util
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from fmp_data.client import FMPDataClient
from fmp_data.mcp.tool_loader import register_from_manifest
from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS


def _load_py_manifest(path: str | Path) -> list[str]:
    """
    Dynamically import a Python file that defines ``TOOLS`` *and* return it.

    Raises
    ------
    RuntimeError
        If the module cannot be imported.
    AttributeError
        If the imported module does not expose ``TOOLS``.
    """
    path = Path(path).expanduser().resolve()
    spec = importlib.util.spec_from_file_location("user_manifest", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import manifest at {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "TOOLS"):
        raise AttributeError(f"{path} does not define a global variable 'TOOLS'")

    return list(module.TOOLS)  # copy to detach from the module


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
    * A *tool spec string* always has the form ``"<client>.<semantics_key>"`` —
      e.g. ``"company.profile"`` or ``"alternative.crypto_quote"``.
    * Full validation (non-existent mapping keys, non-callable methods, …) happens
      inside :func:`register_from_manifest`.
    """

    # ------------------------------------------------------------------ #
    # 1) Resolve the source of our tool spec list
    # ------------------------------------------------------------------ #
    if tools is None:
        manifest_path = os.getenv("FMP_MCP_MANIFEST")
        tool_specs: list[str] = (
            _load_py_manifest(manifest_path) if manifest_path else DEFAULT_TOOLS
        )
    elif isinstance(tools, str | Path):
        tool_specs = _load_py_manifest(tools)
    else:  # assume iterable of str
        tool_specs = list(tools)

    # ------------------------------------------------------------------ #
    # 2) Underlying FMP client (reads FMP_API_KEY from env)
    # ------------------------------------------------------------------ #
    fmp_client = FMPDataClient.from_env()

    # ------------------------------------------------------------------ #
    # 3) FastMCP skeleton
    # ------------------------------------------------------------------ #
    app = FastMCP(
        "fmp-data",
        description="Financial Modeling Prep data exposed as MCP tools",
        version="0.3.0",
    )

    # ------------------------------------------------------------------ #
    # 4) Register our tools
    # ------------------------------------------------------------------ #
    register_from_manifest(app, fmp_client, tool_specs)

    return app
