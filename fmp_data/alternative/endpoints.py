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
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    HTTPMethod,
    ParamLocation,
    ParamType,
    URLType,
)

CRYPTO_LIST = Endpoint(
    name="crypto_list",
    path="symbol/available-cryptocurrencies",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get list of available cryptocurrencies",
    mandatory_params=[],
    optional_params=[],
    response_model=CryptoPair,
)

CRYPTO_QUOTES = Endpoint(
    name="crypto_quotes",
    path="quotes/crypto",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get cryptocurrency quotes",
    mandatory_params=[],
    optional_params=[],
    response_model=CryptoQuote,
)

CRYPTO_QUOTE = Endpoint(
    name="crypto_quote",
    path="quote/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get cryptocurrency quote",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Crypto pair symbol",
        )
    ],
    optional_params=[],
    response_model=CryptoQuote,
)

CRYPTO_HISTORICAL = Endpoint(
    name="crypto_historical",
    path="historical-price-full/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get cryptocurrency historical prices",
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
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
        ),
    ],
    response_model=CryptoHistoricalData,
)

CRYPTO_INTRADAY = Endpoint(
    name="crypto_intraday",
    path="historical-chart/{interval}/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get cryptocurrency intraday prices",
    mandatory_params=[
        EndpointParam(
            name="interval",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
            valid_values=["1min", "5min", "15min", "30min", "1hour", "4hour"],
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
)

FOREX_LIST = Endpoint(
    name="forex_list",
    path="symbol/available-forex-currency-pairs",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get list of available forex pairs",
    mandatory_params=[],
    optional_params=[],
    response_model=ForexPair,
)

FOREX_QUOTES = Endpoint(
    name="forex_quotes",
    path="quotes/forex",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get forex quotes",
    mandatory_params=[],
    optional_params=[],
    response_model=ForexQuote,
)

FOREX_QUOTE = Endpoint(
    name="forex_quote",
    path="quote/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get forex quote",
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
)

FOREX_HISTORICAL = Endpoint(
    name="forex_historical",
    path="historical-price-full/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get forex historical prices",
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
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
        ),
    ],
    response_model=ForexPriceHistory,
)

FOREX_INTRADAY = Endpoint(
    name="forex_intraday",
    path="historical-chart/{interval}/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get forex intraday prices",
    mandatory_params=[
        EndpointParam(
            name="interval",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
            valid_values=["1min", "5min", "15min", "30min", "1hour", "4hour"],
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
)

COMMODITIES_LIST = Endpoint(
    name="commodities_list",
    path="symbol/available-commodities",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get list of available commodities",
    mandatory_params=[],
    optional_params=[],
    response_model=Commodity,
)

COMMODITIES_QUOTES = Endpoint(
    name="commodities_quotes",
    path="quotes/commodity",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get commodities quotes",
    mandatory_params=[],
    optional_params=[],
    response_model=CommodityQuote,
)

COMMODITY_QUOTE = Endpoint(
    name="commodity_quote",
    path="quote/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get commodity quote",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
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
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get commodity historical prices",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Commodity symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
        ),
    ],
    response_model=CommodityPriceHistory,
)

COMMODITY_INTRADAY = Endpoint(
    name="commodity_intraday",
    path="historical-chart/{interval}/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get commodity intraday prices",
    mandatory_params=[
        EndpointParam(
            name="interval",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
            valid_values=["1min", "5min", "15min", "30min", "1hour", "4hour"],
        ),
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Commodity symbol",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
        ),
    ],
    response_model=CommodityIntradayPrice,
)
