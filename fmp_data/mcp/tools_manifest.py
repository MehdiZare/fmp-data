# fmp_data/mcp/tools_manifest.py
"""
Declarative list of MCP tools to expose.

Each tool is referenced by its semantic key as discovered by the MCP discovery system.
Tools are organized by client module for clarity.

To customize the available tools, modify the DEFAULT_TOOLS list or set the
FMP_MCP_MANIFEST environment variable to point to a custom manifest file.
"""

#: Tool keys that still resolve but are on their way out.
#:
#: Maps a deprecated ``<client>.<key>`` spec to the canonical spec that replaces
#: it. The invariant being restored is **one tool key per ``(client, method)``
#: pair** (#136): each key below names the same callable as its replacement, so
#: an MCP client saw two tools that did exactly the same thing.
#:
#: Deprecated keys keep resolving through 2.6 behind a ``DeprecationWarning``
#: (see ``fmp_data.mcp.tool_loader._warn_if_deprecated``) and are removed in
#: 3.0. They are excluded from :data:`DEFAULT_TOOLS` now, so a default server
#: already advertises exactly one tool per method.
DEPRECATED_TOOLS: dict[str, str] = {
    "company.executives": "company.key_executives",
    "company.historical_price": "company.historical_prices",
    "company.intraday_price": "company.intraday_prices",
}

