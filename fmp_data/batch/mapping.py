# fmp_data/batch/mapping.py
from __future__ import annotations

from fmp_data.batch.endpoints import (
    BALANCE_SHEET_STATEMENT_BULK,
    BALANCE_SHEET_STATEMENT_GROWTH_BULK,
    BATCH_AFTERMARKET_QUOTE,
    BATCH_AFTERMARKET_TRADE,
    BATCH_COMMODITY_QUOTES,
    BATCH_CRYPTO_QUOTES,
    BATCH_ETF_QUOTES,
    BATCH_EXCHANGE_QUOTE,
    BATCH_FOREX_QUOTES,
    BATCH_INDEX_QUOTES,
    BATCH_MARKET_CAP,
    BATCH_MUTUALFUND_QUOTES,
    BATCH_QUOTE,
    BATCH_QUOTE_SHORT,
    CASH_FLOW_STATEMENT_BULK,
    CASH_FLOW_STATEMENT_GROWTH_BULK,
    DCF_BULK,
    EARNINGS_SURPRISES_BULK,
    EOD_BULK,
    ETF_HOLDER_BULK,
    INCOME_STATEMENT_BULK,
    INCOME_STATEMENT_GROWTH_BULK,
    KEY_METRICS_TTM_BULK,
    PEERS_BULK,
    PRICE_TARGET_SUMMARY_BULK,
    PROFILE_BULK,
    RATING_BULK,
    RATIOS_TTM_BULK,
    SCORES_BULK,
    UPGRADES_DOWNGRADES_CONSENSUS_BULK,
)
from fmp_data.lc.models import EndpointSemantics, SemanticCategory

# Batch endpoints mapping
BATCH_ENDPOINT_MAP = {
    "get_quotes": BATCH_QUOTE,
    "get_quotes_short": BATCH_QUOTE_SHORT,
    "get_aftermarket_trades": BATCH_AFTERMARKET_TRADE,
    "get_aftermarket_quotes": BATCH_AFTERMARKET_QUOTE,
    "get_exchange_quotes": BATCH_EXCHANGE_QUOTE,
    "get_mutualfund_quotes": BATCH_MUTUALFUND_QUOTES,
    "get_etf_quotes": BATCH_ETF_QUOTES,
    "get_commodity_quotes": BATCH_COMMODITY_QUOTES,
    "get_crypto_quotes": BATCH_CRYPTO_QUOTES,
    "get_forex_quotes": BATCH_FOREX_QUOTES,
    "get_index_quotes": BATCH_INDEX_QUOTES,
    "get_market_caps": BATCH_MARKET_CAP,
    "get_profile_bulk": PROFILE_BULK,
    "get_dcf_bulk": DCF_BULK,
    "get_rating_bulk": RATING_BULK,
    "get_scores_bulk": SCORES_BULK,
    "get_ratios_ttm_bulk": RATIOS_TTM_BULK,
    "get_price_target_summary_bulk": PRICE_TARGET_SUMMARY_BULK,
    "get_etf_holder_bulk": ETF_HOLDER_BULK,
    "get_upgrades_downgrades_consensus_bulk": UPGRADES_DOWNGRADES_CONSENSUS_BULK,
    "get_key_metrics_ttm_bulk": KEY_METRICS_TTM_BULK,
    "get_peers_bulk": PEERS_BULK,
    "get_earnings_surprises_bulk": EARNINGS_SURPRISES_BULK,
    "get_income_statement_bulk": INCOME_STATEMENT_BULK,
    "get_income_statement_growth_bulk": INCOME_STATEMENT_GROWTH_BULK,
    "get_balance_sheet_bulk": BALANCE_SHEET_STATEMENT_BULK,
    "get_balance_sheet_growth_bulk": BALANCE_SHEET_STATEMENT_GROWTH_BULK,
    "get_cash_flow_bulk": CASH_FLOW_STATEMENT_BULK,
    "get_cash_flow_growth_bulk": CASH_FLOW_STATEMENT_GROWTH_BULK,
    "get_eod_bulk": EOD_BULK,
}

