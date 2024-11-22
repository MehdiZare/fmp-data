from datetime import datetime

from fmp_data import FMPDataClient
from fmp_data.market.models import (
    HistoricalData,
    IntradayPrice,
    MarketCapitalization,
    MarketHours,
    MarketMover,
    PrePostMarketQuote,
    Quote,
    SectorPerformance,
    SimpleQuote,
)


class TestMarketClientEndpoints:
    """Integration tests for MarketClient endpoints using VCR"""

    def test_get_quote(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting real-time stock quote"""
        with vcr_instance.use_cassette("market/quote.yaml"):
            quote = fmp_client.market.get_quote("AAPL")

            assert isinstance(quote, Quote)
            assert quote.symbol == "AAPL"
            assert quote.name
            assert isinstance(quote.price, float)
            assert isinstance(quote.change_percentage, float)
            assert isinstance(quote.market_cap, float)
            assert isinstance(quote.volume, int)
            assert isinstance(quote.timestamp, datetime)

    def test_get_simple_quote(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting simple stock quote"""
        with vcr_instance.use_cassette("market/simple_quote.yaml"):
            quote = fmp_client.market.get_simple_quote("AAPL")

            assert isinstance(quote, SimpleQuote)
            assert quote.symbol == "AAPL"
            assert isinstance(quote.price, float)
            assert isinstance(quote.volume, int)

    def test_get_historical_prices(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical price data"""
        with vcr_instance.use_cassette("market/historical_prices.yaml"):
            prices = fmp_client.market.get_historical_prices(
                "AAPL", from_date="2023-01-01", to_date="2023-01-31"
            )

            assert isinstance(prices, HistoricalData)
            assert len(prices.historical) > 0

            for price in prices.historical:
                assert isinstance(price.date, datetime)
                assert isinstance(price.open, float)
                assert isinstance(price.high, float)
                assert isinstance(price.low, float)
                assert isinstance(price.close, float)
                assert isinstance(price.adj_close, float)
                assert isinstance(price.volume, int)

    def test_get_intraday_prices(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting intraday price data"""
        with vcr_instance.use_cassette("market/intraday_prices.yaml"):
            prices = fmp_client.market.get_intraday_prices("AAPL", interval="5min")

            assert isinstance(prices, list)
            assert len(prices) > 0

            for price in prices:
                assert isinstance(price, IntradayPrice)
                assert isinstance(price.date, datetime)
                assert isinstance(price.open, float)
                assert isinstance(price.high, float)
                assert isinstance(price.low, float)
                assert isinstance(price.close, float)
                assert isinstance(price.volume, int)

    def test_get_market_hours(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting market hours information"""
        with vcr_instance.use_cassette("market/market_hours.yaml"):
            hours = fmp_client.market.get_market_hours()

            assert isinstance(hours, MarketHours)
            assert hours.stockExchangeName
            assert hours.stockMarketHours
            assert isinstance(hours.stockMarketHolidays, list)
            assert isinstance(hours.isTheStockMarketOpen, bool)
            assert isinstance(hours.isTheEuronextMarketOpen, bool)
            assert isinstance(hours.isTheForexMarketOpen, bool)
            assert isinstance(hours.isTheCryptoMarketOpen, bool)

    def test_get_market_cap(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting market capitalization data"""
        with vcr_instance.use_cassette("market/market_cap.yaml"):
            cap = fmp_client.market.get_market_cap("AAPL")

            assert isinstance(cap, MarketCapitalization)
            assert cap.symbol == "AAPL"
            assert isinstance(cap.date, datetime)
            assert isinstance(cap.market_cap, float)
            assert cap.market_cap > 0

    def test_get_historical_market_cap(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical market capitalization data"""
        with vcr_instance.use_cassette("market/historical_market_cap.yaml"):
            caps = fmp_client.market.get_historical_market_cap("AAPL")

            assert isinstance(caps, list)
            assert len(caps) > 0

            for cap in caps:
                assert isinstance(cap, MarketCapitalization)
                assert cap.symbol == "AAPL"
                assert isinstance(cap.date, datetime)
                assert isinstance(cap.market_cap, float)
                assert cap.market_cap > 0

    def test_get_gainers(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting market gainers"""
        with vcr_instance.use_cassette("market/gainers.yaml"):
            gainers = fmp_client.market.get_gainers()

            assert isinstance(gainers, list)
            assert len(gainers) > 0

            for gainer in gainers:
                assert isinstance(gainer, MarketMover)
                assert gainer.symbol
                assert gainer.name
                assert isinstance(gainer.change, float)
                assert isinstance(gainer.price, float)
                assert isinstance(gainer.change_percentage, float)
                assert gainer.change_percentage > 0

    def test_get_losers(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting market losers"""
        with vcr_instance.use_cassette("market/losers.yaml"):
            losers = fmp_client.market.get_losers()

            assert isinstance(losers, list)
            assert len(losers) > 0

            for loser in losers:
                assert isinstance(loser, MarketMover)
                assert loser.symbol
                assert loser.name
                assert isinstance(loser.change, float)
                assert isinstance(loser.price, float)
                assert isinstance(loser.change_percentage, float)
                assert loser.change_percentage < 0

    def test_get_most_active(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting most active stocks"""
        with vcr_instance.use_cassette("market/most_active.yaml"):
            actives = fmp_client.market.get_most_active()

            assert isinstance(actives, list)
            assert len(actives) > 0

            for active in actives:
                assert isinstance(active, MarketMover)
                assert active.symbol
                assert active.name
                assert isinstance(active.change, float)
                assert isinstance(active.price, float)
                assert isinstance(active.change_percentage, float)

    def test_get_sector_performance(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting sector performance data"""
        with vcr_instance.use_cassette("market/sector_performance.yaml"):
            sectors = fmp_client.market.get_sector_performance()

            assert isinstance(sectors, list)
            assert len(sectors) > 0

            for sector in sectors:
                assert isinstance(sector, SectorPerformance)
                assert sector.sector
                assert isinstance(sector.change_percentage, float)

    def test_get_pre_post_market(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting pre/post market data"""
        with vcr_instance.use_cassette("market/pre_post_market.yaml"):
            quotes = fmp_client.market.get_pre_post_market()

            assert isinstance(quotes, list)
            assert len(quotes) >= 0  # May be empty outside trading hours

            for quote in quotes:
                assert isinstance(quote, PrePostMarketQuote)
                assert quote.symbol
                assert isinstance(quote.timestamp, datetime)
                assert isinstance(quote.price, float)
                assert isinstance(quote.volume, int)
                assert quote.session in ("pre", "post")
