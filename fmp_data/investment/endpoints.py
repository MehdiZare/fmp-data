# fmp_data/investment/endpoints.py
from datetime import date

from fmp_data.investment.models import (
    ETFCountryWeighting,
    ETFExposure,
    ETFHolder,
    ETFHolding,
    ETFInfo,
    ETFSectorWeighting,
    MutualFundHolder,
    MutualFundHolding,
)
from fmp_data.models import APIVersion, Endpoint, EndpointParam, ParamType

# ETF endpoints
ETF_HOLDINGS = Endpoint(
    name="etf_holdings",
    path="etf-holdings",
    version=APIVersion.V4,
    description="Get ETF holdings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="ETF symbol",
        ),
        EndpointParam(
            name="date",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Holdings date",
        ),
    ],
    response_model=ETFHolding,
)

ETF_HOLDING_DATES = Endpoint(
    name="etf_holding_dates",
    path="etf-holdings/portfolio-date",
    version=APIVersion.V4,
    description="Get ETF holding dates",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="ETF symbol",
        )
    ],
    response_model=list[date],
)

ETF_INFO = Endpoint(
    name="etf_info",
    path="etf-info",
    version=APIVersion.V4,
    description="Get ETF information",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="ETF symbol",
        )
    ],
    response_model=ETFInfo,
)

ETF_SECTOR_WEIGHTINGS = Endpoint(
    name="etf_sector_weightings",
    path="etf-sector-weightings/{symbol}",
    version=APIVersion.V3,
    description="Get ETF sector weightings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="ETF symbol",
        )
    ],
    response_model=ETFSectorWeighting,
)

ETF_COUNTRY_WEIGHTINGS = Endpoint(
    name="etf_country_weightings",
    path="etf-country-weightings/{symbol}",
    version=APIVersion.V3,
    description="Get ETF country weightings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="ETF symbol",
        )
    ],
    response_model=ETFCountryWeighting,
)

ETF_EXPOSURE = Endpoint(
    name="etf_exposure",
    path="etf-stock-exposure/{symbol}",
    version=APIVersion.V3,
    description="Get ETF stock exposure",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="ETF symbol",
        )
    ],
    response_model=ETFExposure,
)

ETF_HOLDER = Endpoint(
    name="etf_holder",
    path="etf-holder/{symbol}",
    version=APIVersion.V3,
    description="Get ETF holder information",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
    response_model=ETFHolder,
)

# Mutual Fund endpoints
MUTUAL_FUND_DATES = Endpoint(
    name="mutual_fund_dates",
    path="mutual-fund-holdings/portfolio-date",
    version=APIVersion.V4,
    description="Get mutual fund dates",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Fund symbol",
        ),
        EndpointParam(
            name="cik",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Fund CIK",
        ),
    ],
    response_model=list[date],
)

MUTUAL_FUND_HOLDINGS = Endpoint(
    name="mutual_fund_holdings",
    path="mutual-fund-holdings",
    version=APIVersion.V4,
    description="Get mutual fund holdings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Fund symbol",
        ),
        EndpointParam(
            name="date",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Holdings date",
        ),
    ],
    response_model=MutualFundHolding,
)

MUTUAL_FUND_BY_NAME = Endpoint(
    name="mutual_fund_by_name",
    path="mutual-fund-holdings/name",
    version=APIVersion.V4,
    description="Get mutual funds by name",
    mandatory_params=[
        EndpointParam(
            name="name",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Fund name",
        )
    ],
    response_model=MutualFundHolding,
)

MUTUAL_FUND_HOLDER = Endpoint(
    name="mutual_fund_holder",
    path="mutual-fund-holder/{symbol}",
    version=APIVersion.V3,
    description="Get mutual fund holder information",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
    response_model=MutualFundHolder,
)
