# fmp_data/sec/async_client.py
"""Async client for SEC filing and company data endpoints."""
from datetime import date, timedelta
from typing import cast

from pydantic import ValidationError as PydanticValidationError
from pydantic_core import ValidationError as PydanticCoreValidationError

from fmp_data.base import AsyncEndpointGroup
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


class AsyncSECClient(AsyncEndpointGroup):
    """Async client for SEC filing and company data endpoints.

    Provides async methods to retrieve SEC filings, company profiles, and related data.
    """

    async def get_latest_8k(
        self, page: int = 0, limit: int = 100
    ) -> list[SECFiling8K]:
        """Get the latest SEC 8-K filings

        Args:
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)

        Returns:
            List of recent 8-K filings
        """
        return await self.client.request_async(SEC_FILINGS_8K, page=page, limit=limit)

    async def get_latest_financials(
        self, page: int = 0, limit: int = 100
    ) -> list[SECFinancialFiling]:
        """Get the latest SEC financial filings (10-K, 10-Q)

        Args:
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)

        Returns:
            List of recent financial filings
        """
        return await self.client.request_async(
            SEC_FILINGS_FINANCIALS, page=page, limit=limit
        )

    async def search_by_form_type(
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
        return await self.client.request_async(
            SEC_FILINGS_SEARCH_FORM_TYPE,
            formType=form_type,
            page=page,
            limit=limit,
            **{
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
            },
        )

    async def search_by_symbol(
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
        return await self.client.request_async(
            SEC_FILINGS_SEARCH_SYMBOL,
            symbol=symbol,
            page=page,
            limit=limit,
            **{
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
            },
        )

    async def search_by_cik(
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
        return await self.client.request_async(
            SEC_FILINGS_SEARCH_CIK,
            cik=cik,
            page=page,
            limit=limit,
            **{
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
            },
        )

    async def search_company_by_name(
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
        return await self.client.request_async(
            SEC_COMPANY_SEARCH_NAME, company=name, page=page, limit=limit
        )

    async def search_company_by_symbol(
        self, symbol: str
    ) -> list[SECCompanySearchResult]:
        """Search SEC companies by stock symbol

        Args:
            symbol: Stock symbol

        Returns:
            List of matching companies
        """
        return await self.client.request_async(SEC_COMPANY_SEARCH_SYMBOL, symbol=symbol)

    async def search_company_by_cik(self, cik: str) -> list[SECCompanySearchResult]:
        """Search SEC companies by CIK number

        Args:
            cik: SEC CIK number

        Returns:
            List of matching companies
        """
        return await self.client.request_async(SEC_COMPANY_SEARCH_CIK, cik=cik)

    async def get_profile(self, symbol: str) -> SECProfile | None:
        """Get SEC profile for a company

        Args:
            symbol: Stock symbol

        Returns:
            SEC profile for the company, or None if not found
        """
        try:
            result = await self.client.request_async(SEC_PROFILE, symbol=symbol)
        except (PydanticValidationError, PydanticCoreValidationError) as exc:
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

    async def get_sic_codes(self) -> list[SICCode]:
        """Get list of all Standard Industrial Classification (SIC) codes

        Returns:
            List of SIC codes
        """
        return await self.client.request_async(SIC_LIST)
