# fmp_data/batch/endpoints.py
from fmp_data.batch.models import (
    AftermarketQuote,
    AftermarketTrade,
    BatchMarketCap,
    BatchQuote,
    BatchQuoteShort,
)
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    HTTPMethod,
    ParamLocation,
    ParamType,
    URLType,
)

BATCH_QUOTE: Endpoint = Endpoint(
    name="batch_quote",
    path="batch-quote",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get real-time quotes for multiple symbols in a single request",
    mandatory_params=[
        EndpointParam(
            name="symbols",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Comma-separated list of stock symbols",
        )
    ],
    optional_params=[],
    response_model=BatchQuote,
    example_queries=[
        "Get quotes for AAPL, MSFT, GOOGL",
        "Batch quote for multiple stocks",
        "Real-time quotes for symbol list",
    ],
)

BATCH_QUOTE_SHORT: Endpoint = Endpoint(
    name="batch_quote_short",
    path="batch-quote-short",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get quick price snapshots for multiple symbols",
    mandatory_params=[
        EndpointParam(
            name="symbols",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Comma-separated list of stock symbols",
        )
    ],
    optional_params=[],
    response_model=BatchQuoteShort,
    example_queries=[
        "Quick quotes for AAPL, MSFT",
        "Short batch quote",
        "Price snapshot for multiple symbols",
    ],
)

BATCH_AFTERMARKET_TRADE: Endpoint = Endpoint(
    name="batch_aftermarket_trade",
    path="batch-aftermarket-trade",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get aftermarket (post-market) trade data for multiple symbols",
    mandatory_params=[
        EndpointParam(
            name="symbols",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Comma-separated list of stock symbols",
        )
    ],
    optional_params=[],
    response_model=AftermarketTrade,
    example_queries=[
        "Get aftermarket trades for AAPL, TSLA",
        "Post-market trading data",
        "After hours trade data",
    ],
)

BATCH_AFTERMARKET_QUOTE: Endpoint = Endpoint(
    name="batch_aftermarket_quote",
    path="batch-aftermarket-quote",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get aftermarket quote data for multiple symbols",
    mandatory_params=[
        EndpointParam(
            name="symbols",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Comma-separated list of stock symbols",
        )
    ],
    optional_params=[],
    response_model=AftermarketQuote,
    example_queries=[
        "Get aftermarket quotes for AAPL, MSFT",
        "Post-market bid/ask data",
        "After hours quote data",
    ],
)

BATCH_EXCHANGE_QUOTE: Endpoint = Endpoint(
    name="batch_exchange_quote",
    path="batch-exchange-quote",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get quotes for all stocks on a specific exchange",
    mandatory_params=[
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Exchange code (e.g., NYSE, NASDAQ)",
        )
    ],
    optional_params=[
        EndpointParam(
            name="short",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            required=False,
            description="Return short quote data only",
        )
    ],
    response_model=BatchQuote,
    example_queries=[
        "Get all NYSE stock quotes",
        "NASDAQ exchange quotes",
        "All stocks on exchange",
    ],
)

BATCH_MUTUALFUND_QUOTES: Endpoint = Endpoint(
    name="batch_mutualfund_quotes",
    path="batch-mutualfund-quotes",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get batch quotes for all mutual funds",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="short",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            required=False,
            description="Return short quote data only",
        )
    ],
    response_model=BatchQuote,
    example_queries=[
        "Get all mutual fund quotes",
        "Batch mutual fund prices",
        "All mutual fund data",
    ],
)

BATCH_ETF_QUOTES: Endpoint = Endpoint(
    name="batch_etf_quotes",
    path="batch-etf-quotes",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get batch quotes for all ETFs",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="short",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            required=False,
            description="Return short quote data only",
        )
    ],
    response_model=BatchQuote,
    example_queries=[
        "Get all ETF quotes",
        "Batch ETF prices",
        "All ETF data",
    ],
)

