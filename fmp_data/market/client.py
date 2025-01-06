# fmp_data/market/client.py
from typing import cast

from fmp_data.base import EndpointGroup
from fmp_data.market.endpoints import (
    ALL_SHARES_FLOAT,
    AVAILABLE_INDEXES,
    CIK_SEARCH,
    CUSIP_SEARCH,
    ETF_LIST,
    EXCHANGE_SYMBOLS,
    GAINERS,
    ISIN_SEARCH,
    LOSERS,
    MARKET_HOURS,
    MOST_ACTIVE,
    PRE_POST_MARKET,
    SEARCH,
    SECTOR_PERFORMANCE,
    STOCK_LIST,
)
from fmp_data.market.models import (
    AvailableIndex,
    CIKResult,
    CompanySearchResult,
    CUSIPResult,
    ExchangeSymbol,
    ISINResult,
    MarketHours,
    MarketMover,
    PrePostMarketQuote,
    SectorPerformance,
)
from fmp_data.models import CompanySymbol, ShareFloat


class MarketClient(EndpointGroup):
    """Client for market data endpoints"""

    def search(
        self, query: str, limit: int | None = None, exchange: str | None = None
    ) -> list[CompanySearchResult]:
        """Search for companies"""
        params = {"query": query}
        if limit is not None:
            params["limit"] = str(limit)
        if exchange is not None:
            params["exchange"] = exchange
        return self.client.request(SEARCH, **params)

    def get_stock_list(self) -> list[CompanySymbol]:
        """Get list of all available stocks"""
        return self.client.request(STOCK_LIST)

    def get_etf_list(self) -> list[CompanySymbol]:
        """Get list of all available ETFs"""
        return self.client.request(ETF_LIST)

    def get_available_indexes(self) -> list[AvailableIndex]:
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

    def get_market_hours(self) -> MarketHours:
        """Get market trading hours information"""
        result = self.client.request(MARKET_HOURS)
        return cast(MarketHours, result)

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
