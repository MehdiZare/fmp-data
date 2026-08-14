# fmp_data/alternative/endpoints.py

from fmp_data.alternative.models import (
    Commodity,
    CommodityHistoricalPrice,
    CommodityIntradayPrice,
    CommodityQuote,
    CryptoHistoricalPrice,
    CryptoIntradayPrice,
    CryptoPair,
    CryptoQuote,
    ForexHistoricalPrice,
    ForexIntradayPrice,
    ForexPair,
    ForexQuote,
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
from fmp_data.schema import INTERVAL_VALUES

# Validation constants
VALID_INTERVALS = list(INTERVAL_VALUES)

CRYPTO_LIST: Endpoint[CryptoPair] = Endpoint(
    name="crypto_list",
    path="cryptocurrency-list",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get a comprehensive list of all available cryptocurrencies and "
        "their basic information including symbol, name, and exchange details"
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=CryptoPair,
    example_queries=[
        "List all available cryptocurrencies",
        "Get cryptocurrency trading pairs",
        "Show supported crypto symbols",
        "What cryptocurrencies can I trade?",
    ],
)

CRYPTO_QUOTES: Endpoint[CryptoQuote] = Endpoint(
    name="crypto_quotes",
    path="quotes/crypto",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "DEPRECATED and non-functional: quotes/crypto 404s. Do not select it. "
        "The live equivalent is the batch client's batch-crypto-quotes, which "
        "returns symbol, price, change and volume only."
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=CryptoQuote,
    example_queries=[
        "Get current prices for all cryptocurrencies",
        "Show real-time crypto quotes",
        "What are the latest cryptocurrency prices?",
        "Get live crypto market data",
    ],
)

CRYPTO_QUOTE: Endpoint[CryptoQuote] = Endpoint(
    name="crypto_quote",
    path="quote",
    version=APIVersion.STABLE,
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
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Crypto pair symbol (e.g., BTCUSD)",
        )
    ],
    optional_params=[],
    response_model=CryptoQuote,
    example_queries=[
        "Get Bitcoin price quote",
        "Show current price for ETH",
        "What is the latest price of BTCUSD?",
        "Get detailed quote for a specific cryptocurrency",
    ],
)

CRYPTO_HISTORICAL: Endpoint[CryptoHistoricalPrice] = Endpoint(
    name="crypto_historical",
    path="historical-price-eod/full",
    version=APIVersion.STABLE,
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
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Crypto pair symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
    ],
    response_model=CryptoHistoricalPrice,
    example_queries=[
        "Get Bitcoin historical prices",
        "Show ETH price history for last month",
        "Historical crypto data between dates",
        "Get historical OHLCV data for cryptocurrency",
    ],
)

CRYPTO_INTRADAY: Endpoint[CryptoIntradayPrice] = Endpoint(
    name="crypto_intraday",
    path="historical-chart/{interval}",
    version=APIVersion.STABLE,
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
            description="Time interval between data points",
            valid_values=VALID_INTERVALS,
        ),
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Crypto pair symbol",
        ),
    ],
    optional_params=[],
    response_model=CryptoIntradayPrice,
    example_queries=[
        "Get Bitcoin minute-by-minute prices",
        "Show hourly cryptocurrency data",
        "Get intraday crypto prices",
        "Get 5-minute interval prices for ETH",
    ],
)

FOREX_LIST: Endpoint[ForexPair] = Endpoint(
    name="forex_list",
    path="forex-list",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get a complete list of available forex currency pairs with "
        "their symbols and basic trading information"
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=ForexPair,
    example_queries=[
        "List all forex pairs",
        "Show available currency pairs",
        "What forex pairs can I trade?",
        "Get forex trading pairs list",
    ],
)

FOREX_QUOTES: Endpoint[ForexQuote] = Endpoint(
    name="forex_quotes",
    path="quotes/forex",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "DEPRECATED and non-functional: quotes/forex 404s. Do not select it. "
        "The live equivalent is the batch client's batch-forex-quotes, which "
        "returns symbol, price, change and volume only."
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=ForexQuote,
    example_queries=[
        "Get all forex quotes",
        "Show current exchange rates",
        "Get live forex prices",
        "Current forex market rates",
    ],
)

