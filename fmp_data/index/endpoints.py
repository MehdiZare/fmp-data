# fmp_data/index/endpoints.py
from fmp_data.index.models import HistoricalIndexConstituent, IndexConstituent
from fmp_data.models import (
    APIVersion,
    Endpoint,
    HTTPMethod,
    URLType,
)

SP500_CONSTITUENTS: Endpoint = Endpoint(
    name="sp500_constituents",
    path="sp500-constituent",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get current S&P 500 index constituents",
    mandatory_params=[],
    optional_params=[],
    response_model=IndexConstituent,
    example_queries=[
        "Get S&P 500 components",
        "List all S&P 500 stocks",
        "S&P 500 constituents",
    ],
)

NASDAQ_CONSTITUENTS: Endpoint = Endpoint(
    name="nasdaq_constituents",
    path="nasdaq-constituent",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get current NASDAQ index constituents",
    mandatory_params=[],
    optional_params=[],
    response_model=IndexConstituent,
    example_queries=[
        "Get NASDAQ components",
        "List all NASDAQ stocks",
        "NASDAQ constituents",
    ],
)

DOWJONES_CONSTITUENTS: Endpoint = Endpoint(
    name="dowjones_constituents",
    path="dowjones-constituent",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get current Dow Jones Industrial Average constituents",
    mandatory_params=[],
    optional_params=[],
    response_model=IndexConstituent,
    example_queries=[
        "Get Dow Jones components",
        "List all Dow 30 stocks",
        "DJIA constituents",
    ],
)

HISTORICAL_SP500: Endpoint = Endpoint(
    name="historical_sp500",
    path="historical-sp500-constituent",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get historical S&P 500 constituent changes",
    mandatory_params=[],
    optional_params=[],
    response_model=HistoricalIndexConstituent,
    example_queries=[
        "Historical S&P 500 changes",
        "S&P 500 additions and removals",
        "S&P 500 constituent history",
    ],
)

HISTORICAL_NASDAQ: Endpoint = Endpoint(
    name="historical_nasdaq",
    path="historical-nasdaq-constituent",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get historical NASDAQ constituent changes",
    mandatory_params=[],
    optional_params=[],
    response_model=HistoricalIndexConstituent,
    example_queries=[
        "Historical NASDAQ changes",
        "NASDAQ additions and removals",
        "NASDAQ constituent history",
    ],
)

HISTORICAL_DOWJONES: Endpoint = Endpoint(
    name="historical_dowjones",
    path="historical-dowjones-constituent",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get historical Dow Jones constituent changes",
    mandatory_params=[],
    optional_params=[],
    response_model=HistoricalIndexConstituent,
    example_queries=[
        "Historical Dow Jones changes",
        "DJIA additions and removals",
        "Dow Jones constituent history",
    ],
)
