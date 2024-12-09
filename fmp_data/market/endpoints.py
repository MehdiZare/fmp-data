# fmp_data/market/endpoints.py
from fmp_data.market.models import (
    HistoricalData,
    IntradayPrice,
    MarketCapitalization,
    MarketHours,
    MarketMover,
    PrePostMarketQuote,
    Quote,
    SectorPerformance,
    SimpleQuote,
)
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    ParamLocation,
    ParamType,
)

QUOTE = Endpoint(
    name="quote",
    path="quote/{symbol}",
    version=APIVersion.V3,
    description="Get real-time stock quote",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[],
    response_model=Quote,
)

SIMPLE_QUOTE = Endpoint(
    name="simple_quote",
    path="quote-short/{symbol}",
    version=APIVersion.V3,
    description="Get simple stock quote",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[],
    response_model=SimpleQuote,
)

HISTORICAL_PRICE = Endpoint(
    name="historical_price",
    path="historical-price-full/{symbol}",
    version=APIVersion.V3,
    description="Get historical daily price data",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    response_model=HistoricalData,
)

INTRADAY_PRICE = Endpoint(
    name="intraday_price",
    path="historical-chart/{interval}/{symbol}",
    version=APIVersion.V3,
    description="Get intraday price data",
    mandatory_params=[
        EndpointParam(
            name="interval",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval (1min, 5min, 15min, 30min, 1hour, 4hour)",
        ),
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
    ],
    optional_params=[],
    response_model=IntradayPrice,
)

MARKET_HOURS = Endpoint(
    name="market_hours",
    path="is-the-market-open",
    version=APIVersion.V3,
    description="Get market trading hours information",
    mandatory_params=[],
    optional_params=[],
    response_model=MarketHours,
)

MARKET_CAP = Endpoint(
    name="market_cap",
    path="market-capitalization/{symbol}",
    version=APIVersion.V3,
    description="Get market capitalization data",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[],
    response_model=MarketCapitalization,
)

HISTORICAL_MARKET_CAP = Endpoint(
    name="historical_market_cap",
    path="historical-market-capitalization/{symbol}",
    version=APIVersion.V3,
    description="Get historical market capitalization data",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[],
    response_model=MarketCapitalization,
)

GAINERS = Endpoint(
    name="gainers",
    path="stock_market/gainers",
    version=APIVersion.V3,
    description="Get market gainers",
    mandatory_params=[],
    optional_params=[],
    response_model=MarketMover,
)

LOSERS = Endpoint(
    name="losers",
    path="stock_market/losers",
    version=APIVersion.V3,
    description="Get market losers",
    mandatory_params=[],
    optional_params=[],
    response_model=MarketMover,
)

MOST_ACTIVE = Endpoint(
    name="most_active",
    path="stock_market/actives",
    version=APIVersion.V3,
    description="Get most active stocks",
    mandatory_params=[],
    optional_params=[],
    response_model=MarketMover,
)

SECTOR_PERFORMANCE = Endpoint(
    name="sector_performance",
    path="sectors-performance",
    version=APIVersion.V3,
    description="Get sector performance data",
    mandatory_params=[],
    optional_params=[],
    response_model=SectorPerformance,
)

PRE_POST_MARKET = Endpoint(
    name="pre_post_market",
    path="pre-post-market",
    version=APIVersion.V4,
    description="Get pre/post market data",
    mandatory_params=[],
    optional_params=[],
    response_model=PrePostMarketQuote,
)
