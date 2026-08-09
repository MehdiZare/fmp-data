# fmp_data/investment/endpoints.py
from fmp_data.investment.models import (
    ETFCountryWeighting,
    ETFExposure,
    ETFHolder,
    ETFHolding,
    ETFInfo,
    ETFPortfolioDate,
    ETFSectorWeighting,
    FundDisclosureHolderLatest,
    FundDisclosureHolding,
    FundDisclosureSearchResult,
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
    path="etf/holdings",
    version=APIVersion.STABLE,
    description="Get ETF holdings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Holdings date (YYYY-MM-DD)",
        ),
    ],
    response_model=ETFHolding,
)

ETF_HOLDING_DATES: Endpoint = Endpoint(
    name="etf_holding_dates",
    path="etf/portfolio-dates",
    version=APIVersion.STABLE,
    description=(
        "DEPRECATED and non-functional: etf/portfolio-dates 404s. Do not "
        "select it. Use the live funds/disclosure-dates endpoint, which "
        "returns a date/year/quarter record per period."
    ),
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
    path="etf/info",
    version=APIVersion.STABLE,
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
    path="etf/sector-weightings",
    version=APIVersion.STABLE,
    description="Get ETF sector weightings",
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
    response_model=ETFSectorWeighting,
)

ETF_COUNTRY_WEIGHTINGS: Endpoint = Endpoint(
    name="etf_country_weightings",
    path="etf/country-weightings",
    version=APIVersion.STABLE,
    description="Get ETF country weightings",
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
    response_model=ETFCountryWeighting,
)

ETF_EXPOSURE: Endpoint = Endpoint(
    name="etf_exposure",
    path="etf/asset-exposure",
    version=APIVersion.STABLE,
    description="Get ETF stock exposure",
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
    response_model=ETFExposure,
)

ETF_HOLDER: Endpoint = Endpoint(
    name="etf_holder",
    path="etf/holder",
    version=APIVersion.STABLE,
    description=(
        "DEPRECATED and non-functional: etf/holder 404s. Do not select it. "
        "The closest live endpoint is funds/disclosure-holders-latest, which "
        "returns holder/shares/change/weightPercent, not asset-level rows."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
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
    path="funds/disclosure-dates",
    version=APIVersion.STABLE,
    description="Get mutual fund/ETF disclosure dates",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Fund or ETF symbol",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.CIK,
            required=False,
            description="Fund CIK",
        ),
    ],
    response_model=PortfolioDate,
)

# The `date` param below disagrees with ETF_HOLDINGS' on both counts: it is
# declared mandatory rather than optional, and ParamType.STRING rather than
# ParamType.DATE (STRING skips date validation and coercion, so a malformed
# date reaches the API as-is instead of failing locally -- the #131/#134
# drift class).
#
# Neither is corrected here, because neither can be *verified*. Probed on
# 2026-08-08: this path returns 404 for every request, every symbol, with and
# without `date`, as do `funds/holdings`, `mutual-fund/holdings` and
# `fund-holdings`. Meanwhile `etf/holdings?symbol=VFIAX` -- a mutual fund --
# returns 200 with 509 rows, suggesting FMP consolidated both product types
# onto etf/holdings. What to do about that is #152; editing these
# declarations to match an endpoint that never answers would be a guess
# dressed up as a fix. Revisit this param and MutualFundHoldingsArgs.date
# together once #152 settles where this endpoint should point.
MUTUAL_FUND_HOLDINGS: Endpoint = Endpoint(
    name="mutual_fund_holdings",
    path="mutual-fund-holdings",
    version=APIVersion.STABLE,
    description=(
        "DEPRECATED and non-functional: mutual-fund-holdings 404s. Do not "
        "select it. Use the live etf/holdings endpoint, which serves mutual "
        "fund symbols too, or funds/disclosure for full N-PORT detail."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
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
    version=APIVersion.STABLE,
    description=(
        "DEPRECATED and non-functional: mutual-fund-holdings/name 404s and "
        "has no replacement -- every path variant probed also 404s. Do not "
        "select it. search-name is a generic symbol search, not fund holdings."
    ),
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
    path="etf/holder",
    version=APIVersion.STABLE,
    description=(
        "DEPRECATED and non-functional: etf/holder 404s, and this endpoint "
        "declared the same path as etf_holder. Do not select it. The closest "
        "live endpoint is funds/disclosure-holders-latest."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[],
    response_model=MutualFundHolder,
)

FUNDS_DISCLOSURE_HOLDERS_LATEST: Endpoint = Endpoint(
    name="funds_disclosure_holders_latest",
    path="funds/disclosure-holders-latest",
    version=APIVersion.STABLE,
    description="Get latest mutual fund/ETF disclosure holders",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Fund or ETF symbol",
        )
    ],
    optional_params=[],
    response_model=FundDisclosureHolderLatest,
)

FUNDS_DISCLOSURE: Endpoint = Endpoint(
    name="funds_disclosure",
    path="funds/disclosure",
    version=APIVersion.STABLE,
    description="Get mutual fund/ETF disclosure holdings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Fund or ETF symbol",
        ),
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Disclosure year",
        ),
        EndpointParam(
            name="quarter",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Disclosure quarter (1-4)",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.CIK,
            required=False,
            description="Fund CIK",
        ),
    ],
    response_model=FundDisclosureHolding,
)

FUNDS_DISCLOSURE_HOLDERS_SEARCH: Endpoint = Endpoint(
    name="funds_disclosure_holders_search",
    path="funds/disclosure-holders-search",
    version=APIVersion.STABLE,
    description="Search mutual fund/ETF disclosure holders by name",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Fund or ETF name",
        )
    ],
    optional_params=[],
    response_model=FundDisclosureSearchResult,
)
