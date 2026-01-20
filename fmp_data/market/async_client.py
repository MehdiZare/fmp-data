# fmp_data/market/async_client.py
"""Async client for market data endpoints."""
from datetime import date as dt_date
from typing import cast

from fmp_data.base import AsyncEndpointGroup
from fmp_data.market.endpoints import (
    ALL_SHARES_FLOAT,
    AVAILABLE_COUNTRIES,
    AVAILABLE_EXCHANGES,
    AVAILABLE_INDEXES,
    AVAILABLE_INDUSTRIES,
    AVAILABLE_SECTORS,
    CIK_SEARCH,
    CUSIP_SEARCH,
    ETF_LIST,
    GAINERS,
    IPO_DISCLOSURE,
    IPO_PROSPECTUS,
    ISIN_SEARCH,
    LOSERS,
    MARKET_HOURS,
    MOST_ACTIVE,
    PRE_POST_MARKET,
    SEARCH_COMPANY,
    SECTOR_PERFORMANCE,
    STOCK_LIST,
)
from fmp_data.market.models import (
    AvailableIndex,
    CIKResult,
    CompanySearchResult,
    CUSIPResult,
    ExchangeSymbol,
    IPODisclosure,
    IPOProspectus,
    ISINResult,
    MarketHours,
    MarketMover,
    PrePostMarketQuote,
    SectorPerformance,
)
from fmp_data.models import CompanySymbol, ShareFloat


class AsyncMarketClient(AsyncEndpointGroup):
    """Async client for market data endpoints."""

    async def search_company(
        self, query: str, limit: int | None = None, exchange: str | None = None
    ) -> list[CompanySearchResult]:
        """Search for companies"""
        params = {"query": query}
        if limit is not None:
            params["limit"] = str(limit)
        if exchange is not None:
            params["exchange"] = exchange
        return await self.client.request_async(SEARCH_COMPANY, **params)

    async def get_stock_list(self) -> list[CompanySymbol]:
        """Get list of all available stocks"""
        return await self.client.request_async(STOCK_LIST)

    async def get_etf_list(self) -> list[CompanySymbol]:
        """Get list of all available ETFs"""
        return await self.client.request_async(ETF_LIST)

    async def get_available_indexes(self) -> list[AvailableIndex]:
        """Get list of all available indexes"""
        return await self.client.request_async(AVAILABLE_INDEXES)

    async def search_by_cik(self, query: str) -> list[CIKResult]:
        """Search companies by CIK number"""
        return await self.client.request_async(CIK_SEARCH, query=query)

    async def search_by_cusip(self, query: str) -> list[CUSIPResult]:
        """Search companies by CUSIP"""
        return await self.client.request_async(CUSIP_SEARCH, query=query)

    async def search_by_isin(self, query: str) -> list[ISINResult]:
        """Search companies by ISIN"""
        return await self.client.request_async(ISIN_SEARCH, query=query)

    async def get_market_hours(self, exchange: str = "NYSE") -> MarketHours:
        """Get market trading hours information for a specific exchange

        Args:
            exchange: Exchange code (e.g., "NYSE", "NASDAQ"). Defaults to "NYSE".

        Returns:
            MarketHours: Exchange trading hours object

        Raises:
            ValueError: If no market hours data returned from API
        """
        result = await self.client.request_async(MARKET_HOURS, exchange=exchange)

        # result is already a list[MarketHours] from base client processing
        if not isinstance(result, list) or not result:
            raise ValueError("No market hours data returned from API")

        # Cast to help mypy understand the type
        return cast(MarketHours, result[0])

    async def get_gainers(self) -> list[MarketMover]:
        """Get market gainers"""
        return await self.client.request_async(GAINERS)

    async def get_losers(self) -> list[MarketMover]:
        """Get market losers"""
        return await self.client.request_async(LOSERS)

    async def get_most_active(self) -> list[MarketMover]:
        """Get most active stocks"""
        return await self.client.request_async(MOST_ACTIVE)

    async def get_sector_performance(
        self, sector: str | None = None, date: dt_date | None = None
    ) -> list[SectorPerformance]:
        """Get sector performance data"""
        params = {}
        if sector is not None:
            params["sector"] = sector
        snapshot_date = date or dt_date.today()
        params["date"] = snapshot_date.strftime("%Y-%m-%d")
        return await self.client.request_async(SECTOR_PERFORMANCE, **params)

    async def get_pre_post_market(self) -> list[PrePostMarketQuote]:
        """Get pre/post market data"""
        return await self.client.request_async(PRE_POST_MARKET)

    async def get_all_shares_float(self) -> list[ShareFloat]:
        """Get share float data for all companies"""
        return await self.client.request_async(ALL_SHARES_FLOAT)

    async def get_available_exchanges(self) -> list[ExchangeSymbol]:
        """Get a complete list of supported stock exchanges"""
        return await self.client.request_async(AVAILABLE_EXCHANGES)

    async def get_available_sectors(self) -> list[str]:
        """Get a complete list of industry sectors"""
        return await self.client.request_async(AVAILABLE_SECTORS)

    async def get_available_industries(self) -> list[str]:
        """Get a comprehensive list of industries where stock symbols are available"""
        return await self.client.request_async(AVAILABLE_INDUSTRIES)

    async def get_available_countries(self) -> list[str]:
        """Get a comprehensive list of countries where stock symbols are available"""
        return await self.client.request_async(AVAILABLE_COUNTRIES)

    async def get_ipo_disclosure(
        self,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
        limit: int = 100,
    ) -> list[IPODisclosure]:
        """Get IPO disclosure documents

        Args:
            from_date: Start date for IPO search (YYYY-MM-DD)
            to_date: End date for IPO search (YYYY-MM-DD)
            limit: Number of results to return (default: 100)

        Returns:
            List of IPO disclosure information
        """
        params: dict[str, str | int] = {"limit": limit}
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        return await self.client.request_async(IPO_DISCLOSURE, **params)

    async def get_ipo_prospectus(
        self,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
        limit: int = 100,
    ) -> list[IPOProspectus]:
        """Get IPO prospectus documents

        Args:
            from_date: Start date for IPO search (YYYY-MM-DD)
            to_date: End date for IPO search (YYYY-MM-DD)
            limit: Number of results to return (default: 100)

        Returns:
            List of IPO prospectus information
        """
        params: dict[str, str | int] = {"limit": limit}
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        return await self.client.request_async(IPO_PROSPECTUS, **params)
