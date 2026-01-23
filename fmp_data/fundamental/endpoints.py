# fmp_data/fundamental/endpoints.py
from fmp_data.fundamental.models import (
    DCF,
    BalanceSheet,
    CashFlowStatement,
    CustomDCF,
    CustomLeveredDCF,
    FinancialRatios,
    FinancialReportDate,
    FinancialStatementFull,
    HistoricalRating,
    IncomeStatement,
    KeyMetrics,
    LatestFinancialStatement,
    LeveredDCF,
    OwnerEarnings,
)
from fmp_data.fundamental.schema import (
    BalanceSheetArgs,
    CashFlowArgs,
    FinancialRatiosArgs,
    IncomeStatementArgs,
    KeyMetricsArgs,
    LatestFinancialStatementsArgs,
    OwnerEarningsArgs,
    SimpleSymbolArgs,
)
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    ParamLocation,
    ParamType,
)

INCOME_STATEMENT: Endpoint = Endpoint(
    name="income_statement",
    path="income-statement",
    version=APIVersion.STABLE,
    description=(
        "Retrieve detailed income statements showing revenue, costs, expenses and "
        "profitability metrics for a company "
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
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period (annual, quarter)",
            default="annual",
            valid_values=["annual", "quarter", "FY", "Q1", "Q2", "Q3", "Q4"],
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
    arg_model=IncomeStatementArgs,
    example_queries=[
        "Get AAPL income statement",
        "Show quarterly income statements for MSFT",
        "What is Tesla's revenue?",
        "Show me Google's profit margins",
        "Get Amazon's operating expenses",
        "Last 5 years income statements for Netflix",
    ],
)

BALANCE_SHEET: Endpoint = Endpoint(
    name="balance_sheet",
    path="balance-sheet-statement",
    version=APIVersion.STABLE,
    description=(
        "Obtain detailed balance sheet statements showing assets, liabilities and "
        "shareholders' equity for a company at specific points in time"
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
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period (annual, quarter, FY, Q1-Q4)",
            default="annual",
            valid_values=["annual", "quarter", "FY", "Q1", "Q2", "Q3", "Q4"],
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
    arg_model=BalanceSheetArgs,
    example_queries=[
        "Get AAPL balance sheet",
        "Show Microsoft's assets and liabilities",
        "What's Tesla's cash position?",
        "Get Google's debt levels",
        "Show Amazon's equity structure",
    ],
)

CASH_FLOW: Endpoint = Endpoint(
    name="cash_flow",
    path="cash-flow-statement",
    version=APIVersion.STABLE,
    description=(
        "Access cash flow statements showing operating, investing, and financing "
        "activities along with key cash flow metrics and changes in cash position"
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
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period (annual, quarter, FY, Q1-Q4)",
            default="annual",
            valid_values=["annual", "quarter", "FY", "Q1", "Q2", "Q3", "Q4"],
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
    arg_model=CashFlowArgs,
    example_queries=[
        "Get AAPL cash flow statement",
        "Show Microsoft's operating cash flow",
        "What's Tesla's free cash flow?",
        "Get Google's capital expenditures",
        "Show Amazon's financing activities",
    ],
)

LATEST_FINANCIAL_STATEMENTS: Endpoint = Endpoint(
    name="latest_financial_statements",
    path="latest-financial-statements",
    version=APIVersion.STABLE,
    description=(
        "Get the latest financial statement publication metadata across symbols, "
        "including date and reporting period."
    ),
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Page number (max 100)",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Records per page (max 250)",
        ),
    ],
    optional_params=[],
    response_model=LatestFinancialStatement,
    arg_model=LatestFinancialStatementsArgs,
    example_queries=[
        "Get latest financial statements page 0",
        "Show the newest financial statement entries",
        "List latest financial statements with limit 100",
    ],
)

KEY_METRICS: Endpoint = Endpoint(
    name="key_metrics",
    path="key-metrics",
    version=APIVersion.STABLE,
    description=(
        "Access essential financial metrics and KPIs including profitability, "
        "efficiency, and valuation measures for company analysis"
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
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period (annual, quarter, FY, Q1-Q4)",
            default="annual",
            valid_values=["annual", "quarter", "FY", "Q1", "Q2", "Q3", "Q4"],
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
    arg_model=KeyMetricsArgs,
    example_queries=[
        "Show AAPL key metrics",
        "Get Microsoft's financial KPIs",
        "What are Tesla's key ratios?",
        "Show performance metrics for Amazon",
        "Get Google's fundamental metrics",
    ],
)

FINANCIAL_RATIOS: Endpoint = Endpoint(
    name="financial_ratios",
    path="ratios",
    version=APIVersion.STABLE,
    description=(
        "Retrieve comprehensive financial ratios including profitability, "
        "liquidity, solvency, and efficiency metrics for analysis"
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
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period (annual, quarter, FY, Q1-Q4)",
            default="annual",
            valid_values=["annual", "quarter", "FY", "Q1", "Q2", "Q3", "Q4"],
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
    arg_model=FinancialRatiosArgs,
    example_queries=[
        "Get AAPL financial ratios",
        "Show Microsoft's profitability metrics",
        "What's Tesla's debt ratio?",
        "Get Google's efficiency ratios",
        "Show Amazon's liquidity metrics",
    ],
)
FULL_FINANCIAL_STATEMENT: Endpoint = Endpoint(
    name="full_financial_statement",
    path="financial-statement-full-as-reported",
    version=APIVersion.STABLE,
    description="Get full financial statements as reported",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
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
            description="Period (annual, quarter, FY, Q1-Q4)",
            default="annual",
            valid_values=["annual", "quarter", "FY", "Q1", "Q2", "Q3", "Q4"],
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

FINANCIAL_REPORTS_DATES: Endpoint = Endpoint(
    name="financial_reports_dates",
    path="financial-reports-dates",
    version=APIVersion.STABLE,
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

OWNER_EARNINGS: Endpoint = Endpoint(
    name="owner_earnings",
    path="owner-earnings",
    version=APIVersion.STABLE,
    description=(
        "Calculate owner earnings metrics using Warren Buffett's methodology "
        "for evaluating true business profitability"
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
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of results",
        ),
    ],
    response_model=OwnerEarnings,
    arg_model=OwnerEarningsArgs,
    example_queries=[
        "Calculate AAPL owner earnings",
        "Get Microsoft's owner earnings",
        "What's Tesla's true earnings power?",
        "Show Google's owner earnings metrics",
    ],
)

LEVERED_DCF: Endpoint = Endpoint(
    name="levered_dcf",
    path="levered-discounted-cash-flow",
    version=APIVersion.STABLE,
    description=(
        "Perform levered discounted cash flow valuation including detailed "
        "assumptions and growth projections"
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
    response_model=LeveredDCF,
    arg_model=SimpleSymbolArgs,
    example_queries=[
        "Calculate AAPL DCF value",
        "Get Microsoft's intrinsic value",
        "What's Tesla worth using DCF?",
        "Show Google's DCF valuation",
        "Get Amazon's fair value estimate",
    ],
)

HISTORICAL_RATING: Endpoint = Endpoint(
    name="historical_rating",
    path="historical-rating",
    version=APIVersion.STABLE,
    description=(
        "Retrieve historical company ratings and scoring metrics over time "
        "based on fundamental analysis"
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
    response_model=HistoricalRating,
    arg_model=SimpleSymbolArgs,
    example_queries=[
        "Get AAPL historical ratings",
        "Show Microsoft's rating history",
        "What are Tesla's past ratings?",
        "Get Google's historical scores",
        "Show Amazon's rating changes",
    ],
)

DISCOUNTED_CASH_FLOW: Endpoint = Endpoint(
    name="discounted_cash_flow",
    path="discounted-cash-flow",
    version=APIVersion.STABLE,
    description=(
        "Calculate discounted cash flow valuation to determine the intrinsic "
        "value of a company based on projected future cash flows"
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
    response_model=DCF,
    arg_model=SimpleSymbolArgs,
    example_queries=[
        "Calculate AAPL DCF valuation",
        "Get Microsoft's intrinsic value",
        "What's Tesla worth using DCF?",
        "Show Google's DCF analysis",
        "Get Amazon's fair value estimate",
    ],
)

CUSTOM_DISCOUNTED_CASH_FLOW: Endpoint = Endpoint(
    name="custom_discounted_cash_flow",
    path="custom-discounted-cash-flow",
    version=APIVersion.STABLE,
    description=(
        "Perform advanced DCF analysis with detailed cash flow projections, "
        "growth rates, WACC calculations, and terminal value assumptions"
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
    response_model=CustomDCF,
    arg_model=SimpleSymbolArgs,
    example_queries=[
        "Get detailed DCF for AAPL",
        "Show Microsoft's cash flow projections",
        "Calculate Tesla's terminal value",
        "What's Google's WACC and DCF?",
        "Get Amazon's 10-year cash flow forecast",
    ],
)

CUSTOM_LEVERED_DCF: Endpoint = Endpoint(
    name="custom_levered_dcf",
    path="custom-levered-discounted-cash-flow",
    version=APIVersion.STABLE,
    description=(
        "Calculate levered DCF valuation using free cash flow to equity (FCFE) "
        "with detailed projections and cost of equity calculations"
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
    response_model=CustomLeveredDCF,
    arg_model=SimpleSymbolArgs,
    example_queries=[
        "Calculate levered DCF for AAPL",
        "Get Microsoft's FCFE projections",
        "What's Tesla's cost of equity?",
        "Show Google's levered valuation",
        "Get Amazon's equity value analysis",
    ],
)