BATCH_COMMODITY_QUOTES: Endpoint = Endpoint(
    name="batch_commodity_quotes",
    path="batch-commodity-quotes",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get batch quotes for all commodities",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="short",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            required=False,
            description="Return short quote data only",
        )
    ],
    response_model=BatchQuote,
    example_queries=[
        "Get all commodity quotes",
        "Batch commodity prices",
        "All commodity data",
    ],
)

BATCH_CRYPTO_QUOTES: Endpoint = Endpoint(
    name="batch_crypto_quotes",
    path="batch-crypto-quotes",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get batch quotes for all cryptocurrencies",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="short",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            required=False,
            description="Return short quote data only",
        )
    ],
    response_model=BatchQuote,
    example_queries=[
        "Get all crypto quotes",
        "Batch cryptocurrency prices",
        "All crypto data",
    ],
)

BATCH_FOREX_QUOTES: Endpoint = Endpoint(
    name="batch_forex_quotes",
    path="batch-forex-quotes",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get batch quotes for all forex pairs",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="short",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            required=False,
            description="Return short quote data only",
        )
    ],
    response_model=BatchQuote,
    example_queries=[
        "Get all forex quotes",
        "Batch forex rates",
        "All currency pair data",
    ],
)

BATCH_INDEX_QUOTES: Endpoint = Endpoint(
    name="batch_index_quotes",
    path="batch-index-quotes",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get batch quotes for all market indexes",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="short",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            required=False,
            description="Return short quote data only",
        )
    ],
    response_model=BatchQuote,
    example_queries=[
        "Get all index quotes",
        "Batch index prices",
        "All market index data",
    ],
)

BATCH_MARKET_CAP: Endpoint = Endpoint(
    name="batch_market_cap",
    path="market-capitalization-batch",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get market capitalization for multiple symbols",
    mandatory_params=[
        EndpointParam(
            name="symbols",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Comma-separated list of stock symbols",
        )
    ],
    optional_params=[],
    response_model=BatchMarketCap,
    example_queries=[
        "Get market cap for AAPL, MSFT, GOOGL",
        "Batch market capitalization",
        "Multiple company market caps",
    ],
)

PROFILE_BULK: Endpoint = Endpoint(
    name="profile_bulk",
    path="profile-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get company profile data in bulk",
    mandatory_params=[
        EndpointParam(
            name="part",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Profile data partition identifier",
        )
    ],
    optional_params=[],
    response_model=bytes,
)

DCF_BULK: Endpoint = Endpoint(
    name="dcf_bulk",
    path="dcf-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get discounted cash flow valuations in bulk",
    mandatory_params=[],
    optional_params=[],
    response_model=bytes,
)

RATING_BULK: Endpoint = Endpoint(
    name="rating_bulk",
    path="rating-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get stock ratings in bulk",
    mandatory_params=[],
    optional_params=[],
    response_model=bytes,
)

SCORES_BULK: Endpoint = Endpoint(
    name="scores_bulk",
    path="scores-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get financial scores in bulk",
    mandatory_params=[],
    optional_params=[],
    response_model=bytes,
)

RATIOS_TTM_BULK: Endpoint = Endpoint(
    name="ratios_ttm_bulk",
    path="ratios-ttm-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get trailing twelve month financial ratios in bulk",
    mandatory_params=[],
    optional_params=[],
    response_model=bytes,
)

PRICE_TARGET_SUMMARY_BULK: Endpoint = Endpoint(
    name="price_target_summary_bulk",
    path="price-target-summary-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get bulk price target summary data",
    mandatory_params=[],
    optional_params=[],
    response_model=bytes,
)

ETF_HOLDER_BULK: Endpoint = Endpoint(
    name="etf_holder_bulk",
    path="etf-holder-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get ETF holdings in bulk",
    mandatory_params=[
        EndpointParam(
            name="part",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="ETF holdings partition identifier",
        )
    ],
    optional_params=[],
    response_model=bytes,
)

