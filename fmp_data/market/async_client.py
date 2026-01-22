# fmp_data/market/async_client.py
"""Async client for market data endpoints."""

from datetime import date as dt_date

from fmp_data.base import AsyncEndpointGroup
from fmp_data.market.endpoints import (
    ACTIVELY_TRADING_LIST,
    ALL_EXCHANGE_MARKET_HOURS,
    ALL_SHARES_FLOAT,
    AVAILABLE_COUNTRIES,
    AVAILABLE_EXCHANGES,
    AVAILABLE_INDEXES,
    AVAILABLE_INDUSTRIES,
    AVAILABLE_SECTORS,
    CIK_LIST,
    CIK_SEARCH,
    COMPANY_SCREENER,
    CUSIP_SEARCH,
    ETF_LIST,
    FINANCIAL_STATEMENT_SYMBOL_LIST,
    GAINERS,
    HISTORICAL_INDUSTRY_PE,
    HISTORICAL_INDUSTRY_PERFORMANCE,
    HISTORICAL_SECTOR_PE,
    HISTORICAL_SECTOR_PERFORMANCE,
    HOLIDAYS_BY_EXCHANGE,
    INDUSTRY_PE_SNAPSHOT,
    INDUSTRY_PERFORMANCE_SNAPSHOT,
    IPO_DISCLOSURE,
    IPO_PROSPECTUS,
    ISIN_SEARCH,
    LOSERS,
    MARKET_HOURS,
    MOST_ACTIVE,
    PRE_POST_MARKET,
    SEARCH_COMPANY,
    SEARCH_EXCHANGE_VARIANTS,
    SEARCH_SYMBOL,
    SECTOR_PE_SNAPSHOT,
    SECTOR_PERFORMANCE,
    STOCK_LIST,
    TRADABLE_SEARCH,
)
from fmp_data.market.models import (
    AvailableIndex,
    CIKListEntry,
    CIKResult,
    CompanySearchResult,
    CUSIPResult,
    ExchangeSymbol,
    IndustryPerformance,
    IndustryPESnapshot,
    IPODisclosure,
    IPOProspectus,
    ISINResult,
    MarketHoliday,
    MarketHours,
    MarketMover,
    PrePostMarketQuote,
    SectorPerformance,
    SectorPESnapshot,
)
from fmp_data.models import CompanySymbol, ShareFloat


