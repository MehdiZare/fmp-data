"""Guard test: docs/mcp/tools.md must list every MCP tool in the catalog.

The reference doc drifted repeatedly (whole client sections missing, stale
per-section counts). This keeps it honest without regenerating it by hand.
"""

from pathlib import Path
import re

from fmp_data.mcp.discovery import discover_all_tools
from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS

DOC_PATH = Path(__file__).resolve().parents[2] / "docs" / "mcp" / "tools.md"


def _documented_keys() -> set[str]:
    return set(re.findall(r"^\| `([a-z_0-9]+)` \|", DOC_PATH.read_text(), re.M))


def test_every_catalog_tool_is_documented() -> None:
    catalog = {tool["key"] for tool in discover_all_tools()}

    undocumented = sorted(catalog - _documented_keys())

    assert undocumented == [], f"Tools missing from {DOC_PATH.name}: {undocumented}"


def test_documented_totals_match_the_catalog() -> None:
    """The header states both totals; they must match what ships."""
    text = DOC_PATH.read_text()
    catalog_total = len(discover_all_tools())
    default_total = len(DEFAULT_TOOLS)

    assert f"`{catalog_total}` catalog tools" in text
    assert f"`{default_total}` default" in text
