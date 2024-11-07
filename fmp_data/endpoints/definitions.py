from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"


class ParameterType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"


class EndpointParameter(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    type: ParameterType
    required: bool = False
    description: str
    default: str | int | float | bool | None = None
    enum_values: list[str] | None = None


class EndpointResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())

    model_name: str
    is_list: bool = False
    description: str


class Endpoint(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    path: str
    version: str = Field(..., pattern="^v[0-9]+$")
    method: HTTPMethod = HTTPMethod.GET
    description: str
    parameters: list[EndpointParameter]
    response: EndpointResponse
    requires_pagination: bool = False
    rate_limit: int | None = None
    category: str
    subcategory: str


class EndpointCategory(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: str
    endpoints: list[Endpoint]


# Define all company-related endpoints
COMPANY_ENDPOINTS = EndpointCategory(
    name="company",
    description="Company information and search functionality",
    endpoints=[
        Endpoint(
            name="profile",
            path="/profile/{symbol}",
            version="v3",
            description="Get company profile information",
            parameters=[
                EndpointParameter(
                    name="symbol",
                    type=ParameterType.STRING,
                    required=True,
                    description="Stock symbol (ticker)",
                )
            ],
            response=EndpointResponse(
                model_name="CompanyProfile",
                is_list=False,
                description="Detailed company profile information",
            ),
            category="company",
            subcategory="profile",
        ),
        Endpoint(
            name="core_information",
            path="/company-core-information",
            version="v4",
            description="Get core company information",
            parameters=[
                EndpointParameter(
                    name="symbol",
                    type=ParameterType.STRING,
                    required=True,
                    description="Stock symbol (ticker)",
                )
            ],
            response=EndpointResponse(
                model_name="CompanyCoreInformation",
                is_list=False,
                description="Core company information",
            ),
            category="company",
            subcategory="core_info",
        ),
        Endpoint(
            name="search",
            path="/search",
            version="v3",
            description="Search for companies",
            parameters=[
                EndpointParameter(
                    name="query",
                    type=ParameterType.STRING,
                    required=True,
                    description="Search query string",
                ),
                EndpointParameter(
                    name="limit",
                    type=ParameterType.INTEGER,
                    required=False,
                    description="Number of results",
                    default=10,
                ),
            ],
            response=EndpointResponse(
                model_name="CompanySearchResult",
                is_list=True,
                description="List of companies matching search criteria",
            ),
            category="company",
            subcategory="search",
        ),
        # Additional endpoints to be added to COMPANY_ENDPOINTS.endpoints:
        Endpoint(
            name="key_executives",
            path="/key-executives/{symbol}",
            version="v3",
            description="Get information about company executives",
            parameters=[
                EndpointParameter(
                    name="symbol",
                    type=ParameterType.STRING,
                    required=True,
                    description="Stock symbol (ticker)",
                )
            ],
            response=EndpointResponse(
                model_name="CompanyExecutive",
                is_list=True,
                description="List of company executives",
            ),
            category="company",
            subcategory="executives",
        ),
        Endpoint(
            name="historical_employee_count",
            path="/historical/employee_count",
            version="v4",
            description="Get historical employee count data",
            parameters=[
                EndpointParameter(
                    name="symbol",
                    type=ParameterType.STRING,
                    required=True,
                    description="Stock symbol (ticker)",
                )
            ],
            response=EndpointResponse(
                model_name="EmployeeCount",
                is_list=True,
                description="Historical employee count data",
            ),
            category="company",
            subcategory="employees",
        ),
        Endpoint(
            name="company_notes",
            path="/company-notes",
            version="v4",
            description="Get company notes",
            parameters=[
                EndpointParameter(
                    name="symbol",
                    type=ParameterType.STRING,
                    required=True,
                    description="Stock symbol (ticker)",
                )
            ],
            response=EndpointResponse(
                model_name="CompanyNote",
                is_list=True,
                description="Company financial notes",
            ),
            category="company",
            subcategory="notes",
        ),
    ],
)

# Define all market data endpoints
MARKET_DATA_ENDPOINTS = EndpointCategory(
    name="market",
    description="Market data including prices and analysis",
    endpoints=[
        Endpoint(
            name="quote",
            path="/quote/{symbol}",
            version="v3",
            description="Get real-time quote",
            parameters=[
                EndpointParameter(
                    name="symbol",
                    type=ParameterType.STRING,
                    required=True,
                    description="Stock symbol (ticker)",
                )
            ],
            response=EndpointResponse(
                model_name="Quote", is_list=False, description="Real-time quote data"
            ),
            category="market",
            subcategory="quotes",
        ),
        Endpoint(
            name="historical_price",
            path="/historical-price-full/{symbol}",
            version="v3",
            description="Get historical daily price data",
            parameters=[
                EndpointParameter(
                    name="symbol",
                    type=ParameterType.STRING,
                    required=True,
                    description="Stock symbol (ticker)",
                ),
                EndpointParameter(
                    name="from",
                    type=ParameterType.DATE,
                    required=False,
                    description="Start date (YYYY-MM-DD)",
                ),
                EndpointParameter(
                    name="to",
                    type=ParameterType.DATE,
                    required=False,
                    description="End date (YYYY-MM-DD)",
                ),
            ],
            response=EndpointResponse(
                model_name="HistoricalPrice",
                is_list=True,
                description="Historical price data",
            ),
            category="market",
            subcategory="historical",
        ),
    ],
)

# Define all fundamental analysis endpoints
FUNDAMENTAL_ENDPOINTS = EndpointCategory(
    name="fundamental",
    description="Fundamental analysis including financial statements",
    endpoints=[
        Endpoint(
            name="income_statement",
            path="/income-statement/{symbol}",
            version="v3",
            description="Get income statements",
            parameters=[
                EndpointParameter(
                    name="symbol",
                    type=ParameterType.STRING,
                    required=True,
                    description="Stock symbol (ticker)",
                ),
                EndpointParameter(
                    name="period",
                    type=ParameterType.STRING,
                    required=False,
                    description="Period (annual or quarter)",
                    default="annual",
                    enum_values=["annual", "quarter"],
                ),
            ],
            response=EndpointResponse(
                model_name="IncomeStatement",
                is_list=True,
                description="Income statement data",
            ),
            category="fundamental",
            subcategory="financial_statements",
        ),
        Endpoint(
            name="balance_sheet",
            path="/balance-sheet-statement/{symbol}",
            version="v3",
            description="Get balance sheets",
            parameters=[
                EndpointParameter(
                    name="symbol",
                    type=ParameterType.STRING,
                    required=True,
                    description="Stock symbol (ticker)",
                ),
                EndpointParameter(
                    name="period",
                    type=ParameterType.STRING,
                    required=False,
                    description="Period (annual or quarter)",
                    default="annual",
                    enum_values=["annual", "quarter"],
                ),
            ],
            response=EndpointResponse(
                model_name="BalanceSheet",
                is_list=True,
                description="Balance sheet data",
            ),
            category="fundamental",
            subcategory="financial_statements",
        ),
    ],
)

# Define all ETF-related endpoints
ETF_ENDPOINTS = EndpointCategory(
    name="etf",
    description="ETF holdings and information",
    endpoints=[
        Endpoint(
            name="holdings",
            path="/etf-holdings",
            version="v4",
            description="Get ETF holdings",
            parameters=[
                EndpointParameter(
                    name="symbol",
                    type=ParameterType.STRING,
                    required=True,
                    description="ETF symbol",
                ),
                EndpointParameter(
                    name="date",
                    type=ParameterType.DATE,
                    required=False,
                    description="Holdings date (YYYY-MM-DD)",
                ),
            ],
            response=EndpointResponse(
                model_name="ETFHolding", is_list=True, description="ETF holdings data"
            ),
            category="etf",
            subcategory="holdings",
        )
    ],
)

# Combine all endpoint categories
ALL_ENDPOINTS = [
    COMPANY_ENDPOINTS,
    MARKET_DATA_ENDPOINTS,
    FUNDAMENTAL_ENDPOINTS,
    ETF_ENDPOINTS,
]

# Main API Configuration
API_CONFIGURATION = {
    "base_url": "https://financialmodelingprep.com/api",
    "categories": ALL_ENDPOINTS,
}
