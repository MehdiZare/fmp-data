# fmp_data/sec/client.py
from datetime import date, timedelta

from pydantic import ValidationError as PydanticValidationError
from pydantic_core import ValidationError as PydanticCoreValidationError

from fmp_data.base import EndpointGroup
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
from fmp_data.sec.models import (
    IndustryClassification,
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
        self,
        page: int = 0,
        limit: int = 100,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[SECFiling8K]:
        """Get the latest SEC 8-K filings

        Args:
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)
            from_date: Start date (default: 30 days ago)
            to_date: End date (default: today)

        Returns:
            List of recent 8-K filings
        """
        end_date = to_date or date.today()
        start_date = from_date or (end_date - timedelta(days=30))
        return self.client.request(
            SEC_FILINGS_8K,
            page=page,
            limit=limit,
            **{
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
            },
        )

    def get_latest_financials(
        self,
        page: int = 0,
        limit: int = 100,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[SECFinancialFiling]:
        """Get the latest SEC financial filings (10-K, 10-Q)

        Args:
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)
            from_date: Start date (default: 30 days ago)
            to_date: End date (default: today)

        Returns:
            List of recent financial filings
        """
        end_date = to_date or date.today()
        start_date = from_date or (end_date - timedelta(days=30))
        return self.client.request(
            SEC_FILINGS_FINANCIALS,
            page=page,
            limit=limit,
            **{
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
            },
        )

    def search_by_form_type(
        self,
        form_type: str,
        page: int = 0,
        limit: int = 100,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[SECFilingSearchResult]:
        """Search SEC filings by form type

        Args:
            form_type: SEC form type (e.g., 10-K, 10-Q, 8-K)
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)

        Returns:
            List of matching filings
        """
        end_date = to_date or date.today()
        start_date = from_date or (end_date - timedelta(days=30))
        return self.client.request(
            SEC_FILINGS_SEARCH_FORM_TYPE,
            formType=form_type,
            page=page,
            limit=limit,
            **{
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
            },
        )

    def search_by_symbol(
        self,
        symbol: str,
        page: int = 0,
        limit: int = 100,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[SECFilingSearchResult]:
        """Search SEC filings by stock symbol

        Args:
            symbol: Stock symbol
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)

        Returns:
            List of matching filings
        """
        end_date = to_date or date.today()
        start_date = from_date or (end_date - timedelta(days=30))
        return self.client.request(
            SEC_FILINGS_SEARCH_SYMBOL,
            symbol=symbol,
            page=page,
            limit=limit,
            **{
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
            },
        )

    def search_by_cik(
        self,
        cik: str,
        page: int = 0,
        limit: int = 100,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[SECFilingSearchResult]:
        """Search SEC filings by CIK number

        Args:
            cik: SEC CIK number
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)

        Returns:
            List of matching filings
        """
        end_date = to_date or date.today()
        start_date = from_date or (end_date - timedelta(days=30))
        return self.client.request(
            SEC_FILINGS_SEARCH_CIK,
            cik=cik,
            page=page,
            limit=limit,
            **{
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
            },
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
            SEC_COMPANY_SEARCH_NAME, company=name, page=page, limit=limit
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
        except (PydanticValidationError, PydanticCoreValidationError) as exc:
            self.client.logger.warning(
                "SEC profile response failed validation; returning None.",
                extra={"symbol": symbol, "error": str(exc)},
            )
            return None
        return self._unwrap_single(result, SECProfile, allow_none=True)

    def get_sic_codes(self) -> list[SICCode]:
        """Get list of all Standard Industrial Classification (SIC) codes

        Returns:
            List of SIC codes
        """
        return self.client.request(SIC_LIST)

    def search_industry_classification(
        self,
        symbol: str | None = None,
        cik: str | None = None,
        sic_code: str | None = None,
    ) -> list[IndustryClassification]:
        """Search industry classification data

        Args:
            symbol: Stock symbol
            cik: SEC CIK number
            sic_code: SIC code

        Returns:
            List of matching industry classification records
        """
        if not symbol and not cik and not sic_code:
            raise ValueError("Provide at least one of symbol, cik, or sic_code")
        params: dict[str, str] = {}
        if symbol:
            params["symbol"] = symbol
        if cik:
            params["cik"] = cik
        if sic_code:
            params["sicCode"] = sic_code
        return self.client.request(INDUSTRY_CLASSIFICATION_SEARCH, **params)

    def get_all_industry_classification(
        self, page: int = 0, limit: int = 100
    ) -> list[IndustryClassification]:
        """Get all industry classification records

        Args:
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)

        Returns:
            List of industry classification records
        """
        return self.client.request(ALL_INDUSTRY_CLASSIFICATION, page=page, limit=limit)
