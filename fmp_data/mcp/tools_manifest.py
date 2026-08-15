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
#:
#: **Not the same mechanism as** ``EndpointSemantics.deprecated`` (#137), and
#: they must not be merged. This table is about duplicate *names* for a method
#: that still works: resolve one and you get live data, plus a warning telling
#: you to rename. That flag is about an endpoint that no longer returns
#: anything, whatever name you reach it by -- the fix there is to stop
#: advertising it to an LLM, not to rename it. The two stay **disjoint**: no
#: spec is both an alias for a live method and a dead endpoint, and a guard
#: asserts it.
#:
#: :data:`WITHDRAWN_TOOLS` is the table that *does* correspond to that flag,
#: one-for-one. Note the three-way split, because it is easy to collapse: an
#: alias for a live method belongs here; a dead endpoint belongs there and
#: carries the flag; nothing belongs in both.
DEPRECATED_TOOLS: dict[str, str] = {
    "company.executives": "company.key_executives",
    "company.historical_price": "company.historical_prices",
    "company.intraday_price": "company.intraday_prices",
}

#: Tool keys whose FMP endpoint is gone, mapped to the nearest live tool.
#:
#: Deliberately **not** merged into :data:`DEPRECATED_TOOLS`, which means
#: something narrower: two keys for one callable, where the replacement is a
#: drop-in and the warning says so. Every key here names a path that 404s, and
#: the value -- when there is one -- is a *different* endpoint with a
#: different payload. Collapsing the two would make ``DEPRECATED_TOOLS``'s
#: "both names call the same client method" guarantee false, and would tell
#: users a migration is mechanical when it is not.
#:
#: ``None`` means FMP withdrew the data with no successor at all.
#:
#: All of these were probed against the live ``stable`` API. They still
#: resolve, so an explicit manifest keeps working, but they are excluded from
#: :data:`DEFAULT_TOOLS`: a default server should not advertise a tool that
#: can only ever return empty.
#:
#: **This table must list every endpoint carrying**
#: ``EndpointSemantics.deprecated=True`` **(#164).** The flag is what hides a
#: dead endpoint from the LangChain vector store; this table is what hides it
#: from MCP. They describe the same fact -- "FMP does not serve this any more"
#: -- so a spec in one and not the other means one surface still advertises a
#: tool that can only answer empty. It did: three ``intelligence`` entries were
#: flagged but untabled, and ``fmp-mcp generate`` shipped all three.
#: ``test_withdrawn_tools_match_the_semantics_flag`` asserts the two agree
#: exactly, so the next withdrawal cannot fix one surface and forget the other.
WITHDRAWN_TOOLS: dict[str, str | None] = {
    "alternative.crypto_quotes": "batch.crypto_quotes",
    "alternative.forex_quotes": "batch.forex_quotes",
    "alternative.commodities_quotes": "batch.commodity_quotes",
    "company.core_information": "company.profile",
    "company.price_target": "company.price_target_summary",
    "company.analyst_recommendations": "intelligence.grades_consensus",
    "company.upgrades_downgrades": "intelligence.grades",
    "company.upgrades_downgrades_consensus": "intelligence.grades_consensus",
    "company.historical_share_float": "company.share_float",
    "fundamental.historical_rating": "intelligence.ratings_historical",
    # Probed live: earning-calendar-confirmed, earnings-surprises and
    # stock-news-sentiments-rss-feed all 404. They carried
    # `EndpointSemantics.deprecated=True` from #137 -- which hid them from the
    # LangChain vector store -- but were absent here, so `fmp-mcp generate`
    # kept shipping three tools that answer empty on every call (#164). FMP
    # publishes nothing equivalent for any of them.
    "intelligence.earnings_confirmed": None,
    "intelligence.earnings_surprises": None,
    "intelligence.senate_trading_rss": "intelligence.senate_latest",
    "intelligence.stock_news_sentiments": None,
    "investment.etf_holding_dates": "investment.mutual_fund_dates",
    "investment.mutual_fund_holdings": "investment.etf_holdings",
    "investment.etf_holder": "investment.fund_disclosure_holders_latest",
    "investment.mutual_fund_holder": "investment.fund_disclosure_holders_latest",
    "investment.mutual_fund_by_name": None,
    "market.pre_post_market": None,
    "institutional.asset_allocation": None,
    "institutional.fail_to_deliver": None,
}

