# fmp_data/fundamental/endpoints.py
from fmp_data.fundamental.models import (
    BalanceSheet,
    CashFlowStatement,
    FinancialRatios,
    FinancialReportDate,
    FinancialStatementFull,
    HistoricalRating,
    IncomeStatement,
    KeyMetrics,
    LeveredDCF,
    OwnerEarnings,
)
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    ParamLocation,
    ParamType,
)

# Financial Statements Endpoints
INCOME_STATEMENT = Endpoint(
    name="income_statement",
    path="income-statement/{symbol}",
    version=APIVersion.V3,
    description="Get income statements",
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
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period (annual/quarter)",
            default="annual",
            valid_values=["annual", "quarter"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of results",
            default=40,
        ),
    ],
    response_model=IncomeStatement,
)

BALANCE_SHEET = Endpoint(
    name="balance_sheet",
    path="balance-sheet-statement/{symbol}",
    version=APIVersion.V3,
    description="Get balance sheets",
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
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period (annual/quarter)",
            default="annual",
            valid_values=["annual", "quarter"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of results",
            default=40,
        ),
    ],
    response_model=BalanceSheet,
)

CASH_FLOW = Endpoint(
    name="cash_flow",
    path="cash-flow-statement/{symbol}",
    version=APIVersion.V3,
    description="Get cash flow statements",
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
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period (annual/quarter)",
            default="annual",
            valid_values=["annual", "quarter"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of results",
            default=40,
        ),
    ],
    response_model=CashFlowStatement,
)

# Financial Analysis Endpoints
KEY_METRICS = Endpoint(
    name="key_metrics",
    path="key-metrics/{symbol}",
    version=APIVersion.V3,
    description="Get key financial metrics",
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
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period (annual/quarter)",
            default="annual",
            valid_values=["annual", "quarter"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of results",
            default=40,
        ),
    ],
    response_model=KeyMetrics,
)

FINANCIAL_RATIOS = Endpoint(
    name="financial_ratios",
    path="ratios/{symbol}",
    version=APIVersion.V3,
    description="Get financial ratios",
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
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period (annual/quarter)",
            default="annual",
            valid_values=["annual", "quarter"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of results",
            default=40,
        ),
    ],
    response_model=FinancialRatios,
)
FULL_FINANCIAL_STATEMENT = Endpoint(
    name="full_financial_statement",
    path="financial-statement-full-as-reported/{symbol}",
    version=APIVersion.V3,
    description="Get full financial statements as reported",
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
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period (annual/quarter)",
            default="annual",
            valid_values=["annual", "quarter"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of results",
            default=40,
        ),
    ],
    response_model=FinancialStatementFull,
)

FINANCIAL_REPORTS_DATES = Endpoint(
    name="financial_reports_dates",
    path="financial-reports-dates",
    version=APIVersion.V4,
    description="Get list of financial report dates",
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
    response_model=FinancialReportDate,
)

OWNER_EARNINGS = Endpoint(
    name="owner_earnings",
    path="owner_earnings",
    version=APIVersion.V4,
    description="Get owner earnings data",
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
    response_model=OwnerEarnings,
)

LEVERED_DCF = Endpoint(
    name="levered_dcf",
    path="advanced_levered_discounted_cash_flow",
    version=APIVersion.V4,
    description="Get levered DCF valuation",
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
    response_model=LeveredDCF,
)

HISTORICAL_RATING = Endpoint(
    name="historical_rating",
    path="historical-rating/{symbol}",
    version=APIVersion.V3,
    description="Get historical company ratings",
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
    response_model=HistoricalRating,
)
