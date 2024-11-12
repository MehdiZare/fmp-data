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
from fmp_data.models import APIVersion, Endpoint, EndpointParam, ParamType

# Cryptocurrency endpoints
CRYPTO_LIST = Endpoint(
    name="crypto_list",
    path="symbol/available-cryptocurrencies",
    version=APIVersion.V3,
    description="Get list of available cryptocurrencies",
    mandatory_params=[],
    optional_params=[],
    response_model=CryptoPair,
)

CRYPTO_QUOTES = Endpoint(
    name="crypto_quotes",
    path="quotes/crypto",
    version=APIVersion.V3,
    description="Get cryptocurrency quotes",
    mandatory_params=[],
    optional_params=[],
    response_model=CryptoQuote,
)

CRYPTO_QUOTE = Endpoint(
    name="crypto_quote",
    path="quote/{symbol}",
    version=APIVersion.V3,
    description="Get cryptocurrency quote",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Crypto pair symbol",
        )
    ],
    response_model=CryptoQuote,
)

CRYPTO_HISTORICAL = Endpoint(
    name="crypto_historical",
    path="historical-price-full/{symbol}",
    version=APIVersion.V3,
    description="Get cryptocurrency historical prices",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Crypto pair symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="from",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="Start date",
        ),
        EndpointParam(
            name="to",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="End date",
        ),
    ],
    response_model=CryptoHistoricalPrice,
)

CRYPTO_INTRADAY = Endpoint(
    name="crypto_intraday",
    path="historical-chart/{interval}/{symbol}",
    version=APIVersion.V3,
    description="Get cryptocurrency intraday prices",
    mandatory_params=[
        EndpointParam(
            name="interval",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Time interval",
            valid_values=["1min", "5min", "15min", "30min", "1hour", "4hour"],
        ),
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Crypto pair symbol",
        ),
    ],
    response_model=CryptoIntradayPrice,
)

# Forex endpoints
FOREX_LIST = Endpoint(
    name="forex_list",
    path="symbol/available-forex-currency-pairs",
    version=APIVersion.V3,
    description="Get list of available forex pairs",
    mandatory_params=[],
    optional_params=[],
    response_model=ForexPair,
)

FOREX_QUOTES = Endpoint(
    name="forex_quotes",
    path="quotes/forex",
    version=APIVersion.V3,
    description="Get forex quotes",
    mandatory_params=[],
    optional_params=[],
    response_model=ForexQuote,
)

FOREX_QUOTE = Endpoint(
    name="forex_quote",
    path="quote/{symbol}",
    version=APIVersion.V3,
    description="Get forex quote",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Forex pair symbol",
        )
    ],
    optional_params=[],
    response_model=ForexQuote,
)

FOREX_HISTORICAL = Endpoint(
    name="forex_historical",
    path="historical-price-full/{symbol}",
    version=APIVersion.V3,
    description="Get forex historical prices",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Forex pair symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="from",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="Start date",
        ),
        EndpointParam(
            name="to",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="End date",
        ),
    ],
    response_model=ForexHistoricalPrice,
)

FOREX_INTRADAY = Endpoint(
    name="forex_intraday",
    path="historical-chart/{interval}/{symbol}",
    version=APIVersion.V3,
    description="Get forex intraday prices",
    mandatory_params=[
        EndpointParam(
            name="interval",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Time interval",
            valid_values=["1min", "5min", "15min", "30min", "1hour", "4hour"],
        ),
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Forex pair symbol",
        ),
    ],
    optional_params=[],
    response_model=ForexIntradayPrice,
)

# Commodities endpoints
COMMODITIES_LIST = Endpoint(
    name="commodities_list",
    path="symbol/available-commodities",
    version=APIVersion.V3,
    description="Get list of available commodities",
    mandatory_params=[],
    optional_params=[],
    response_model=Commodity,
)

COMMODITIES_QUOTES = Endpoint(
    name="commodities_quotes",
    path="quotes/commodity",
    version=APIVersion.V3,
    description="Get commodities quotes",
    mandatory_params=[],
    optional_params=[],
    response_model=CommodityQuote,
)

COMMODITY_QUOTE = Endpoint(
    name="commodity_quote",
    path="quote/{symbol}",
    version=APIVersion.V3,
    description="Get commodity quote",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Commodity symbol",
        )
    ],
    optional_params=[],
    response_model=CommodityQuote,
)

COMMODITY_HISTORICAL = Endpoint(
    name="commodity_historical",
    path="historical-price-full/{symbol}",
    version=APIVersion.V3,
    description="Get commodity historical prices",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Commodity symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="from",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="Start date",
        ),
        EndpointParam(
            name="to",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="End date",
        ),
    ],
    response_model=CommodityHistoricalPrice,
)

COMMODITY_INTRADAY = Endpoint(
    name="commodity_intraday",
    path="historical-chart/{interval}/{symbol}",
    version=APIVersion.V3,
    description="Get commodity intraday prices",
    mandatory_params=[
        EndpointParam(
            name="interval",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Time interval",
            valid_values=["1min", "5min", "15min", "30min", "1hour", "4hour"],
        ),
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Commodity symbol",
        ),
    ],
    optional_params=[],
    response_model=CommodityIntradayPrice,
)
