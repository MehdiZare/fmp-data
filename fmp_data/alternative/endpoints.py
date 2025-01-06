# fmp_data/alternative/endpoints.py

from fmp_data.alternative.models import (
    Commodity,
    CommodityIntradayPrice,
    CommodityPriceHistory,
    CommodityQuote,
    CryptoHistoricalData,
    CryptoIntradayPrice,
    CryptoPair,
    CryptoQuote,
    ForexIntradayPrice,
    ForexPair,
    ForexPriceHistory,
    ForexQuote,
)
from fmp_data.alternative.schema import (
    CommoditiesListArgs,
    CommoditiesQuotesArgs,
    CommodityHistoricalArgs,
    CommodityIntradayArgs,
    CommodityQuoteArgs,
    CryptoHistoricalArgs,
    CryptoIntradayArgs,
    CryptoListArgs,
    CryptoQuoteArgs,
    CryptoQuotesArgs,
    ForexHistoricalArgs,
    ForexIntradayArgs,
    ForexListArgs,
    ForexQuoteArgs,
    ForexQuotesArgs,
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

# Validation constants
VALID_INTERVALS = ["1min", "5min", "15min", "30min", "1hour", "4hour"]

CRYPTO_LIST: Endpoint = Endpoint(
    name="crypto_list",
    path="symbol/available-cryptocurrencies",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get a comprehensive list of all available cryptocurrencies and "
        "their basic information including symbol, name, and exchange details"
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=CryptoPair,
    arg_model=CryptoListArgs,
    example_queries=[
        "List all available cryptocurrencies",
        "Get cryptocurrency trading pairs",
        "Show supported crypto symbols",
        "What cryptocurrencies can I trade?",
    ],
)

CRYPTO_QUOTES: Endpoint = Endpoint(
    name="crypto_quotes",
    path="quotes/crypto",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Retrieve real-time price quotes for all available cryptocurrencies "
        "including current price, daily change, volume and other key metrics"
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=CryptoQuote,
    arg_model=CryptoQuotesArgs,
    example_queries=[
        "Get current prices for all cryptocurrencies",
        "Show real-time crypto quotes",
        "What are the latest cryptocurrency prices?",
        "Get live crypto market data",
    ],
)

CRYPTO_QUOTE: Endpoint = Endpoint(
    name="crypto_quote",
    path="quote/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get detailed real-time price quote and trading information for "
        "a specific cryptocurrency including price, volume, change percentage, "
        "and market metrics"
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Crypto pair symbol (e.g., BTCUSD)",
        )
    ],
    optional_params=[],
    response_model=CryptoQuote,
    arg_model=CryptoQuoteArgs,
    example_queries=[
        "Get Bitcoin price quote",
        "Show current price for ETH",
        "What is the latest price of BTCUSD?",
        "Get detailed quote for a specific cryptocurrency",
    ],
)

CRYPTO_HISTORICAL: Endpoint = Endpoint(
    name="crypto_historical",
    path="historical-price-full/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Retrieve historical price data for a cryptocurrency over "
        "a specified date range, including daily OHLCV "
        "(Open, High, Low, Close, Volume) data and adjusted prices"
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Crypto pair symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="End date",
            alias="to",
        ),
    ],
    response_model=CryptoHistoricalData,
    arg_model=CryptoHistoricalArgs,
    example_queries=[
        "Get Bitcoin historical prices",
        "Show ETH price history for last month",
        "Historical crypto data between dates",
        "Get historical OHLCV data for cryptocurrency",
    ],
)

CRYPTO_INTRADAY: Endpoint = Endpoint(
    name="crypto_intraday",
    path="historical-chart/{interval}/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get detailed intraday price data for a cryptocurrency at "
        "specified time intervals, perfect for short-term trading "
        "analysis and high-frequency data needs"
    ),
    mandatory_params=[
        EndpointParam(
            name="interval",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval between data points",
            valid_values=VALID_INTERVALS,
        ),
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Crypto pair symbol",
        ),
    ],
    optional_params=[],
    response_model=CryptoIntradayPrice,
    arg_model=CryptoIntradayArgs,
    example_queries=[
        "Get Bitcoin minute-by-minute prices",
        "Show hourly cryptocurrency data",
        "Get intraday crypto prices",
        "Get 5-minute interval prices for ETH",
    ],
)

FOREX_LIST: Endpoint = Endpoint(
    name="forex_list",
    path="symbol/available-forex-currency-pairs",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get a complete list of available forex currency pairs with "
        "their symbols and basic trading information"
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=ForexPair,
    arg_model=ForexListArgs,
    example_queries=[
        "List all forex pairs",
        "Show available currency pairs",
        "What forex pairs can I trade?",
        "Get forex trading pairs list",
    ],
)

FOREX_QUOTES: Endpoint = Endpoint(
    name="forex_quotes",
    path="quotes/forex",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Retrieve real-time quotes for all available forex currency pairs "
        "including current exchange rates and daily changes"
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=ForexQuote,
    arg_model=ForexQuotesArgs,
    example_queries=[
        "Get all forex quotes",
        "Show current exchange rates",
        "Get live forex prices",
        "Current forex market rates",
    ],
)