DEFAULT_TOOLS: list[str] = [
    # Alternative (12 tools) - Crypto, Forex, and Commodities
    # Dead FMP endpoints intentionally omitted (see WITHDRAWN_TOOLS):
    # crypto_quotes, forex_quotes, commodities_quotes -- the live
    # batch-*-quotes paths are served by the batch client instead.
    "alternative.commodities_list",
    "alternative.commodity_historical",
    "alternative.commodity_intraday",
    "alternative.commodity_quote",
    "alternative.crypto_historical",
    "alternative.crypto_intraday",
    "alternative.crypto_list",
    "alternative.crypto_quote",
    "alternative.forex_historical",
    "alternative.forex_intraday",
    "alternative.forex_list",
    "alternative.forex_quote",
    # Company (22 tools) - Company Information and Quotes
    # Dead FMP endpoints intentionally omitted (see WITHDRAWN_TOOLS):
    # analyst_recommendations, core_information, price_target,
    # upgrades_downgrades, upgrades_downgrades_consensus,
    # historical_share_float -- replaced by grades_consensus, profile,
    # price_target_summary, grades and share_float respectively.
    "company.analyst_estimates",
    "company.company_notes",
    "company.delisted_companies",
    "company.employee_count",
    "company.executive_compensation",
    "company.aftermarket_quote",
    "company.aftermarket_trade",
    "company.geographic_revenue_segmentation",
    "company.historical_market_cap",
    "company.historical_prices",
    "company.intraday_prices",
    "company.key_executives",
    "company.market_cap",
    "company.price_target_consensus",
    "company.price_target_summary",
    "company.product_revenue_segmentation",
    "company.profile",
    "company.quote",
    "company.share_float",
    "company.simple_quote",
    "company.stock_price_change",
    "company.symbol_changes",
    # Economics (7 tools) - Economic Indicators
    "economics.economic_calendar",
    "economics.economic_indicators",
    "economics.market_risk_premium",
    "economics.commitment_of_traders_report",
    "economics.commitment_of_traders_analysis",
    "economics.commitment_of_traders_list",
    "economics.treasury_rates",
    # Fundamental (12 tools) - Financial Statements and Valuation
    "fundamental.balance_sheet",
    "fundamental.cash_flow",
    "fundamental.custom_discounted_cash_flow",
    "fundamental.custom_levered_dcf",
    "fundamental.discounted_cash_flow",
    "fundamental.financial_ratios",
    "fundamental.full_financial_statement",
    "fundamental.income_statement",
    "fundamental.key_metrics",
    "fundamental.levered_dcf",
    "fundamental.latest_financial_statements",
    "fundamental.owner_earnings",
    # Institutional (8 tools) - Institutional and Insider Data
    "institutional.beneficial_ownership",
    "institutional.form_13f",
    "institutional.form_13f_dates",
    "institutional.insider_roster",
    "institutional.insider_statistics",
    "institutional.insider_trades",
    "institutional.institutional_holdings",
    "institutional.transaction_types",
    # Intelligence (40 tools) - news, events, grades/ratings (#116)
    # Dead FMP endpoints intentionally omitted from defaults, all in
    # WITHDRAWN_TOOLS: earnings_confirmed, earnings_surprises and
    # stock_news_sentiments 404 with no successor at all, and
    # senate_trading_rss is superseded by senate_latest.
    # historical_social_sentiment, trending_social_sentiment and
    # social_sentiment_changes are still importable on the client but have no
    # semantics entry, so they are not MCP tools and cannot be listed here.
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
    "intelligence.house_trades_by_id",
    "intelligence.house_trades_by_name",
    "intelligence.ipo_calendar",
    "intelligence.press_releases",
    "intelligence.press_releases_by_symbol",
    "intelligence.price_target_latest_news",
    "intelligence.price_target_news",
    "intelligence.ratings_historical",
    "intelligence.ratings_snapshot",
    "intelligence.senate_trading",
    "intelligence.senate_latest",
    "intelligence.senate_trades_by_id",
    "intelligence.senate_trades_by_name",
    "intelligence.stock_news",
    "intelligence.stock_splits_calendar",
    # Investment (9 tools) - ETFs and Mutual Funds
    # Dead FMP endpoints intentionally omitted (see WITHDRAWN_TOOLS):
    # etf_holding_dates and mutual_fund_holdings are replaced by
    # mutual_fund_dates and etf_holdings; etf_holder, mutual_fund_holder and
    # mutual_fund_by_name have no replacement.
    "investment.etf_country_weightings",
    "investment.etf_exposure",
    "investment.etf_holdings",
    "investment.etf_info",
    "investment.etf_sector_weightings",
    "investment.fund_disclosure",
    "investment.fund_disclosure_holders_latest",
    "investment.fund_disclosure_holders_search",
    "investment.mutual_fund_dates",
    # Market (21 tools) - Market Data and Search
    # pre_post_market omitted: the path 404s and the market-wide shape no
    # longer exists at FMP (see WITHDRAWN_TOOLS).
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
