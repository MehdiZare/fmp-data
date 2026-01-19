# fmp_data/sec/client.py
from typing import cast

from pydantic import ValidationError as PydanticValidationError

from fmp_data.base import EndpointGroup
from fmp_data.sec.endpoints import (
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
from fmp_data.sec.models import (
    SECCompanySearchResult,
    SECFiling8K,
    SECFilingSearchResult,
    SECFinancialFiling,
    SECProfile,
    SICCode,
)


class SECClient(EndpointGroup):
    """Client for SEC filing and company data endpoints

    Provides methods to retrieve SEC filings, company profiles, and related data.
    """

    def get_latest_8k(
        self, page: int = 0, limit: int = 100
    ) -> list[SECFiling8K]:
        """Get the latest SEC 8-K filings

        Args:
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)

        Returns:
            List of recent 8-K filings
        """
        return self.client.request(SEC_FILINGS_8K, page=page, limit=limit)

    def get_latest_financials(
        self, page: int = 0, limit: int = 100
    ) -> list[SECFinancialFiling]:
        """Get the latest SEC financial filings (10-K, 10-Q)

        Args:
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)

        Returns:
            List of recent financial filings
        """
        return self.client.request(SEC_FILINGS_FINANCIALS, page=page, limit=limit)

    def search_by_form_type(
        self,
        form_type: str,
        page: int = 0,
        limit: int = 100,
    ) -> list[SECFilingSearchResult]:
        """Search SEC filings by form type

        Args:
            form_type: SEC form type (e.g., 10-K, 10-Q, 8-K)
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)

        Returns:
            List of matching filings
        """
        return self.client.request(
            SEC_FILINGS_SEARCH_FORM_TYPE, formType=form_type, page=page, limit=limit
        )

    def search_by_symbol(
        self,
        symbol: str,
        page: int = 0,
        limit: int = 100,
    ) -> list[SECFilingSearchResult]:
        """Search SEC filings by stock symbol

        Args:
            symbol: Stock symbol
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)

        Returns:
            List of matching filings
        """
        return self.client.request(
            SEC_FILINGS_SEARCH_SYMBOL, symbol=symbol, page=page, limit=limit
        )

    def search_by_cik(
        self,
        cik: str,
        page: int = 0,
        limit: int = 100,
    ) -> list[SECFilingSearchResult]:
        """Search SEC filings by CIK number

        Args:
            cik: SEC CIK number
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)

        Returns:
            List of matching filings
        """
        return self.client.request(
            SEC_FILINGS_SEARCH_CIK, cik=cik, page=page, limit=limit
        )

    def search_company_by_name(
        self,
        name: str,
        page: int = 0,
        limit: int = 100,
    ) -> list[SECCompanySearchResult]:
        """Search SEC companies by name

        Args:
            name: Company name or partial name
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)

        Returns:
            List of matching companies
        """
        return self.client.request(
            SEC_COMPANY_SEARCH_NAME, name=name, page=page, limit=limit
        )

    def search_company_by_symbol(self, symbol: str) -> list[SECCompanySearchResult]:
        """Search SEC companies by stock symbol

        Args:
            symbol: Stock symbol

        Returns:
            List of matching companies
        """
        return self.client.request(SEC_COMPANY_SEARCH_SYMBOL, symbol=symbol)

    def search_company_by_cik(self, cik: str) -> list[SECCompanySearchResult]:
        """Search SEC companies by CIK number

        Args:
            cik: SEC CIK number

        Returns:
            List of matching companies
        """
        return self.client.request(SEC_COMPANY_SEARCH_CIK, cik=cik)

    def get_profile(self, symbol: str) -> SECProfile | None:
        """Get SEC profile for a company

        Args:
            symbol: Stock symbol

        Returns:
            SEC profile for the company, or None if not found
        """
        try:
            result = self.client.request(SEC_PROFILE, symbol=symbol)
        except PydanticValidationError as exc:
            self.client.logger.warning(
                "SEC profile response failed validation; returning None.",
                extra={"symbol": symbol, "error": str(exc)},
            )
            return None
        if isinstance(result, list):
            if not result:
                return None
            return cast(SECProfile, result[0])
        return cast(SECProfile, result)

    def get_sic_codes(self) -> list[SICCode]:
        """Get list of all Standard Industrial Classification (SIC) codes

        Returns:
            List of SIC codes
        """
        return self.client.request(SIC_LIST)