FOREX_QUOTE: Endpoint = Endpoint(
    name="forex_quote",
    path="quote/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get detailed real-time quote for a specific forex "
        "currency pair including current rate, daily change, and trading metrics"
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Forex pair symbol",
        )
    ],
    optional_params=[],
    response_model=ForexQuote,
    arg_model=ForexQuoteArgs,
    example_queries=[
        "Get EURUSD exchange rate",
        "Show current price for GBPUSD",
        "What is the latest USDJPY rate?",
        "Get forex pair quote",
    ],
)

FOREX_HISTORICAL: Endpoint = Endpoint(
    name="forex_historical",
    path="historical-price-full/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Access historical exchange rate data for forex pairs "
        "over a specified date range, including daily rates and price changes"
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Forex pair symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="End date",
            alias="to",
        ),
    ],
    response_model=ForexPriceHistory,
    arg_model=ForexHistoricalArgs,
    example_queries=[
        "Get historical EURUSD rates",
        "Show forex pair price history",
        "Historical exchange rates between dates",
        "Get past forex prices",
    ],
)

FOREX_INTRADAY: Endpoint = Endpoint(
    name="forex_intraday",
    path="historical-chart/{interval}/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Retrieve intraday exchange rate data for forex pairs "
        "at specified intervals, ideal for day trading and "
        "short-term analysis"
    ),
    mandatory_params=[
        EndpointParam(
            name="interval",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval between data points",
            valid_values=VALID_INTERVALS,
        ),
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Forex pair symbol",
        ),
    ],
    optional_params=[],
    response_model=ForexIntradayPrice,
    arg_model=ForexIntradayArgs,
    example_queries=[
        "Get minute-by-minute EURUSD data",
        "Show hourly forex rates",
        "Get intraday currency prices",
        "5-minute interval forex data",
    ],
)

COMMODITIES_LIST: Endpoint = Endpoint(
    name="commodities_list",
    path="symbol/available-commodities",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get a comprehensive list of all available commodity "
        "symbols and their basic trading information"
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=Commodity,
    arg_model=CommoditiesListArgs,
    example_queries=[
        "List all commodities",
        "Show available commodity symbols",
        "What commodities can I trade?",
        "Get commodities trading list",
    ],
)

COMMODITIES_QUOTES: Endpoint = Endpoint(
    name="commodities_quotes",
    path="quotes/commodity",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Retrieve real-time quotes for all available commodities "
        "including current prices, daily changes, and trading volumes"
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=CommodityQuote,
    arg_model=CommoditiesQuotesArgs,
    example_queries=[
        "Get all commodity prices",
        "Show current commodity quotes",
        "Get live commodity market data",
        "Latest commodities prices",
    ],
)

COMMODITY_QUOTE: Endpoint = Endpoint(
    name="commodity_quote",
    path="quote/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get detailed real-time price quote for a specific commodity "
        "including current price, daily change, trading volume and "
        "other key market metrics"
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Commodity symbol (e.g., GC for Gold, CL for Crude Oil)",
        )
    ],
    optional_params=[],
    response_model=CommodityQuote,
    arg_model=CommodityQuoteArgs,
    example_queries=[
        "Get gold price quote",
        "Show current oil price",
        "What is the latest silver price?",
        "Get real-time commodity quote",
        "Current price for specific commodity",
    ],
)

COMMODITY_HISTORICAL: Endpoint = Endpoint(
    name="commodity_historical",
    path="historical-price-full/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Retrieve comprehensive historical price data for a "
        "commodity over a specified date range, including "
        "daily OHLCV (Open, High, Low, Close, Volume) data, "
        "adjusted prices, and price change metrics"
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Commodity symbol (e.g., GC, CL, SI)",
        )
    ],
    optional_params=[
        EndpointParam(
            name="start_date",  # Changed from "from"
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date for historical data",
        ),
        EndpointParam(
            name="end_date",  # Changed from "to"
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date for historical data",
        ),
    ],
    response_model=CommodityPriceHistory,
    arg_model=CommodityHistoricalArgs,
    example_queries=[
        "Get gold price history",
        "Show historical oil prices",
        "Get commodity prices between dates",
        "Historical OHLCV data for commodity",
        "Past price data for precious metals",
        "Get commodity price trends",
    ],
)

COMMODITY_INTRADAY: Endpoint = Endpoint(
    name="commodity_intraday",
    path="historical-chart/{interval}/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Access detailed intraday price data for commodities "
        "at specified time intervals. Provides high-frequency "
        "price data including open, high, low, close prices and volume"
    ),
    mandatory_params=[
        EndpointParam(
            name="interval",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval between data points",
            valid_values=VALID_INTERVALS,
        ),
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Commodity symbol",
        ),
    ],
    optional_params=[],
    response_model=CommodityIntradayPrice,
    arg_model=CommodityIntradayArgs,
    example_queries=[
        "Get minute-by-minute gold prices",
        "Show hourly oil price data",
        "Get intraday commodity prices",
        "5-minute interval silver prices",
        "Get high-frequency commodity data",
        "Real-time commodity price updates",
    ],
)
