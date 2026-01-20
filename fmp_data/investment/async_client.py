# fmp_data/investment/async_client.py
"""Async client for investment products endpoints."""
from datetime import date
import warnings

from fmp_data.base import AsyncEndpointGroup
from fmp_data.investment.endpoints import (
    ETF_COUNTRY_WEIGHTINGS,
    ETF_EXPOSURE,
    ETF_HOLDER,
    ETF_HOLDING_DATES,
    ETF_HOLDINGS,
    ETF_INFO,
    ETF_SECTOR_WEIGHTINGS,
    MUTUAL_FUND_BY_NAME,
    MUTUAL_FUND_DATES,
    MUTUAL_FUND_HOLDER,
    MUTUAL_FUND_HOLDINGS,
)
from fmp_data.investment.models import (
    ETFCountryWeighting,
    ETFExposure,
    ETFHolder,
    ETFHolding,
    ETFInfo,
    ETFSectorWeighting,
    MutualFundHolder,
    MutualFundHolding,
)


class AsyncInvestmentClient(AsyncEndpointGroup):
    """Async client for investment products endpoints."""

    # ETF methods
    async def get_etf_holdings(
        self, symbol: str, holdings_date: date
    ) -> list[ETFHolding]:
        """Get ETF holdings"""
        return await self.client.request_async(
            ETF_HOLDINGS, symbol=symbol, date=holdings_date.strftime("%Y-%m-%d")
        )

    async def get_etf_holding_dates(self, symbol: str) -> list[date]:
        """Get ETF holding dates"""
        return await self.client.request_async(ETF_HOLDING_DATES, symbol=symbol)

    async def get_etf_info(self, symbol: str) -> ETFInfo | None:
        """
        Get ETF information

        Args:
            symbol: ETF symbol

        Returns:
            ETFInfo object if found, or None if no data/error occurs
        """
        try:
            result = await self.client.request_async(ETF_INFO, symbol=symbol)
            if isinstance(result, list):
                return result[0] if result else None
            if isinstance(result, ETFInfo):
                return result
            warnings.warn(
                f"Unexpected result type from ETF_INFO: {type(result)}", stacklevel=2
            )
            return None
        except Exception as e:
            warnings.warn(f"Error in get_etf_info: {e!s}", stacklevel=2)
            return None

    async def get_etf_sector_weightings(
        self, symbol: str
    ) -> list[ETFSectorWeighting]:
        """Get ETF sector weightings"""
        return await self.client.request_async(ETF_SECTOR_WEIGHTINGS, symbol=symbol)

    async def get_etf_country_weightings(
        self, symbol: str
    ) -> list[ETFCountryWeighting]:
        """Get ETF country weightings"""
        return await self.client.request_async(ETF_COUNTRY_WEIGHTINGS, symbol=symbol)

    async def get_etf_exposure(self, symbol: str) -> list[ETFExposure]:
        """Get ETF stock exposure"""
        return await self.client.request_async(ETF_EXPOSURE, symbol=symbol)

    async def get_etf_holder(self, symbol: str) -> list[ETFHolder]:
        """Get ETF holder information"""
        return await self.client.request_async(ETF_HOLDER, symbol=symbol)

    # Mutual Fund methods
    async def get_mutual_fund_dates(
        self, symbol: str, cik: str | None = None
    ) -> list[date]:
        """Get mutual fund/ETF disclosure dates

        Args:
            symbol: Fund or ETF symbol
            cik: Deprecated, no longer used by the API

        Returns:
            List of disclosure dates
        """
        if cik is not None:
            warnings.warn(
                "The 'cik' parameter is deprecated and no longer used by the API",
                DeprecationWarning,
                stacklevel=2,
            )
        return await self.client.request_async(MUTUAL_FUND_DATES, symbol=symbol)

    async def get_mutual_fund_holdings(
        self, symbol: str, holdings_date: date
    ) -> list[MutualFundHolding]:
        """Get mutual fund holdings"""
        return await self.client.request_async(
            MUTUAL_FUND_HOLDINGS, symbol=symbol, date=holdings_date.strftime("%Y-%m-%d")
        )

    async def get_mutual_fund_by_name(self, name: str) -> list[MutualFundHolding]:
        """Get mutual funds by name"""
        return await self.client.request_async(MUTUAL_FUND_BY_NAME, name=name)

    async def get_mutual_fund_holder(self, symbol: str) -> list[MutualFundHolder]:
        """Get mutual fund holder information"""
        return await self.client.request_async(MUTUAL_FUND_HOLDER, symbol=symbol)