DEFAULT_TOOLS: list[str] = [
    # Alternative (15 tools) - Crypto, Forex, and Commodities
    "alternative.commodities_list",
    "alternative.commodities_quotes",
    "alternative.commodity_historical",
    "alternative.commodity_intraday",
    "alternative.commodity_quote",
    "alternative.crypto_historical",
    "alternative.crypto_intraday",
    "alternative.crypto_list",
    "alternative.crypto_quote",
    "alternative.crypto_quotes",
    "alternative.forex_historical",
    "alternative.forex_intraday",
    "alternative.forex_list",
    "alternative.forex_quote",
    "alternative.forex_quotes",
    # Company (31 tools) - Company Information and Quotes
    "company.analyst_estimates",
    "company.analyst_recommendations",
    "company.company_notes",
    "company.core_information",
    "company.employee_count",
    "company.executive_compensation",
    "company.aftermarket_quote",
    "company.aftermarket_trade",
    "company.geographic_revenue_segmentation",
    "company.historical_market_cap",
    "company.historical_prices",
    "company.historical_share_float",
    "company.intraday_prices",
    "company.key_executives",
    "company.market_cap",
    "company.price_target",
    "company.price_target_consensus",
    "company.price_target_summary",
    "company.product_revenue_segmentation",
    "company.profile",
    "company.quote",
    "company.share_float",
    "company.simple_quote",
    "company.stock_price_change",
    "company.symbol_changes",
    "company.upgrades_downgrades",
    "company.upgrades_downgrades_consensus",
    # Economics (4 tools) - Economic Indicators
    "economics.economic_calendar",
    "economics.economic_indicators",
    "economics.market_risk_premium",
    "economics.commitment_of_traders_report",
    "economics.commitment_of_traders_analysis",
    "economics.commitment_of_traders_list",
    "economics.treasury_rates",
    # Fundamental (14 tools) - Financial Statements and Valuation
    "fundamental.balance_sheet",
    "fundamental.cash_flow",
    "fundamental.custom_discounted_cash_flow",
    "fundamental.custom_levered_dcf",
    "fundamental.discounted_cash_flow",
    "fundamental.financial_ratios",
    "fundamental.full_financial_statement",
    "fundamental.historical_rating",
    "fundamental.income_statement",
    "fundamental.key_metrics",
    "fundamental.levered_dcf",
    "fundamental.latest_financial_statements",
    "fundamental.owner_earnings",
    # Institutional (13 tools) - Institutional and Insider Data
    "institutional.asset_allocation",
    "institutional.beneficial_ownership",
    "institutional.fail_to_deliver",
    "institutional.form_13f",
    "institutional.form_13f_dates",
    "institutional.insider_roster",
    "institutional.insider_statistics",
    "institutional.insider_trades",
    "institutional.institutional_holdings",
    "institutional.transaction_types",
    # Intelligence (39 tools) - news, events, grades/ratings (#116)
    # Dead/deprecated FMP endpoints intentionally omitted from defaults:
    # earnings_confirmed, earnings_surprises, stock_news_sentiments,
    # historical_social_sentiment, trending_social_sentiment,
    # social_sentiment_changes (still importable on the client).
    "intelligence.crowdfunding_by_cik",
    "intelligence.crowdfunding_rss",
    "intelligence.crowdfunding_search",
    "intelligence.crypto_news",
    "intelligence.crypto_symbol_news",
    "intelligence.dividends_calendar",
    "intelligence.earnings_calendar",
    "intelligence.equity_offering_by_cik",
    "intelligence.equity_offering_rss",
    "intelligence.equity_offering_search",
    "intelligence.esg_benchmark",
    "intelligence.esg_data",
    "intelligence.esg_ratings",
    "intelligence.fmp_articles",
    "intelligence.forex_news",
    "intelligence.forex_symbol_news",
    "intelligence.general_news",
    "intelligence.grades",
    "intelligence.grades_consensus",
    "intelligence.grades_historical",
    "intelligence.grades_latest_news",
    "intelligence.grades_news",
    "intelligence.historical_earnings",
    "intelligence.house_disclosure",
    "intelligence.house_latest",
    "intelligence.house_trades_by_name",
    "intelligence.ipo_calendar",
    "intelligence.press_releases",
    "intelligence.press_releases_by_symbol",
    "intelligence.price_target_latest_news",
    "intelligence.price_target_news",
    "intelligence.ratings_historical",
    "intelligence.ratings_snapshot",
    "intelligence.senate_trading",
    "intelligence.senate_trading_rss",
    "intelligence.senate_latest",
    "intelligence.senate_trades_by_name",
    "intelligence.stock_news",
    "intelligence.stock_splits_calendar",
    # Investment (11 tools) - ETFs and Mutual Funds
    "investment.etf_country_weightings",
    "investment.etf_exposure",
    "investment.etf_holder",
    "investment.etf_holding_dates",
    "investment.etf_holdings",
    "investment.etf_info",
    "investment.etf_sector_weightings",
    "investment.fund_disclosure",
    "investment.fund_disclosure_holders_latest",
    "investment.fund_disclosure_holders_search",
    "investment.mutual_fund_by_name",
    "investment.mutual_fund_dates",
    "investment.mutual_fund_holder",
    "investment.mutual_fund_holdings",
    # Market (14 tools) - Market Data and Search
    "market.all_shares_float",
    "market.all_exchange_market_hours",
    "market.available_indexes",
    "market.etf_list",
    "market.gainers",
    "market.historical_industry_pe",
    "market.historical_industry_performance",
    "market.historical_sector_pe",
    "market.historical_sector_performance",
    "market.industry_pe_snapshot",
    "market.industry_performance_snapshot",
    "market.holidays_by_exchange",
    "market.losers",
    "market.market_hours",
    "market.most_active",
    "market.pre_post_market",
    "market.search_by_cik",
    "market.search_by_cusip",
    "market.search_by_isin",
    "market.sector_pe_snapshot",
    "market.sector_performance",
    "market.stock_list",
    # Technical (9 tools) - Technical Indicators
    "technical.adx",
    "technical.dema",
    "technical.ema",
    "technical.rsi",
    "technical.sma",
    "technical.standard_deviation",
    "technical.tema",
    "technical.williams",
    "technical.wma",
]

# Minimal set for quick testing
MINIMAL_TOOLS: list[str] = [
    "company.profile",
    "company.quote",
    "alternative.crypto_quote",
]

# Extended set for comprehensive coverage
EXTENDED_TOOLS: list[str] = [
    *DEFAULT_TOOLS,
    # Additional company data
    "company.price_target_summary",
    "company.share_float",
    "company.company_notes",
    # More market data
    "market.available_indexes",
    "market.search",
    # Institutional data
    "institutional.institutional_holders",
    "institutional.insider_trades",
    # Investment products
    "investment.etf_info",
    "investment.etf_holdings",
    # More technical indicators
    "technical.ema",
    "technical.williams",
    "technical.adx",
]
