# fmp_data/market/client.py
from datetime import date as dt_date

from fmp_data.base import EndpointGroup
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

    def search_symbol(
        self, query: str, limit: int | None = None, exchange: str | None = None
    ) -> list[CompanySearchResult]:
        """Search for security symbols across all asset types"""
        params = {"query": query}
        if limit is not None:
            params["limit"] = str(limit)
        if exchange is not None:
            params["exchange"] = exchange
        return self.client.request(SEARCH_SYMBOL, **params)

    def search_exchange_variants(self, query: str) -> list[CompanySearchResult]:
        """Search for exchange trading variants of a company"""
        return self.client.request(SEARCH_EXCHANGE_VARIANTS, query=query)

    def get_stock_list(self) -> list[CompanySymbol]:
        """Get list of all available stocks"""
        return self.client.request(STOCK_LIST)

    def get_financial_statement_symbol_list(self) -> list[CompanySymbol]:
        """Get list of symbols with financial statements available"""
        return self.client.request(FINANCIAL_STATEMENT_SYMBOL_LIST)

    def get_etf_list(self) -> list[CompanySymbol]:
        """Get list of all available ETFs"""
        return self.client.request(ETF_LIST)

    def get_actively_trading_list(self) -> list[CompanySymbol]:
        """Get list of actively trading stocks"""
        return self.client.request(ACTIVELY_TRADING_LIST)

    def get_tradable_list(
        self, limit: int | None = None, offset: int | None = None
    ) -> list[CompanySymbol]:
        """Get list of tradable securities"""
        params: dict[str, int] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return self.client.request(TRADABLE_SEARCH, **params)

    def get_available_indexes(self) -> list[AvailableIndex]:
        """Get list of all available indexes"""
        return self.client.request(AVAILABLE_INDEXES)

    def search_by_cik(self, query: str) -> list[CIKResult]:
        """Search companies by CIK number"""
        return self.client.request(CIK_SEARCH, query=query)

    def get_cik_list(self, page: int = 0, limit: int = 1000) -> list[CIKListEntry]:
        """Get complete list of all CIK numbers"""
        return self.client.request(CIK_LIST, page=page, limit=limit)

    def search_by_cusip(self, query: str) -> list[CUSIPResult]:
        """Search companies by CUSIP"""
        return self.client.request(CUSIP_SEARCH, query=query)

    def search_by_isin(self, query: str) -> list[ISINResult]:
        """Search companies by ISIN"""
        return self.client.request(ISIN_SEARCH, query=query)

    def get_company_screener(
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
        return self.client.request(COMPANY_SCREENER, **params)

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
        if isinstance(result, list):
            if not result:
                raise ValueError("No market hours data returned from API")
            return result[0]
        return result

    def get_all_exchange_market_hours(self) -> list[MarketHours]:
        """Get market trading hours information for all exchanges"""
        result = self.client.request(ALL_EXCHANGE_MARKET_HOURS)
        if isinstance(result, list):
            return result
        return [result]

    def get_holidays_by_exchange(self, exchange: str = "NYSE") -> list[MarketHoliday]:
        """Get market holidays for a specific exchange"""
        return self.client.request(HOLIDAYS_BY_EXCHANGE, exchange=exchange)

    def get_gainers(self) -> list[MarketMover]:
        """Get market gainers"""
        return self.client.request(GAINERS)

    def get_losers(self) -> list[MarketMover]:
        """Get market losers"""
        return self.client.request(LOSERS)

    def get_most_active(self) -> list[MarketMover]:
        """Get most active stocks"""
        return self.client.request(MOST_ACTIVE)

    def get_sector_performance(
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
        return self.client.request(SECTOR_PERFORMANCE, **params)

    def get_industry_performance_snapshot(
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
        return self.client.request(INDUSTRY_PERFORMANCE_SNAPSHOT, **params)

    def get_historical_sector_performance(
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
        return self.client.request(HISTORICAL_SECTOR_PERFORMANCE, **params)

    def get_historical_industry_performance(
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
        return self.client.request(HISTORICAL_INDUSTRY_PERFORMANCE, **params)

    def get_sector_pe_snapshot(
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
        return self.client.request(SECTOR_PE_SNAPSHOT, **params)

    def get_industry_pe_snapshot(
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
        return self.client.request(INDUSTRY_PE_SNAPSHOT, **params)

    def get_historical_sector_pe(
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
        return self.client.request(HISTORICAL_SECTOR_PE, **params)

    def get_historical_industry_pe(
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
        return self.client.request(HISTORICAL_INDUSTRY_PE, **params)

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
        return self.client.request(IPO_DISCLOSURE, **params)

    def get_ipo_prospectus(
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
        return self.client.request(IPO_PROSPECTUS, **params)
