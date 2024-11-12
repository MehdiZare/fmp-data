# fmp_data/market/endpoints.py
from ..models import APIVersion, Endpoint, EndpointParam, ParamType
from .models import (
    HistoricalPrice,
    IntradayPrice,
    MarketCapitalization,
    MarketHours,
    MarketMover,
    PrePostMarketQuote,
    Quote,
    SectorPerformance,
    SimpleQuote,
)

QUOTE = Endpoint(
    name="quote",
    path="quote/{symbol}",
    version=APIVersion.V3,
    description="Get real-time stock quote",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol (ticker)",
        )
    ],
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
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol (ticker)",
        )
    ],
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
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[
        EndpointParam(
            name="from",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    response_model=HistoricalPrice,
)

INTRADAY_PRICE = Endpoint(
    name="intraday_price",
    path="historical-chart/{interval}/{symbol}",
    version=APIVersion.V3,
    description="Get intraday price data",
    mandatory_params=[
        EndpointParam(
            name="interval",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Time interval (1min, 5min, 15min, 30min, 1hour, 4hour)",
        ),
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol (ticker)",
        ),
    ],
    response_model=IntradayPrice,
)

MARKET_HOURS = Endpoint(
    name="market_hours",
    path="is-the-market-open",
    version=APIVersion.V3,
    description="Get market trading hours information",
    mandatory_params=[],
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
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol (ticker)",
        )
    ],
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
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol (ticker)",
        )
    ],
    response_model=MarketCapitalization,
)

GAINERS = Endpoint(
    name="gainers",
    path="stock_market/gainers",
    version=APIVersion.V3,
    description="Get market gainers",
    mandatory_params=[],
    response_model=MarketMover,
)

LOSERS = Endpoint(
    name="losers",
    path="stock_market/losers",
    version=APIVersion.V3,
    description="Get market losers",
    mandatory_params=[],
    response_model=MarketMover,
)

MOST_ACTIVE = Endpoint(
    name="most_active",
    path="stock_market/actives",
    version=APIVersion.V3,
    description="Get most active stocks",
    mandatory_params=[],
    response_model=MarketMover,
)

SECTOR_PERFORMANCE = Endpoint(
    name="sector_performance",
    path="sectors-performance",
    version=APIVersion.V3,
    description="Get sector performance data",
    mandatory_params=[],
    response_model=SectorPerformance,
)

PRE_POST_MARKET = Endpoint(
    name="pre_post_market",
    path="pre-post-market",
    version=APIVersion.V4,
    description="Get pre/post market data",
    mandatory_params=[],
    response_model=PrePostMarketQuote,
)