# Complete semantic definitions for all endpoints
BATCH_ENDPOINTS_SEMANTICS = {
    "batch_quote": EndpointSemantics(
        client_name="batch",
        method_name="get_quotes",
        natural_description=(
            "Get real-time quotes for multiple symbols in a single request. "
            "Get current price, volume, and market data for many stocks."
        ),
        example_queries=[
            "Get quotes for AAPL, MSFT, GOOGL",
            "Batch quotes for multiple stocks",
            "Real-time quotes for symbol list",
            "Get prices for several companies",
            "Multi-symbol quote data",
        ],
        related_terms=[
            "batch quotes",
            "multiple quotes",
            "bulk quotes",
            "multi-symbol",
            "price list",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=[
            "Portfolio monitoring",
            "Multi-symbol analysis",
            "Market screening",
            "Watchlist tracking",
        ],
    ),
    "batch_quote_short": EndpointSemantics(
        client_name="batch",
        method_name="get_quotes_short",
        natural_description=(
            "Get quick price snapshots for multiple symbols. "
            "Fast, lightweight quotes with essential price information."
        ),
        example_queries=[
            "Get quick prices for multiple stocks",
            "Fast batch quotes",
            "Short quote data for symbols",
            "Lightweight multi-symbol quotes",
        ],
        related_terms=[
            "quick quotes",
            "short quotes",
            "fast quotes",
            "price snapshots",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "aftermarket_trades": EndpointSemantics(
        client_name="batch",
        method_name="get_aftermarket_trades",
        natural_description=(
            "Get aftermarket (post-market) trade data for multiple symbols. "
            "Returns trading activity that occurred after regular market hours."
        ),
        example_queries=[
            "Get aftermarket trades",
            "Post-market trading data",
            "After-hours trade activity",
            "Extended hours trades",
        ],
        related_terms=[
            "aftermarket",
            "after-hours",
            "post-market",
            "extended hours",
            "pre-market",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "aftermarket_quotes": EndpointSemantics(
        client_name="batch",
        method_name="get_aftermarket_quotes",
        natural_description=(
            "Get aftermarket quote data for multiple symbols. "
            "Returns current prices and quotes from after-hours trading sessions."
        ),
        example_queries=[
            "Get aftermarket quotes",
            "Post-market quote data",
            "After-hours prices",
            "Extended hours quotes",
        ],
        related_terms=[
            "aftermarket",
            "after-hours quotes",
            "post-market quotes",
            "extended hours",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "exchange_quotes": EndpointSemantics(
        client_name="batch",
        method_name="get_exchange_quotes",
        natural_description=(
            "Get quotes for all stocks on a specific exchange. "
            "Returns market data for entire exchange (NYSE, NASDAQ, etc.)."
        ),
        example_queries=[
            "Get all NYSE quotes",
            "Quotes for entire NASDAQ exchange",
            "All stocks on an exchange",
            "Exchange-wide market data",
        ],
        related_terms=[
            "exchange quotes",
            "market-wide data",
            "exchange data",
            "NYSE",
            "NASDAQ",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "mutualfund_quotes": EndpointSemantics(
        client_name="batch",
        method_name="get_mutualfund_quotes",
        natural_description=(
            "Get batch quotes for all mutual funds. "
            "Returns comprehensive quote data for entire mutual fund universe."
        ),
        example_queries=[
            "Get all mutual fund quotes",
            "Batch mutual fund prices",
            "All mutual fund data",
            "Universe of mutual funds",
        ],
        related_terms=[
            "mutual funds",
            "fund quotes",
            "fund universe",
            "NAV",
            "fund prices",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "etf_quotes": EndpointSemantics(
        client_name="batch",
        method_name="get_etf_quotes",
        natural_description=(
            "Get batch quotes for all ETFs. "
            "Returns comprehensive quote data for entire ETF universe."
        ),
        example_queries=[
            "Get all ETF quotes",
            "Batch ETF prices",
            "All ETF data",
            "Universe of ETFs",
            "Exchange-traded fund quotes",
        ],
        related_terms=[
            "ETFs",
            "exchange-traded funds",
            "ETF universe",
            "fund quotes",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "commodity_quotes": EndpointSemantics(
        client_name="batch",
        method_name="get_commodity_quotes",
        natural_description=(
            "Get batch quotes for all commodities. "
            "Returns prices for gold, silver, oil, and other commodity futures."
        ),
        example_queries=[
            "Get all commodity quotes",
            "Batch commodity prices",
            "All commodity data",
            "Gold silver oil prices",
        ],
        related_terms=[
            "commodities",
            "commodity prices",
            "futures",
            "gold",
            "oil",
            "metals",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "crypto_quotes": EndpointSemantics(
        client_name="batch",
        method_name="get_crypto_quotes",
        natural_description=(
            "Get batch quotes for all cryptocurrencies. "
            "Returns crypto market data including Bitcoin, Ethereum, etc."
        ),
        example_queries=[
            "Get all crypto quotes",
            "Batch cryptocurrency prices",
            "All crypto market data",
            "Bitcoin Ethereum prices",
        ],
        related_terms=[
            "cryptocurrency",
            "crypto",
            "Bitcoin",
            "Ethereum",
            "digital assets",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "forex_quotes": EndpointSemantics(
        client_name="batch",
        method_name="get_forex_quotes",
        natural_description=(
            "Get batch quotes for all forex pairs. "
            "Returns comprehensive foreign exchange rate data for all currency pairs."
        ),
        example_queries=[
            "Get all forex quotes",
            "Batch currency exchange rates",
            "All forex pairs",
            "Foreign exchange rates",
        ],
        related_terms=[
            "forex",
            "foreign exchange",
            "currency pairs",
            "FX rates",
            "exchange rates",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "index_quotes": EndpointSemantics(
        client_name="batch",
        method_name="get_index_quotes",
        natural_description=(
            "Get batch quotes for all market indexes. "
            "Returns data for S&P 500, Dow Jones, NASDAQ, and other indexes."
        ),
        example_queries=[
            "Get all index quotes",
            "Batch market index prices",
            "All market indexes",
            "S&P 500 Dow NASDAQ data",
        ],
        related_terms=[
            "market indexes",
            "index quotes",
            "S&P 500",
            "Dow Jones",
            "NASDAQ",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "market_caps": EndpointSemantics(
        client_name="batch",
        method_name="get_market_caps",
        natural_description=(
            "Get market capitalization for multiple symbols. "
            "Returns current market cap values for specified companies."
        ),
        example_queries=[
            "Get market caps for multiple stocks",
            "Batch market capitalization",
            "Multi-symbol market cap data",
            "Company valuation batch",
        ],
        related_terms=[
            "market cap",
            "market capitalization",
            "company valuation",
            "market value",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "profile_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_profile_bulk",
        natural_description=(
            "Get company profile data in bulk (CSV format). "
            "Returns comprehensive company information for many companies at once."
        ),
        example_queries=[
            "Get bulk company profiles",
            "Batch company information",
            "All company profiles",
            "Bulk corporate data",
        ],
        related_terms=[
            "bulk profiles",
            "company data",
            "corporate information",
            "batch profiles",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "dcf_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_dcf_bulk",
        natural_description=(
            "Get discounted cash flow valuations in bulk. "
            "Returns DCF analysis and intrinsic value calculations for many companies."
        ),
        example_queries=[
            "Get bulk DCF valuations",
            "Batch discounted cash flow",
            "All company valuations",
            "Intrinsic value bulk data",
        ],
        related_terms=[
            "DCF",
            "discounted cash flow",
            "valuation",
            "intrinsic value",
            "fair value",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "rating_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_rating_bulk",
        natural_description=(
            "Get stock ratings in bulk. "
            "Returns comprehensive rating data and recommendations for many stocks."
        ),
        example_queries=[
            "Get bulk stock ratings",
            "Batch company ratings",
            "All stock recommendations",
            "Rating data in bulk",
        ],
        related_terms=[
            "ratings",
            "recommendations",
            "analyst ratings",
            "stock scores",
        ],
        category=SemanticCategory.INTELLIGENCE,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "scores_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_scores_bulk",
        natural_description=(
            "Get financial scores in bulk. "
            "Returns Piotroski F-Score and Altman Z-Score for many companies."
        ),
        example_queries=[
            "Get bulk financial scores",
            "Batch company scores",
            "Piotroski scores bulk",
            "Altman Z-scores bulk",
        ],
        related_terms=[
            "financial scores",
            "Piotroski score",
            "Altman Z-score",
            "company health",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "ratios_ttm_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_ratios_ttm_bulk",
        natural_description=(
            "Get trailing twelve month financial ratios in bulk. "
            "Returns comprehensive financial ratio analysis for many companies."
        ),
        example_queries=[
            "Get bulk TTM ratios",
            "Batch financial ratios",
            "Trailing twelve month ratios",
            "Financial metrics bulk",
        ],
        related_terms=[
            "TTM",
            "trailing twelve months",
            "financial ratios",
            "metrics",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "price_target_summary_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_price_target_summary_bulk",
        natural_description=(
            "Get bulk price target summaries. "
            "Returns analyst price target data and consensus for many stocks."
        ),
        example_queries=[
            "Get bulk price targets",
            "Batch analyst price targets",
            "Price target summaries",
            "Analyst targets bulk",
        ],
        related_terms=[
            "price targets",
            "analyst targets",
            "target prices",
            "price consensus",
        ],
        category=SemanticCategory.INTELLIGENCE,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "etf_holder_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_etf_holder_bulk",
        natural_description=(
            "Get bulk ETF holdings. "
            "Returns comprehensive ETF holding data for many funds."
        ),
        example_queries=[
            "Get bulk ETF holdings",
            "Batch ETF portfolio data",
            "All ETF positions",
            "ETF holdings bulk",
        ],
        related_terms=[
            "ETF holdings",
            "fund positions",
            "portfolio holdings",
            "ETF portfolios",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "upgrades_downgrades_consensus_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_upgrades_downgrades_consensus_bulk",
        natural_description=(
            "Get bulk upgrades/downgrades consensus data. "
            "Returns analyst rating changes and consensus for many stocks."
        ),
        example_queries=[
            "Get bulk analyst upgrades downgrades",
            "Batch rating changes",
            "Analyst consensus bulk",
            "Rating change data",
        ],
        related_terms=[
            "upgrades",
            "downgrades",
            "rating changes",
            "analyst consensus",
        ],
        category=SemanticCategory.INTELLIGENCE,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "key_metrics_ttm_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_key_metrics_ttm_bulk",
        natural_description=(
            "Get bulk trailing twelve month key metrics. "
            "Returns comprehensive financial metrics and KPIs for many companies."
        ),
        example_queries=[
            "Get bulk key metrics",
            "Batch TTM metrics",
            "Financial KPIs bulk",
            "Key metrics bulk data",
        ],
        related_terms=[
            "key metrics",
            "KPIs",
            "financial metrics",
            "TTM metrics",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "peers_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_peers_bulk",
        natural_description=(
            "Get bulk peer lists. "
            "Returns peer company data and competitor lists for many companies."
        ),
        example_queries=[
            "Get bulk peer lists",
            "Batch competitor data",
            "Company peers bulk",
            "Peer analysis bulk",
        ],
        related_terms=[
            "peers",
            "competitors",
            "peer companies",
            "competitor analysis",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "earnings_surprises_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_earnings_surprises_bulk",
        natural_description=(
            "Get bulk earnings surprises for a given year. "
            "Returns actual vs expected earnings data for many companies."
        ),
        example_queries=[
            "Get bulk earnings surprises",
            "Batch earnings miss/beat data",
            "Annual earnings surprises",
            "Earnings vs estimates bulk",
        ],
        related_terms=[
            "earnings surprise",
            "earnings beat",
            "earnings miss",
            "vs estimates",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "income_statement_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_income_statement_bulk",
        natural_description=(
            "Get bulk income statements. "
            "Returns comprehensive income statement data for many companies."
        ),
        example_queries=[
            "Get bulk income statements",
            "Batch P&L data",
            "Revenue data bulk",
            "Income statements bulk",
        ],
        related_terms=[
            "income statement",
            "P&L",
            "profit and loss",
            "revenue",
            "earnings",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "income_statement_growth_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_income_statement_growth_bulk",
        natural_description=(
            "Get bulk income statement growth data. "
            "Returns year-over-year growth metrics for income statement items."
        ),
        example_queries=[
            "Get bulk income growth data",
            "Batch revenue growth",
            "Income statement growth bulk",
            "YoY growth metrics",
        ],
        related_terms=[
            "income growth",
            "revenue growth",
            "YoY growth",
            "growth rates",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "balance_sheet_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_balance_sheet_bulk",
        natural_description=(
            "Get bulk balance sheet statements. "
            "Returns comprehensive balance sheet data for many companies."
        ),
        example_queries=[
            "Get bulk balance sheets",
            "Batch balance sheet data",
            "Assets liabilities bulk",
            "Balance sheet bulk",
        ],
        related_terms=[
            "balance sheet",
            "assets",
            "liabilities",
            "equity",
            "financial position",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "balance_sheet_growth_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_balance_sheet_growth_bulk",
        natural_description=(
            "Get bulk balance sheet growth data. "
            "Returns year-over-year growth metrics for balance sheet items."
        ),
        example_queries=[
            "Get bulk balance sheet growth",
            "Batch asset growth",
            "Balance sheet growth bulk",
            "YoY balance sheet changes",
        ],
        related_terms=[
            "balance sheet growth",
            "asset growth",
            "liability growth",
            "YoY changes",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "cash_flow_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_cash_flow_bulk",
        natural_description=(
            "Get bulk cash flow statements. "
            "Returns comprehensive cash flow data for many companies."
        ),
        example_queries=[
            "Get bulk cash flow statements",
            "Batch cash flow data",
            "Operating cash flow bulk",
            "Cash flow bulk",
        ],
        related_terms=[
            "cash flow",
            "operating cash flow",
            "free cash flow",
            "cash from operations",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "cash_flow_growth_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_cash_flow_growth_bulk",
        natural_description=(
            "Get bulk cash flow growth data. "
            "Returns year-over-year growth metrics for cash flow items."
        ),
        example_queries=[
            "Get bulk cash flow growth",
            "Batch cash flow growth",
            "Operating cash flow growth bulk",
            "YoY cash flow changes",
        ],
        related_terms=[
            "cash flow growth",
            "FCF growth",
            "cash generation growth",
            "YoY cash flow",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "eod_bulk": EndpointSemantics(
        client_name="batch",
        method_name="get_eod_bulk",
        natural_description=(
            "Get bulk end-of-day prices. "
            "Returns closing price data for all stocks for a specific date."
        ),
        example_queries=[
            "Get bulk EOD prices",
            "Batch end-of-day data",
            "All closing prices for date",
            "EOD bulk data",
        ],
        related_terms=[
            "EOD",
            "end of day",
            "closing prices",
            "daily prices",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
}