FOREX_QUOTE: Endpoint[ForexQuote] = Endpoint(
    name="forex_quote",
    path="quote",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get detailed real-time quote for a specific forex "
        "currency pair including current rate, daily change, and trading metrics"
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Forex pair symbol",
        )
    ],
    optional_params=[],
    response_model=ForexQuote,
    example_queries=[
        "Get EURUSD exchange rate",
        "Show current price for GBPUSD",
        "What is the latest USDJPY rate?",
        "Get forex pair quote",
    ],
)

FOREX_HISTORICAL: Endpoint[ForexHistoricalPrice] = Endpoint(
    name="forex_historical",
    path="historical-price-eod/full",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Access historical exchange rate data for forex pairs "
        "over a specified date range, including daily rates and price changes"
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Forex pair symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date",
            alias="to",
        ),
    ],
    response_model=ForexHistoricalPrice,
    example_queries=[
        "Get historical EURUSD rates",
        "Show forex pair price history",
        "Historical exchange rates between dates",
        "Get past forex prices",
    ],
)

FOREX_INTRADAY: Endpoint[ForexIntradayPrice] = Endpoint(
    name="forex_intraday",
    path="historical-chart/{interval}",
    version=APIVersion.STABLE,
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
            description="Time interval between data points",
            valid_values=VALID_INTERVALS,
        ),
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Forex pair symbol",
        ),
    ],
    optional_params=[],
    response_model=ForexIntradayPrice,
    example_queries=[
        "Get minute-by-minute EURUSD data",
        "Show hourly forex rates",
        "Get intraday currency prices",
        "5-minute interval forex data",
    ],
)

COMMODITIES_LIST: Endpoint[Commodity] = Endpoint(
    name="commodities_list",
    path="commodities-list",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get a comprehensive list of all available commodity "
        "symbols and their basic trading information"
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=Commodity,
    example_queries=[
        "List all commodities",
        "Show available commodity symbols",
        "What commodities can I trade?",
        "Get commodities trading list",
    ],
)

COMMODITIES_QUOTES: Endpoint[CommodityQuote] = Endpoint(
    name="commodities_quotes",
    path="quotes/commodity",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "DEPRECATED and non-functional: quotes/commodity 404s. Do not select "
        "it. The live equivalent is the batch client's batch-commodity-quotes, "
        "which returns symbol, price, change and volume only."
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=CommodityQuote,
    example_queries=[
        "Get all commodity prices",
        "Show current commodity quotes",
        "Get live commodity market data",
        "Latest commodities prices",
    ],
)

COMMODITY_QUOTE: Endpoint[CommodityQuote] = Endpoint(
    name="commodity_quote",
    path="quote",
    version=APIVersion.STABLE,
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
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Commodity symbol (e.g., GC for Gold, CL for Crude Oil)",
        )
    ],
    optional_params=[],
    response_model=CommodityQuote,
    example_queries=[
        "Get gold price quote",
        "Show current oil price",
        "What is the latest silver price?",
        "Get real-time commodity quote",
        "Current price for specific commodity",
    ],
)

COMMODITY_HISTORICAL: Endpoint[CommodityHistoricalPrice] = Endpoint(
    name="commodity_historical",
    path="historical-price-eod/full",
    version=APIVersion.STABLE,
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
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Commodity symbol (e.g., GC, CL, SI)",
        )
    ],
    optional_params=[
        EndpointParam(
            name="start_date",  # Changed from "from"
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date for historical data",
            alias="from",
        ),
        EndpointParam(
            name="end_date",  # Changed from "to"
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date for historical data",
            alias="to",
        ),
    ],
    response_model=CommodityHistoricalPrice,
    example_queries=[
        "Get gold price history",
        "Show historical oil prices",
        "Get commodity prices between dates",
        "Historical OHLCV data for commodity",
        "Past price data for precious metals",
        "Get commodity price trends",
    ],
)

COMMODITY_INTRADAY: Endpoint[CommodityIntradayPrice] = Endpoint(
    name="commodity_intraday",
    path="historical-chart/{interval}",
    version=APIVersion.STABLE,
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
            description="Time interval between data points",
            valid_values=VALID_INTERVALS,
        ),
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Commodity symbol",
        ),
    ],
    optional_params=[],
    response_model=CommodityIntradayPrice,
    example_queries=[
        "Get minute-by-minute gold prices",
        "Show hourly oil price data",
        "Get intraday commodity prices",
        "5-minute interval silver prices",
        "Get high-frequency commodity data",
        "Real-time commodity price updates",
    ],
)
