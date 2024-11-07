# company/client.py

from ..base import EndpointGroup
from .endpoints import (
    AVAILABLE_INDEXES,
    CIK_SEARCH,
    COMPANY_LOGO,
    COMPANY_NOTES,
    CORE_INFORMATION,
    CUSIP_SEARCH,
    EMPLOYEE_COUNT,
    ETF_LIST,
    EXCHANGE_SYMBOLS,
    ISIN_SEARCH,
    KEY_EXECUTIVES,
    PROFILE,
    SEARCH,
    STOCK_LIST,
)
from .models import (
    CIKResult,
    CompanyCoreInformation,
    CompanyExecutive,
    CompanyNote,
    CompanyProfile,
    CompanySearchResult,
    CompanySymbol,
    CUSIPResult,
    EmployeeCount,
    ExchangeSymbol,
    ISINResult,
)


class CompanyClient(EndpointGroup):
    """Client for company-related API endpoints"""

    def get_profile(self, symbol: str) -> CompanyProfile:
        """Get company profile information"""
        result = self.client.request(PROFILE, symbol=symbol)
        # Handle the case where API returns a list with single item
        return result[0] if isinstance(result, list) else result

    def get_core_information(self, symbol: str) -> CompanyCoreInformation:
        """Get core company information"""
        return self.client.request(CORE_INFORMATION, symbol=symbol)

    def search(
        self, query: str, limit: int | None = None, exchange: str | None = None
    ) -> list[CompanySearchResult]:
        """Search for companies"""
        params = {"query": query}
        if limit is not None:
            params["limit"] = limit
        if exchange is not None:
            params["exchange"] = exchange
        return self.client.request(SEARCH, **params)

    def get_executives(self, symbol: str) -> list[CompanyExecutive]:
        """Get company executives information"""
        return self.client.request(KEY_EXECUTIVES, symbol=symbol)

    def get_employee_count(self, symbol: str) -> list[EmployeeCount]:
        """Get company employee count history"""
        return self.client.request(EMPLOYEE_COUNT, symbol=symbol)

    def get_company_notes(self, symbol: str) -> list[CompanyNote]:
        """Get company financial notes"""
        return self.client.request(COMPANY_NOTES, symbol=symbol)

    def get_company_logo_url(self, symbol: str) -> str:
        """Get company logo URL"""
        return self.client.request(COMPANY_LOGO, symbol=symbol)

    def get_stock_list(self) -> list[CompanySymbol]:
        """Get list of all available stocks"""
        return self.client.request(STOCK_LIST)

    def get_etf_list(self) -> list[CompanySymbol]:
        """Get list of all available ETFs"""
        return self.client.request(ETF_LIST)

    def get_available_indexes(self) -> list[str]:
        """Get list of all available indexes"""
        return self.client.request(AVAILABLE_INDEXES)

    def get_exchange_symbols(self, exchange: str) -> list[ExchangeSymbol]:
        """Get all symbols for a specific exchange"""
        return self.client.request(EXCHANGE_SYMBOLS, exchange=exchange)

    def search_by_cik(self, query: str) -> list[CIKResult]:
        """Search companies by CIK number"""
        return self.client.request(CIK_SEARCH, query=query)

    def search_by_cusip(self, query: str) -> list[CUSIPResult]:
        """Search companies by CUSIP"""
        return self.client.request(CUSIP_SEARCH, query=query)

    def search_by_isin(self, query: str) -> list[ISINResult]:
        """Search companies by ISIN"""
        return self.client.request(ISIN_SEARCH, query=query)