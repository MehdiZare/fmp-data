"""Guard test: docs/mcp/tools.md must list every MCP tool in the catalog.

The reference doc drifted repeatedly (whole client sections missing, stale
per-section counts). This keeps it honest without regenerating it by hand.

Everything here compares on the fully-qualified ``client.key`` spec rather than
the bare tool key: ``crypto_quotes`` and ``forex_quotes`` each exist under two
clients, so a bare-key comparison silently tolerates deleting one of the two
rows.
"""

from collections import Counter
from pathlib import Path
import re

from fmp_data.mcp.discovery import discover_all_tools
from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS, WITHDRAWN_TOOLS

DOC_PATH = Path(__file__).resolve().parents[2] / "docs" / "mcp" / "tools.md"

_SECTION_RE = re.compile(r"^## (?P<title>.+)$")
_ROW_RE = re.compile(r"^\| `(?P<key>[a-z_0-9]+)` \|")
_COUNT_RE = re.compile(r"^\*\*(?P<catalog>\d+) tools?\*\*.*?\((?P<default>\d+) default")
_TOC_RE = re.compile(
    r"^- \[(?P<title>.+?) \((?P<catalog>\d+) tools?, (?P<default>\d+) default\)\]"
)


def _documented_specs() -> list[str]:
    """Every ``client.key`` row in the doc, in order, duplicates preserved."""
    specs: list[str] = []
    client: str | None = None

    for line in DOC_PATH.read_text().splitlines():
        section = _SECTION_RE.match(line)
        if section:
            title = section.group("title")
            client = None if title == "Table of Contents" else title.lower()
            continue

        row = _ROW_RE.match(line)
        if row and client is not None:
            specs.append(f"{client}.{row.group('key')}")

    return specs


def _documented_section_counts() -> dict[str, tuple[int, int]]:
    """``{client: (catalog_count, default_count)}`` from each section's count line."""
    counts: dict[str, tuple[int, int]] = {}
    client: str | None = None

    for line in DOC_PATH.read_text().splitlines():
        section = _SECTION_RE.match(line)
        if section:
            title = section.group("title")
            client = None if title == "Table of Contents" else title.lower()
            continue

        count = _COUNT_RE.match(line)
        if count and client is not None:
            counts[client] = (int(count.group("catalog")), int(count.group("default")))

    return counts


def _toc_counts() -> dict[str, tuple[int, int]]:
    """``{client: (catalog_count, default_count)}`` from the table of contents."""
    return {
        match.group("title").lower(): (
            int(match.group("catalog")),
            int(match.group("default")),
        )
        for match in (_TOC_RE.match(line) for line in DOC_PATH.read_text().splitlines())
        if match
    }


def _catalog_section_counts() -> dict[str, tuple[int, int]]:
    catalog = Counter(tool["client"] for tool in discover_all_tools())
    defaults = Counter(spec.split(".", 1)[0] for spec in DEFAULT_TOOLS)
    return {client: (total, defaults[client]) for client, total in catalog.items()}


def test_every_catalog_tool_is_documented() -> None:
    catalog = {tool["spec"] for tool in discover_all_tools()}

    undocumented = sorted(catalog - set(_documented_specs()))

    assert undocumented == [], f"Tools missing from {DOC_PATH.name}: {undocumented}"


def test_no_documented_tool_is_stale() -> None:
    """A row for a tool that no longer exists must fail, not linger."""
    catalog = {tool["spec"] for tool in discover_all_tools()}

    stale = sorted(set(_documented_specs()) - catalog)

    assert stale == [], f"{DOC_PATH.name} documents tools that do not exist: {stale}"


def test_default_tools_all_exist_in_the_catalog() -> None:
    """Every DEFAULT_TOOLS entry must name a real tool.

    The per-section counts below compare DEFAULT_TOOLS against the doc, so a
    manifest entry naming a tool that does not exist shows up only as an
    off-by-one the doc appears to be wrong about -- and "fixing" the doc count
    makes the suite green while the MCP server still fails to start on it.
    """
    catalog = {tool["spec"] for tool in discover_all_tools()}

    phantom = sorted(set(DEFAULT_TOOLS) - catalog)

    assert phantom == [], (
        f"DEFAULT_TOOLS names tools that do not exist in the catalog: {phantom}"
    )


def test_no_duplicate_rows() -> None:
    """The same tool must not be listed twice under one client."""
    duplicated = sorted(
        spec for spec, count in Counter(_documented_specs()).items() if count > 1
    )

    assert duplicated == [], f"Duplicate rows in {DOC_PATH.name}: {duplicated}"


def test_documented_totals_match_the_catalog() -> None:
    """The header states both totals; they must match what ships."""
    text = DOC_PATH.read_text()
    catalog_total = len(discover_all_tools())
    default_total = len(DEFAULT_TOOLS)

    assert f"`{catalog_total}` catalog tools" in text
    assert f"`{default_total}` default" in text


_NO_SUCCESSOR_WORDS = {
    6: "Six",
    7: "Seven",
    8: "Eight",
    9: "Nine",
    10: "Ten",
}


def test_withdrawn_preamble_counts_match_source() -> None:
    """The withdrawn-endpoint prose must track WITHDRAWN_TOOLS, not rot."""
    text = DOC_PATH.read_text()
    withdrawn = len(WITHDRAWN_TOOLS)
    no_successor = sum(value is None for value in WITHDRAWN_TOOLS.values())
    word = _NO_SUCCESSOR_WORDS.get(no_successor)

    assert f"{withdrawn} tools name an FMP endpoint that no longer exists" in text
    assert word is not None, (
        f"add a word mapping for {no_successor} withdrawn tools with no successor"
    )
    assert f"{word} have no successor at all" in text


def test_per_section_counts_match_the_catalog() -> None:
    """Each section's own count line must match the catalog, not just the totals."""
    expected = _catalog_section_counts()

    assert _documented_section_counts() == expected


def test_toc_counts_match_the_catalog() -> None:
    """The table of contents restates every count and must agree too."""
    expected = _catalog_section_counts()

    assert _toc_counts() == expected