class AsyncMarketClient(AsyncEndpointGroup):
    """Async client for market data endpoints."""

    async def search_company(
        self, query: str, limit: int | None = None, exchange: str | None = None
    ) -> list[CompanySearchResult]:
        """Search for companies"""
        params: dict[str, str | int] = {"query": query}
        if limit is not None:
            params["limit"] = limit
        if exchange is not None:
            params["exchange"] = exchange
        return await self.client.request_async(SEARCH_COMPANY, **params)

    async def search_symbol(
        self, query: str, limit: int | None = None, exchange: str | None = None
    ) -> list[CompanySearchResult]:
        """Search for security symbols across all asset types"""
        params: dict[str, str | int] = {"query": query}
        if limit is not None:
            params["limit"] = limit
        if exchange is not None:
            params["exchange"] = exchange
        return await self.client.request_async(SEARCH_SYMBOL, **params)

    async def search_exchange_variants(self, query: str) -> list[CompanySearchResult]:
        """Search for exchange trading variants of a company"""
        return await self.client.request_async(SEARCH_EXCHANGE_VARIANTS, query=query)

    async def get_stock_list(self) -> list[CompanySymbol]:
        """Get list of all available stocks"""
        return await self.client.request_async(STOCK_LIST)

    async def get_financial_statement_symbol_list(self) -> list[CompanySymbol]:
        """Get list of symbols with financial statements available"""
        return await self.client.request_async(FINANCIAL_STATEMENT_SYMBOL_LIST)

    async def get_etf_list(self) -> list[CompanySymbol]:
        """Get list of all available ETFs"""
        return await self.client.request_async(ETF_LIST)

    async def get_actively_trading_list(self) -> list[CompanySymbol]:
        """Get list of actively trading stocks"""
        return await self.client.request_async(ACTIVELY_TRADING_LIST)

    async def get_tradable_list(
        self, limit: int | None = None, offset: int | None = None
    ) -> list[CompanySymbol]:
        """Get list of tradable securities"""
        params: dict[str, int] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return await self.client.request_async(TRADABLE_SEARCH, **params)

    async def get_available_indexes(self) -> list[AvailableIndex]:
        """Get list of all available indexes"""
        return await self.client.request_async(AVAILABLE_INDEXES)

    async def search_by_cik(self, query: str) -> list[CIKResult]:
        """Search companies by CIK number"""
        return await self.client.request_async(CIK_SEARCH, query=query)

    async def get_cik_list(
        self, page: int = 0, limit: int = 1000
    ) -> list[CIKListEntry]:
        """Get complete list of all CIK numbers"""
        return await self.client.request_async(CIK_LIST, page=page, limit=limit)

    async def search_by_cusip(self, query: str) -> list[CUSIPResult]:
        """Search companies by CUSIP"""
        return await self.client.request_async(CUSIP_SEARCH, query=query)

    async def search_by_isin(self, query: str) -> list[ISINResult]:
        """Search companies by ISIN"""
        return await self.client.request_async(ISIN_SEARCH, query=query)

    async def get_company_screener(
        self,
        market_cap_more_than: float | None = None,
        market_cap_less_than: float | None = None,
        price_more_than: float | None = None,
        price_less_than: float | None = None,
        beta_more_than: float | None = None,
        beta_less_than: float | None = None,
        volume_more_than: int | None = None,
        volume_less_than: int | None = None,
        dividend_more_than: float | None = None,
        dividend_less_than: float | None = None,
        is_etf: bool | None = None,
        is_fund: bool | None = None,
        is_actively_trading: bool | None = None,
        sector: str | None = None,
        industry: str | None = None,
        country: str | None = None,
        exchange: str | None = None,
        limit: int | None = None,
        include_all_share_classes: bool | None = None,
    ) -> list[CompanySearchResult]:
        """Screen companies based on various criteria"""
        params = {
            "market_cap_more_than": market_cap_more_than,
            "market_cap_less_than": market_cap_less_than,
            "price_more_than": price_more_than,
            "price_less_than": price_less_than,
            "beta_more_than": beta_more_than,
            "beta_less_than": beta_less_than,
            "volume_more_than": volume_more_than,
            "volume_less_than": volume_less_than,
            "dividend_more_than": dividend_more_than,
            "dividend_less_than": dividend_less_than,
            "is_etf": is_etf,
            "is_fund": is_fund,
            "is_actively_trading": is_actively_trading,
            "sector": sector,
            "industry": industry,
            "country": country,
            "exchange": exchange,
            "limit": limit,
            "include_all_share_classes": include_all_share_classes,
        }
        params = {key: value for key, value in params.items() if value is not None}
        return await self.client.request_async(COMPANY_SCREENER, **params)

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
        if isinstance(result, list):
            if not result:
                raise ValueError("No market hours data returned from API")
            return result[0]
        return result

    async def get_all_exchange_market_hours(self) -> list[MarketHours]:
        """Get market trading hours information for all exchanges"""
        result = await self.client.request_async(ALL_EXCHANGE_MARKET_HOURS)
        if isinstance(result, list):
            return result
        return [result]

    async def get_holidays_by_exchange(
        self, exchange: str = "NYSE"
    ) -> list[MarketHoliday]:
        """Get market holidays for a specific exchange"""
        return await self.client.request_async(HOLIDAYS_BY_EXCHANGE, exchange=exchange)

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
        self,
        sector: str | None = None,
        date: dt_date | None = None,
        exchange: str | None = None,
    ) -> list[SectorPerformance]:
        """Get sector performance data"""
        params: dict[str, str] = {}
        if sector is not None:
            params["sector"] = sector
        if exchange is not None:
            params["exchange"] = exchange
        snapshot_date = date or dt_date.today()
        params["date"] = snapshot_date.strftime("%Y-%m-%d")
        return await self.client.request_async(SECTOR_PERFORMANCE, **params)

    async def get_industry_performance_snapshot(
        self,
        industry: str | None = None,
        date: dt_date | None = None,
        exchange: str | None = None,
    ) -> list[IndustryPerformance]:
        """Get industry performance snapshot data"""
        params: dict[str, str] = {}
        if industry is not None:
            params["industry"] = industry
        if exchange is not None:
            params["exchange"] = exchange
        snapshot_date = date or dt_date.today()
        params["date"] = snapshot_date.strftime("%Y-%m-%d")
        return await self.client.request_async(INDUSTRY_PERFORMANCE_SNAPSHOT, **params)

    async def get_historical_sector_performance(
        self,
        sector: str,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
        exchange: str | None = None,
    ) -> list[SectorPerformance]:
        """Get historical sector performance data"""
        params: dict[str, str] = {"sector": sector}
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        if exchange:
            params["exchange"] = exchange
        return await self.client.request_async(HISTORICAL_SECTOR_PERFORMANCE, **params)

    async def get_historical_industry_performance(
        self,
        industry: str,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
        exchange: str | None = None,
    ) -> list[IndustryPerformance]:
        """Get historical industry performance data"""
        params: dict[str, str] = {"industry": industry}
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        if exchange:
            params["exchange"] = exchange
        return await self.client.request_async(
            HISTORICAL_INDUSTRY_PERFORMANCE, **params
        )

    async def get_sector_pe_snapshot(
        self,
        date: dt_date | None = None,
        sector: str | None = None,
        exchange: str | None = None,
    ) -> list[SectorPESnapshot]:
        """Get sector price-to-earnings snapshot data"""
        params: dict[str, str] = {}
        if sector is not None:
            params["sector"] = sector
        if exchange is not None:
            params["exchange"] = exchange
        snapshot_date = date or dt_date.today()
        params["date"] = snapshot_date.strftime("%Y-%m-%d")
        return await self.client.request_async(SECTOR_PE_SNAPSHOT, **params)

    async def get_industry_pe_snapshot(
        self,
        date: dt_date | None = None,
        industry: str | None = None,
        exchange: str | None = None,
    ) -> list[IndustryPESnapshot]:
        """Get industry price-to-earnings snapshot data"""
        params: dict[str, str] = {}
        if industry is not None:
            params["industry"] = industry
        if exchange is not None:
            params["exchange"] = exchange
        snapshot_date = date or dt_date.today()
        params["date"] = snapshot_date.strftime("%Y-%m-%d")
        return await self.client.request_async(INDUSTRY_PE_SNAPSHOT, **params)

    async def get_historical_sector_pe(
        self,
        sector: str,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
        exchange: str | None = None,
    ) -> list[SectorPESnapshot]:
        """Get historical sector price-to-earnings data"""
        params: dict[str, str] = {"sector": sector}
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        if exchange:
            params["exchange"] = exchange
        return await self.client.request_async(HISTORICAL_SECTOR_PE, **params)

    async def get_historical_industry_pe(
        self,
        industry: str,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
        exchange: str | None = None,
    ) -> list[IndustryPESnapshot]:
        """Get historical industry price-to-earnings data"""
        params: dict[str, str] = {"industry": industry}
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        if exchange:
            params["exchange"] = exchange
        return await self.client.request_async(HISTORICAL_INDUSTRY_PE, **params)

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
