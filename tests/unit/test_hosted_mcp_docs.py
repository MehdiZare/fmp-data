"""Guard: docs/mcp/hosted.md must name every FMP hosted MCP tool we probed.

The 2026-08-12 live ``tools/list`` returned 28 dataset tools. The matrix is
the only place we record that set; if a row is deleted the decision page
silently lies.
"""

from pathlib import Path

DOC_PATH = Path(__file__).resolve().parents[2] / "docs" / "mcp" / "hosted.md"

# Live tools/list, 2026-08-12. Refresh with the probe notes in hosted.md.
HOSTED_MCP_TOOLS = (
    "ESG",
    "Fundraisers",
    "analyst",
    "calendar",
    "chart",
    "commitmentOfTraders",
    "commodity",
    "company",
    "crypto",
    "directory",
    "discountedCashFlow",
    "earningsTranscript",
    "economics",
    "etfAndMutualFunds",
    "forex",
    "form13F",
    "indexes",
    "insiderTrades",
    "marketHours",
    "marketPerformance",
    "news",
    "quote",
    "search",
    "secFilings",
    "senate",
    "statements",
    "technicalIndicators",
    "tipranks",
)


def test_hosted_doc_lists_every_probed_tool() -> None:
    text = DOC_PATH.read_text()
    missing = [name for name in HOSTED_MCP_TOOLS if f"`{name}`" not in text]
    assert missing == [], f"docs/mcp/hosted.md missing hosted tools: {missing}"


def test_hosted_doc_records_twenty_eight_tools() -> None:
    text = DOC_PATH.read_text()
    assert "**28** dataset tools" in text
    assert len(HOSTED_MCP_TOOLS) == 28
    matrix_rows = [
        line
        for line in text.splitlines()
        if line.startswith("| `")
        and any(f"`{name}`" in line for name in HOSTED_MCP_TOOLS)
    ]
    assert len(matrix_rows) == 28, (
        f"hosted.md matrix rows {len(matrix_rows)} != probed tool count 28"
    )
