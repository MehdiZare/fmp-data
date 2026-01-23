# fmp_data/sec/mapping.py
from __future__ import annotations

from fmp_data.lc.hints import SYMBOL_HINT
from fmp_data.lc.models import EndpointSemantics, SemanticCategory
from fmp_data.sec.endpoints import (
    ALL_INDUSTRY_CLASSIFICATION,
    INDUSTRY_CLASSIFICATION_SEARCH,
    SEC_COMPANY_SEARCH_CIK,
    SEC_COMPANY_SEARCH_NAME,
    SEC_COMPANY_SEARCH_SYMBOL,
    SEC_FILINGS_8K,
    SEC_FILINGS_FINANCIALS,
    SEC_FILINGS_SEARCH_CIK,
    SEC_FILINGS_SEARCH_FORM_TYPE,
    SEC_FILINGS_SEARCH_SYMBOL,
    SEC_PROFILE,
    SIC_LIST,
)

# SEC endpoints mapping
SEC_ENDPOINT_MAP = {
    "get_latest_8k": SEC_FILINGS_8K,
    "get_latest_financials": SEC_FILINGS_FINANCIALS,
    "search_by_form_type": SEC_FILINGS_SEARCH_FORM_TYPE,
    "search_by_symbol": SEC_FILINGS_SEARCH_SYMBOL,
    "search_by_cik": SEC_FILINGS_SEARCH_CIK,
    "search_company_by_name": SEC_COMPANY_SEARCH_NAME,
    "search_company_by_symbol": SEC_COMPANY_SEARCH_SYMBOL,
    "search_company_by_cik": SEC_COMPANY_SEARCH_CIK,
    "get_profile": SEC_PROFILE,
    "get_sic_codes": SIC_LIST,
    "search_industry_classification": INDUSTRY_CLASSIFICATION_SEARCH,
    "get_all_industry_classification": ALL_INDUSTRY_CLASSIFICATION,
}