UPGRADES_DOWNGRADES_CONSENSUS_BULK: Endpoint = Endpoint(
    name="upgrades_downgrades_consensus_bulk",
    path="upgrades-downgrades-consensus-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get upgrades/downgrades consensus data in bulk",
    mandatory_params=[],
    optional_params=[],
    response_model=bytes,
)

KEY_METRICS_TTM_BULK: Endpoint = Endpoint(
    name="key_metrics_ttm_bulk",
    path="key-metrics-ttm-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get trailing twelve month key metrics in bulk",
    mandatory_params=[],
    optional_params=[],
    response_model=bytes,
)

PEERS_BULK: Endpoint = Endpoint(
    name="peers_bulk",
    path="peers-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get peer lists for all symbols in bulk",
    mandatory_params=[],
    optional_params=[],
    response_model=bytes,
)

EARNINGS_SURPRISES_BULK: Endpoint = Endpoint(
    name="earnings_surprises_bulk",
    path="earnings-surprises-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get earnings surprises in bulk for a given year",
    mandatory_params=[
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Earnings year",
        )
    ],
    optional_params=[],
    response_model=bytes,
)

INCOME_STATEMENT_BULK: Endpoint = Endpoint(
    name="income_statement_bulk",
    path="income-statement-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get income statements in bulk",
    mandatory_params=[
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Filing year",
        ),
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Reporting period",
            valid_values=["Q1", "Q2", "Q3", "Q4", "FY"],
        ),
    ],
    optional_params=[],
    response_model=bytes,
)

INCOME_STATEMENT_GROWTH_BULK: Endpoint = Endpoint(
    name="income_statement_growth_bulk",
    path="income-statement-growth-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get income statement growth in bulk",
    mandatory_params=[
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Filing year",
        ),
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Reporting period",
            valid_values=["Q1", "Q2", "Q3", "Q4", "FY"],
        ),
    ],
    optional_params=[],
    response_model=bytes,
)

BALANCE_SHEET_STATEMENT_BULK: Endpoint = Endpoint(
    name="balance_sheet_statement_bulk",
    path="balance-sheet-statement-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get balance sheet statements in bulk",
    mandatory_params=[
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Filing year",
        ),
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Reporting period",
            valid_values=["Q1", "Q2", "Q3", "Q4", "FY"],
        ),
    ],
    optional_params=[],
    response_model=bytes,
)

BALANCE_SHEET_STATEMENT_GROWTH_BULK: Endpoint = Endpoint(
    name="balance_sheet_statement_growth_bulk",
    path="balance-sheet-statement-growth-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get balance sheet statement growth in bulk",
    mandatory_params=[
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Filing year",
        ),
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Reporting period",
            valid_values=["Q1", "Q2", "Q3", "Q4", "FY"],
        ),
    ],
    optional_params=[],
    response_model=bytes,
)

CASH_FLOW_STATEMENT_BULK: Endpoint = Endpoint(
    name="cash_flow_statement_bulk",
    path="cash-flow-statement-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get cash flow statements in bulk",
    mandatory_params=[
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Filing year",
        ),
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Reporting period",
            valid_values=["Q1", "Q2", "Q3", "Q4", "FY"],
        ),
    ],
    optional_params=[],
    response_model=bytes,
)

CASH_FLOW_STATEMENT_GROWTH_BULK: Endpoint = Endpoint(
    name="cash_flow_statement_growth_bulk",
    path="cash-flow-statement-growth-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get cash flow statement growth in bulk",
    mandatory_params=[
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Filing year",
        ),
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Reporting period",
            valid_values=["Q1", "Q2", "Q3", "Q4", "FY"],
        ),
    ],
    optional_params=[],
    response_model=bytes,
)

EOD_BULK: Endpoint = Endpoint(
    name="eod_bulk",
    path="eod-bulk",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get end-of-day prices in bulk",
    mandatory_params=[
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="End-of-day date",
        )
    ],
    optional_params=[],
    response_model=bytes,
)
