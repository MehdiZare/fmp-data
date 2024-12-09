# fmp_data/market/client.py

from fmp_data.base import EndpointGroup
from fmp_data.market.endpoints import (
    GAINERS,
    HISTORICAL_MARKET_CAP,
    HISTORICAL_PRICE,
    INTRADAY_PRICE,
    LOSERS,
    MARKET_CAP,
    MARKET_HOURS,
    MOST_ACTIVE,
    PRE_POST_MARKET,
    QUOTE,
    SECTOR_PERFORMANCE,
    SIMPLE_QUOTE,
)
from fmp_data.market.models import (
    HistoricalPrice,
    IntradayPrice,
    MarketCapitalization,
    MarketHours,
    MarketMover,
    PrePostMarketQuote,
    Quote,
    SectorPerformance,
    SimpleQuote,
)


class MarketClient(EndpointGroup):
    """Client for market data endpoints"""

    def get_quote(self, symbol: str) -> Quote:
        """Get real-time stock quote"""
        result = self.client.request(QUOTE, symbol=symbol)
        return result[0] if isinstance(result, list) else result

    def get_simple_quote(self, symbol: str) -> SimpleQuote:
        """Get simple stock quote"""
        result = self.client.request(SIMPLE_QUOTE, symbol=symbol)
        return result[0] if isinstance(result, list) else result

    def get_historical_prices(
        self,
        symbol: str,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[HistoricalPrice]:
        """Get historical daily price data"""
        return self.client.request(
            HISTORICAL_PRICE, symbol=symbol, from_=from_date, to=to_date
        )

    def get_intraday_prices(
        self, symbol: str, interval: str = "1min"
    ) -> list[IntradayPrice]:
        """Get intraday price data"""
        return self.client.request(INTRADAY_PRICE, symbol=symbol, interval=interval)

    def get_market_hours(self) -> MarketHours:
        """Get market trading hours information"""
        return self.client.request(MARKET_HOURS)

    def get_market_cap(self, symbol: str) -> MarketCapitalization:
        """Get market capitalization data"""
        result = self.client.request(MARKET_CAP, symbol=symbol)
        return result[0] if isinstance(result, list) else result

    def get_historical_market_cap(self, symbol: str) -> list[MarketCapitalization]:
        """Get historical market capitalization data"""
        return self.client.request(HISTORICAL_MARKET_CAP, symbol=symbol)

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
