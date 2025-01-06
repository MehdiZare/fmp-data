# fmp_data/investment/endpoints.py
from fmp_data.investment.models import (
    ETFCountryWeighting,
    ETFExposure,
    ETFHolder,
    ETFHolding,
    ETFInfo,
    ETFPortfolioDate,
    ETFSectorWeighting,
    MutualFundHolder,
    MutualFundHolding,
    PortfolioDate,
)
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    ParamLocation,
    ParamType,
)

# ETF endpoints
ETF_HOLDINGS: Endpoint = Endpoint(
    name="etf_holdings",
    path="etf-holdings",
    version=APIVersion.V4,
    description="Get ETF holdings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Holdings date",
        ),
    ],
    optional_params=[],
    response_model=ETFHolding,
)

ETF_HOLDING_DATES: Endpoint = Endpoint(
    name="etf_holding_dates",
    path="etf-holdings/portfolio-date",
    version=APIVersion.V4,
    description="Get ETF holding dates",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="ETF Symbol",
        )
    ],
    optional_params=[],
    response_model=ETFPortfolioDate,
)

ETF_INFO: Endpoint = Endpoint(
    name="etf_info",
    path="etf-info",
    version=APIVersion.V4,
    description="Get ETF information",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="ETF Symbol",
        )
    ],
    optional_params=[],
    response_model=ETFInfo,
)

ETF_SECTOR_WEIGHTINGS: Endpoint = Endpoint(
    name="etf_sector_weightings",
    path="etf-sector-weightings/{symbol}",
    version=APIVersion.V3,
    description="Get ETF sector weightings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="ETF Symbol",
        )
    ],
    optional_params=[],
    response_model=ETFSectorWeighting,
)

ETF_COUNTRY_WEIGHTINGS: Endpoint = Endpoint(
    name="etf_country_weightings",
    path="etf-country-weightings/{symbol}",
    version=APIVersion.V3,
    description="Get ETF country weightings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="ETF Symbol",
        )
    ],
    optional_params=[],
    response_model=ETFCountryWeighting,
)

ETF_EXPOSURE: Endpoint = Endpoint(
    name="etf_exposure",
    path="etf-stock-exposure/{symbol}",
    version=APIVersion.V3,
    description="Get ETF stock exposure",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="ETF Symbol",
        )
    ],
    optional_params=[],
    response_model=ETFExposure,
)

ETF_HOLDER: Endpoint = Endpoint(
    name="etf_holder",
    path="etf-holder/{symbol}",
    version=APIVersion.V3,
    description="Get ETF holder information",
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
    response_model=ETFHolder,
)

# Mutual Fund endpoints
MUTUAL_FUND_DATES: Endpoint = Endpoint(
    name="mutual_fund_dates",
    path="mutual-fund-holdings/portfolio-date",
    version=APIVersion.V4,
    description="Get mutual fund dates",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Fund symbol",
        ),
        EndpointParam(
            name="cik",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Fund cik",
        ),
    ],
    optional_params=[],
    response_model=PortfolioDate,
)

MUTUAL_FUND_HOLDINGS: Endpoint = Endpoint(
    name="mutual_fund_holdings",
    path="mutual-fund-holdings",
    version=APIVersion.V4,
    description="Get mutual fund holdings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Fund symbol",
        ),
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Holdings date",
        ),
    ],
    optional_params=[],
    response_model=MutualFundHolding,
)

MUTUAL_FUND_BY_NAME: Endpoint = Endpoint(
    name="mutual_fund_by_name",
    path="mutual-fund-holdings/name",
    version=APIVersion.V4,
    description="Get mutual funds by name",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Fund name",
        )
    ],
    optional_params=[],
    response_model=MutualFundHolding,
)

MUTUAL_FUND_HOLDER: Endpoint = Endpoint(
    name="mutual_fund_holder",
    path="mutual-fund-holder/{symbol}",
    version=APIVersion.V3,
    description="Get mutual fund holder information",
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
    response_model=MutualFundHolder,
)
