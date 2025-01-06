# /fmp_data/lc/mapping.py
from fmp_data.alternative.mapping import (
    ALTERNATIVE_ENDPOINT_MAP,
    ALTERNATIVE_ENDPOINTS_SEMANTICS,
)
from fmp_data.company.mapping import COMPANY_ENDPOINT_MAP, COMPANY_ENDPOINTS_SEMANTICS
from fmp_data.economics.mapping import (
    ECONOMICS_ENDPOINT_MAP,
    ECONOMICS_ENDPOINTS_SEMANTICS,
)
from fmp_data.fundamental.mapping import (
    FUNDAMENTAL_ENDPOINT_MAP,
    FUNDAMENTAL_ENDPOINTS_SEMANTICS,
)
from fmp_data.institutional.mapping import (
    INSTITUTIONAL_ENDPOINT_MAP,
    INSTITUTIONAL_ENDPOINTS_SEMANTICS,
)
from fmp_data.intelligence.mapping import (
    INTELLIGENCE_ENDPOINT_MAP,
    INTELLIGENCE_ENDPOINTS_SEMANTICS,
)
from fmp_data.investment.mapping import (
    INVESTMENT_ENDPOINT_MAP,
    INVESTMENT_ENDPOINTS_SEMANTICS,
)
from fmp_data.market.mapping import MARKET_ENDPOINT_MAP, MARKET_ENDPOINTS_SEMANTICS
from fmp_data.technical.mapping import (
    TECHNICAL_ENDPOINT_MAP,
    TECHNICAL_ENDPOINTS_SEMANTICS,
)

ALL_ENDPOINT_SEMANTICS = {
    **ALTERNATIVE_ENDPOINTS_SEMANTICS,
    **COMPANY_ENDPOINTS_SEMANTICS,
    **ECONOMICS_ENDPOINTS_SEMANTICS,
    **FUNDAMENTAL_ENDPOINTS_SEMANTICS,
    **INSTITUTIONAL_ENDPOINTS_SEMANTICS,
    **INVESTMENT_ENDPOINTS_SEMANTICS,
    **MARKET_ENDPOINTS_SEMANTICS,
    **TECHNICAL_ENDPOINTS_SEMANTICS,
}

ALL_ENDPOINT_MAP = {
    **ALTERNATIVE_ENDPOINT_MAP,
    **COMPANY_ENDPOINT_MAP,
    **ECONOMICS_ENDPOINT_MAP,
    **FUNDAMENTAL_ENDPOINT_MAP,
    **INSTITUTIONAL_ENDPOINT_MAP,
    **INVESTMENT_ENDPOINT_MAP,
    **MARKET_ENDPOINTS_SEMANTICS,
    **TECHNICAL_ENDPOINT_MAP,
}

ENDPOINT_GROUPS = {
    "alternative": {
        "endpoint_map": ALTERNATIVE_ENDPOINT_MAP,
        "semantics_map": ALTERNATIVE_ENDPOINTS_SEMANTICS,
        "display_name": "alternative market",
    },
    "company": {
        "endpoint_map": COMPANY_ENDPOINT_MAP,
        "semantics_map": COMPANY_ENDPOINTS_SEMANTICS,
        "display_name": "company information",
    },
    "economics": {
        "endpoint_map": ECONOMICS_ENDPOINT_MAP,
        "semantics_map": ECONOMICS_ENDPOINTS_SEMANTICS,
        "display_name": "economics data",
    },
    "fundamental": {
        "endpoint_map": FUNDAMENTAL_ENDPOINT_MAP,
        "semantics_map": FUNDAMENTAL_ENDPOINTS_SEMANTICS,
        "display_name": "fundamental analysis",
    },
    "institutional": {
        "endpoint_map": INSTITUTIONAL_ENDPOINT_MAP,
        "semantics_map": INSTITUTIONAL_ENDPOINTS_SEMANTICS,
        "display_name": "institutional data",
    },
    "intelligence": {
        "endpoint_map": INTELLIGENCE_ENDPOINT_MAP,
        "semantics_map": INTELLIGENCE_ENDPOINTS_SEMANTICS,
        "display_name": "market intelligence",
    },
    "investment": {
        "endpoint_map": INVESTMENT_ENDPOINT_MAP,
        "semantics_map": INVESTMENT_ENDPOINTS_SEMANTICS,
        "display_name": "investment",
    },
    "market": {
        "endpoint_map": MARKET_ENDPOINT_MAP,
        "semantics_map": MARKET_ENDPOINTS_SEMANTICS,
        "display_name": "market",
    },
    "technical": {
        "endpoint_map": TECHNICAL_ENDPOINT_MAP,
        "semantics_map": TECHNICAL_ENDPOINTS_SEMANTICS,
        "display_name": "technical analysis",
    },
}

__all__ = [
    "ALL_ENDPOINT_MAP",
    "ALL_ENDPOINT_SEMANTICS",
    "ENDPOINT_GROUPS",
]
