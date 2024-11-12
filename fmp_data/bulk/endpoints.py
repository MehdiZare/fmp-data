# fmp_data/bulk/endpoints.py
from fmp_data.bulk.models import (
    BulkBalanceSheet,
    BulkCashFlowStatement,
    BulkCompanyProfile,
    BulkEarningSurprise,
    BulkEODPrice,
    BulkFinancialGrowth,
    BulkIncomeStatement,
    BulkKeyMetric,
    BulkQuote,
    BulkRatio,
    BulkStockPeer,
)
from fmp_data.models import APIVersion, Endpoint, EndpointParam, ParamType

BULK_QUOTES = Endpoint(
    name="bulk_quotes",
    path="quote/{symbols}",
    version=APIVersion.V3,
    description="Get multiple company quotes",
    mandatory_params=[
        EndpointParam(
            name="symbols",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Comma-separated stock symbols",
        )
    ],
    optional_params=[],
    response_model=BulkQuote,
)

BATCH_EOD = Endpoint(
    name="batch_eod",
    path="batch-historical-eod",
    version=APIVersion.V4,
    description="Get batch end-of-day prices",
    mandatory_params=[
        EndpointParam(
            name="date",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Trading date",
        )
    ],
    optional_params=[],
    response_model=BulkEODPrice,
)

BULK_INCOME_STATEMENTS = Endpoint(
    name="bulk_income_statements",
    path="income-statement-bulk",
    version=APIVersion.V4,
    description="Get bulk income statements",
    mandatory_params=[
        EndpointParam(
            name="year",
            param_type=ParamType.QUERY,
            required=True,
            type=int,
            description="Filing year",
        ),
        EndpointParam(
            name="period",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Filing period",
            valid_values=["annual", "quarter"],
        ),
    ],
    optional_params=[],
    response_model=BulkIncomeStatement,
)

BULK_BALANCE_SHEETS = Endpoint(
    name="bulk_balance_sheets",
    path="balance-sheet-statement-bulk",
    version=APIVersion.V4,
    description="Get bulk balance sheets",
    mandatory_params=[
        EndpointParam(
            name="year",
            param_type=ParamType.QUERY,
            required=True,
            type=int,
            description="Filing year",
        ),
        EndpointParam(
            name="period",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Filing period",
            valid_values=["annual", "quarter"],
        ),
    ],
    optional_params=[],
    response_model=BulkBalanceSheet,
)

BULK_CASH_FLOWS = Endpoint(
    name="bulk_cash_flows",
    path="cash-flow-statement-bulk",
    version=APIVersion.V4,
    description="Get bulk cash flow statements",
    mandatory_params=[
        EndpointParam(
            name="year",
            param_type=ParamType.QUERY,
            required=True,
            type=int,
            description="Filing year",
        ),
        EndpointParam(
            name="period",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Filing period",
            valid_values=["annual", "quarter"],
        ),
    ],
    optional_params=[],
    response_model=BulkCashFlowStatement,
)

BULK_RATIOS = Endpoint(
    name="bulk_ratios",
    path="ratios-bulk",
    version=APIVersion.V4,
    description="Get bulk financial ratios",
    mandatory_params=[
        EndpointParam(
            name="year",
            param_type=ParamType.QUERY,
            required=True,
            type=int,
            description="Filing year",
        ),
        EndpointParam(
            name="period",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Filing period",
            valid_values=["annual", "quarter"],
        ),
    ],
    optional_params=[],
    response_model=BulkRatio,
)

BULK_KEY_METRICS = Endpoint(
    name="bulk_key_metrics",
    path="key-metrics-bulk",
    version=APIVersion.V4,
    description="Get bulk key metrics",
    mandatory_params=[
        EndpointParam(
            name="year",
            param_type=ParamType.QUERY,
            required=True,
            type=int,
            description="Filing year",
        ),
        EndpointParam(
            name="period",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Filing period",
            valid_values=["annual", "quarter"],
        ),
    ],
    optional_params=[],
    response_model=BulkKeyMetric,
)

BULK_EARNINGS_SURPRISES = Endpoint(
    name="bulk_earnings_surprises",
    path="earnings-surprises-bulk",
    version=APIVersion.V4,
    description="Get bulk earnings surprises",
    mandatory_params=[],
    optional_params=[],
    response_model=BulkEarningSurprise,
)

BULK_COMPANY_PROFILES = Endpoint(
    name="bulk_company_profiles",
    path="profile-bulk",
    version=APIVersion.STABLE,
    description="Get bulk company profiles",
    mandatory_params=[
        EndpointParam(
            name="part",
            param_type=ParamType.QUERY,
            required=True,
            type=int,
            description="Data part number",
        )
    ],
    optional_params=[],
    response_model=BulkCompanyProfile,
)

BULK_STOCK_PEERS = Endpoint(
    name="bulk_stock_peers",
    path="stock_peers_bulk",
    version=APIVersion.V4,
    description="Get bulk stock peers data",
    mandatory_params=[],
    optional_params=[],
    response_model=BulkStockPeer,
)

BULK_FINANCIAL_GROWTH = Endpoint(
    name="bulk_financial_growth",
    path="financial-growth-bulk",
    version=APIVersion.V4,
    description="Get bulk financial growth data",
    mandatory_params=[
        EndpointParam(
            name="year",
            param_type=ParamType.QUERY,
            required=True,
            type=int,
            description="Filing year",
        ),
        EndpointParam(
            name="period",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Filing period",
            valid_values=["annual", "quarter"],
        ),
    ],
    optional_params=[],
    response_model=BulkFinancialGrowth,
)
