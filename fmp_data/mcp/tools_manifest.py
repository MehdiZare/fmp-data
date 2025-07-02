# fmp_data/mcp/tools_manifest.py
"""
Declarative list of MCP tools to expose.

Each item follows the pattern   "<client>.<semantics_key>"
• <client> is the sub-client directory (company, market, alternative, …)
• <semantics_key> is the key in <CLIENT>_ENDPOINTS_SEMANTICS
                  (e.g. "profile", "crypto_quote", …)
"""

DEFAULT_TOOLS: list[str] = [
    "company.profile",
    "company.market_cap",
    "alternative.crypto_quote",
    "company.historical_price",
    # add/remove freely…
]
