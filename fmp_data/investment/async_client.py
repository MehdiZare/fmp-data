# fmp_data/investment/async_client.py
"""Async client for investment products endpoints."""

from datetime import date
import logging
import warnings

from fmp_data.base import AsyncEndpointGroup
from fmp_data.exceptions import FMPError, ValidationError
from fmp_data.investment.endpoints import (
    ETF_COUNTRY_WEIGHTINGS,
    ETF_EXPOSURE,
    ETF_HOLDER,
    ETF_HOLDING_DATES,
    ETF_HOLDINGS,
    ETF_INFO,
    ETF_SECTOR_WEIGHTINGS,
    FUNDS_DISCLOSURE,
    FUNDS_DISCLOSURE_HOLDERS_LATEST,
    FUNDS_DISCLOSURE_HOLDERS_SEARCH,
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
    FundDisclosureHolderLatest,
    FundDisclosureHolding,
    FundDisclosureSearchResult,
    MutualFundHolder,
    MutualFundHolding,
)

logger = logging.getLogger(__name__)


class AsyncInvestmentClient(AsyncEndpointGroup):
    """Async client for investment products endpoints."""

    # ETF methods
    async def get_etf_holdings(
        self, symbol: str, holdings_date: date | None = None
    ) -> list[ETFHolding]:
        """Get ETF holdings"""
        params: dict[str, str] = {"symbol": symbol}
        if holdings_date is not None:
            params["date"] = holdings_date.strftime("%Y-%m-%d")
        return await self.client.request_async(ETF_HOLDINGS, **params)

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
        except (FMPError, ValidationError) as e:
            warnings.warn(f"Error in get_etf_info: {e!s}", stacklevel=2)
            return None
        except Exception:
            logger.exception("Unexpected error in get_etf_info for symbol %s", symbol)
            raise

    async def get_etf_sector_weightings(self, symbol: str) -> list[ETFSectorWeighting]:
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
            cik: Optional fund CIK

        Returns:
            List of disclosure dates
        """
        params: dict[str, str] = {"symbol": symbol}
        if cik is not None:
            params["cik"] = cik
        return await self.client.request_async(MUTUAL_FUND_DATES, **params)

    async def get_fund_disclosure_dates(
        self, symbol: str, cik: str | None = None
    ) -> list[date]:
        """Get mutual fund/ETF disclosure dates"""
        return await self.get_mutual_fund_dates(symbol=symbol, cik=cik)

    async def get_mutual_fund_holdings(
        self, symbol: str, holdings_date: date
    ) -> list[MutualFundHolding]:
        """Get mutual fund holdings"""
        return await self.client.request_async(
            MUTUAL_FUND_HOLDINGS,
            symbol=symbol,
            date=holdings_date.strftime("%Y-%m-%d"),
        )

    async def get_mutual_fund_by_name(self, name: str) -> list[MutualFundHolding]:
        """Get mutual funds by name"""
        return await self.client.request_async(MUTUAL_FUND_BY_NAME, name=name)

    async def get_mutual_fund_holder(self, symbol: str) -> list[MutualFundHolder]:
        """Get mutual fund holder information"""
        return await self.client.request_async(MUTUAL_FUND_HOLDER, symbol=symbol)

    async def get_fund_disclosure_holders_latest(
        self, symbol: str
    ) -> list[FundDisclosureHolderLatest]:
        """Get latest mutual fund/ETF disclosure holders"""
        return await self.client.request_async(
            FUNDS_DISCLOSURE_HOLDERS_LATEST, symbol=symbol
        )

    async def get_fund_disclosure(
        self, symbol: str, year: int, quarter: int, cik: str | None = None
    ) -> list[FundDisclosureHolding]:
        """Get mutual fund/ETF disclosure holdings"""
        params: dict[str, str | int] = {
            "symbol": symbol,
            "year": year,
            "quarter": quarter,
        }
        if cik is not None:
            params["cik"] = cik
        return await self.client.request_async(FUNDS_DISCLOSURE, **params)

    async def search_fund_disclosure_holders(
        self, name: str
    ) -> list[FundDisclosureSearchResult]:
        """Search mutual fund/ETF disclosure holders by name"""
        return await self.client.request_async(
            FUNDS_DISCLOSURE_HOLDERS_SEARCH, name=name
        )
