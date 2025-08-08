# fmp_data/market/client.py
from datetime import date
from typing import cast

from fmp_data.base import EndpointGroup
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


class MarketClient(EndpointGroup):
    """Client for market data endpoints"""

    def search_company(
        self, query: str, limit: int | None = None, exchange: str | None = None
    ) -> list[CompanySearchResult]:
        """Search for companies"""
        params = {"query": query}
        if limit is not None:
            params["limit"] = str(limit)
        if exchange is not None:
            params["exchange"] = exchange
        return self.client.request(SEARCH_COMPANY, **params)

    def get_stock_list(self) -> list[CompanySymbol]:
        """Get list of all available stocks"""
        return self.client.request(STOCK_LIST)

    def get_etf_list(self) -> list[CompanySymbol]:
        """Get list of all available ETFs"""
        return self.client.request(ETF_LIST)

    def get_available_indexes(self) -> list[AvailableIndex]:
        """Get list of all available indexes"""
        return self.client.request(AVAILABLE_INDEXES)

    def search_by_cik(self, query: str) -> list[CIKResult]:
        """Search companies by CIK number"""
        return self.client.request(CIK_SEARCH, query=query)

    def search_by_cusip(self, query: str) -> list[CUSIPResult]:
        """Search companies by CUSIP"""
        return self.client.request(CUSIP_SEARCH, query=query)

    def search_by_isin(self, query: str) -> list[ISINResult]:
        """Search companies by ISIN"""
        return self.client.request(ISIN_SEARCH, query=query)

    def get_market_hours(self, exchange: str = "NYSE") -> MarketHours:
        """Get market trading hours information for a specific exchange

        Args:
            exchange: Exchange code (e.g., "NYSE", "NASDAQ"). Defaults to "NYSE".

        Returns:
            MarketHours: Exchange trading hours object

        Raises:
            ValueError: If no market hours data returned from API
        """
        result = self.client.request(MARKET_HOURS, exchange=exchange)

        # result is already a list[MarketHours] from base client processing
        if not isinstance(result, list) or not result:
            raise ValueError("No market hours data returned from API")

        # Cast to help mypy understand the type
        return cast(MarketHours, result[0])

    def get_gainers(self) -> list[MarketMover]:
        """Get market gainers"""
        return self.client.request(GAINERS)

    def get_losers(self) -> list[MarketMover]:
        """Get market losers"""
        return self.client.request(LOSERS)

    def get_most_active(self) -> list[MarketMover]:
        """Get most active stocks"""
        return self.client.request(MOST_ACTIVE)

    def get_sector_performance(self) -> list[SectorPerformance]:
        """Get sector performance data"""
        return self.client.request(SECTOR_PERFORMANCE)

    def get_pre_post_market(self) -> list[PrePostMarketQuote]:
        """Get pre/post market data"""
        return self.client.request(PRE_POST_MARKET)

    def get_all_shares_float(self) -> list[ShareFloat]:
        """Get share float data for all companies"""
        return self.client.request(ALL_SHARES_FLOAT)

    def get_available_exchanges(self) -> list[ExchangeSymbol]:
        """Get a complete list of supported stock exchanges"""
        return self.client.request(AVAILABLE_EXCHANGES)

    def get_available_sectors(self) -> list[str]:
        """Get a complete list of industry sectors"""
        return self.client.request(AVAILABLE_SECTORS)

    def get_available_industries(self) -> list[str]:
        """Get a comprehensive list of industries where stock symbols are available"""
        return self.client.request(AVAILABLE_INDUSTRIES)

    def get_available_countries(self) -> list[str]:
        """Get a comprehensive list of countries where stock symbols are available"""
        return self.client.request(AVAILABLE_COUNTRIES)

    def get_ipo_disclosure(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
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
        return self.client.request(IPO_DISCLOSURE, **params)

    def get_ipo_prospectus(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
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
        return self.client.request(IPO_PROSPECTUS, **params)