# Complete semantic definitions for all endpoints
SEC_ENDPOINTS_SEMANTICS = {
    "filings_8k": EndpointSemantics(
        client_name="sec",
        method_name="get_latest_8k",
        natural_description=(
            "Get the latest SEC 8-K filings (material events). "
            "Returns recent 8-K filings which companies file to announce major events."
        ),
        example_queries=[
            "Get latest 8-K filings",
            "Show me recent SEC 8-K reports",
            "Material event filings",
            "Latest corporate event disclosures",
            "Recent 8-K announcements",
        ],
        related_terms=[
            "8-K filing",
            "material events",
            "corporate events",
            "SEC filing",
            "event disclosure",
            "current report",
        ],
        category=SemanticCategory.INTELLIGENCE,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "filings_financials": EndpointSemantics(
        client_name="sec",
        method_name="get_latest_financials",
        natural_description=(
            "Get the latest SEC financial filings (10-K, 10-Q). "
            "Returns recent financial filings (annual and quarterly reports)."
        ),
        example_queries=[
            "Get latest 10-K filings",
            "Show me recent 10-Q reports",
            "Latest SEC financial filings",
            "Recent quarterly filings",
            "Annual report filings",
        ],
        related_terms=[
            "10-K filing",
            "10-Q filing",
            "financial statements",
            "annual report",
            "quarterly report",
            "SEC filing",
        ],
        category=SemanticCategory.INTELLIGENCE,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "filings_search_form": EndpointSemantics(
        client_name="sec",
        method_name="search_by_form_type",
        natural_description=(
            "Search SEC filings by form type (e.g., 10-K, 10-Q, 8-K, S-1). "
            "Returns filings matching the specified SEC form type."
        ),
        example_queries=[
            "Search for 10-K filings",
            "Find all 8-K filings",
            "Get S-1 registration statements",
            "Search SEC filings by form type",
            "Filter filings by form",
        ],
        related_terms=[
            "SEC form",
            "filing type",
            "form search",
            "10-K",
            "10-Q",
            "8-K",
            "S-1",
        ],
        category=SemanticCategory.INTELLIGENCE,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "filings_search_symbol": EndpointSemantics(
        client_name="sec",
        method_name="search_by_symbol",
        natural_description=(
            "Search SEC filings by stock symbol. "
            "Returns all SEC filings for a specific company identified by stock ticker."
        ),
        example_queries=[
            "Get Apple SEC filings",
            "Search TSLA SEC filings",
            "Find all AAPL SEC reports",
            "Show me Microsoft SEC filings",
            "Company SEC filing history",
        ],
        related_terms=[
            "company filings",
            "SEC reports",
            "filing history",
            "company SEC data",
            "ticker filings",
        ],
        category=SemanticCategory.INTELLIGENCE,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "filings_search_cik": EndpointSemantics(
        client_name="sec",
        method_name="search_by_cik",
        natural_description=(
            "Search SEC filings by CIK number (Central Index Key). "
            "Returns all SEC filings for a company identified by CIK."
        ),
        example_queries=[
            "Get SEC filings by CIK",
            "Search filings for CIK 0000320193",
            "Find company filings using CIK number",
            "CIK filing search",
            "Central Index Key filings",
        ],
        related_terms=[
            "CIK",
            "Central Index Key",
            "company identifier",
            "SEC identifier",
            "filing lookup",
        ],
        category=SemanticCategory.INTELLIGENCE,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "company_search_name": EndpointSemantics(
        client_name="sec",
        method_name="search_company_by_name",
        natural_description=(
            "Search SEC-registered companies by name. "
            "Returns companies matching the search term in their registered name."
        ),
        example_queries=[
            "Search for Apple in SEC database",
            "Find companies named Tesla",
            "Search SEC companies by name",
            "Lookup company in SEC registry",
            "Find company SEC registration",
        ],
        related_terms=[
            "company search",
            "SEC registry",
            "company lookup",
            "registered companies",
            "company name search",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "company_search_symbol": EndpointSemantics(
        client_name="sec",
        method_name="search_company_by_symbol",
        natural_description=(
            "Search SEC-registered companies by stock symbol. "
            "Returns SEC registration information for a specific ticker symbol."
        ),
        example_queries=[
            "Get SEC info for AAPL",
            "Find company by ticker symbol",
            "Search SEC database by symbol",
            "Lookup TSLA SEC registration",
            "Company SEC data by ticker",
        ],
        related_terms=[
            "ticker lookup",
            "symbol search",
            "SEC registration",
            "company info",
            "ticker SEC data",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={},
        use_cases=["Financial analysis", "Investment research"],
    ),
    "company_search_cik": EndpointSemantics(
        client_name="sec",
        method_name="search_company_by_cik",
        natural_description=(
            "Search SEC-registered companies by CIK number. "
            "Returns company SEC registration information by Central Index Key."
        ),
        example_queries=[
            "Find company by CIK number",
            "Search SEC company database using CIK",
            "Lookup company with CIK 0000320193",
            "Get company info by Central Index Key",
            "CIK company search",
        ],
        related_terms=[
            "CIK",
            "Central Index Key",
            "company lookup",
            "SEC registry",
            "company identifier",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "sec_profile": EndpointSemantics(
        client_name="sec",
        method_name="get_profile",
        natural_description=(
            "Get SEC profile with CIK, SIC codes, and registration details."
        ),
        example_queries=[
            "Get Apple SEC profile",
            "Show me TSLA SEC registration data",
            "Company SEC profile and CIK",
            "SEC registration details",
            "Company SIC code and SEC info",
        ],
        related_terms=[
            "SEC profile",
            "company registration",
            "CIK number",
            "SIC code",
            "SEC data",
            "registration info",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={},
        use_cases=["Financial analysis", "Investment research"],
    ),
    "sic_codes": EndpointSemantics(
        client_name="sec",
        method_name="get_sic_codes",
        natural_description=(
            "Get list of all Standard Industrial Classification (SIC) codes. "
            "Returns complete SIC code directory used by the SEC."
        ),
        example_queries=[
            "Get all SIC codes",
            "List Standard Industrial Classification codes",
            "Show me SEC industry codes",
            "SIC code directory",
            "Industry classification codes",
        ],
        related_terms=[
            "SIC",
            "Standard Industrial Classification",
            "industry codes",
            "classification system",
            "industry taxonomy",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={},
        response_hints={},
        use_cases=["Financial analysis", "Investment research"],
    ),
    "industry_classification_search": EndpointSemantics(
        client_name="sec",
        method_name="search_industry_classification",
        natural_description=(
            "Search industry classification data by symbol, CIK, or SIC code. "
            "Returns industry classification information for companies."
        ),
        example_queries=[
            "Get industry classification for AAPL",
            "Search industry by SIC code",
            "Find company industry classification",
            "Lookup SIC data by CIK",
            "Company industry category",
        ],
        related_terms=[
            "industry classification",
            "SIC lookup",
            "industry category",
            "company industry",
            "classification search",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "all_industry_classification": EndpointSemantics(
        client_name="sec",
        method_name="get_all_industry_classification",
        natural_description=(
            "Get all industry classification records. "
            "Returns industry classifications for all registered companies."
        ),
        example_queries=[
            "Get all industry classifications",
            "List all company industry categories",
            "Show me complete industry classification data",
            "All SIC code assignments",
            "Industry classification directory",
        ],
        related_terms=[
            "industry directory",
            "classification list",
            "all industries",
            "SIC assignments",
            "industry data",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
}
