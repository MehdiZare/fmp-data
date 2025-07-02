import warnings
from datetime import datetime
from typing import Any

import pytest
import tenacity
import vcr

from fmp_data import FMPDataClient
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
from tests.integration.base import BaseTestCase


class TestMarketClientEndpoints(BaseTestCase):
    """Integration tests for MarketClient endpoints using VCR"""

    def test_get_market_hours(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting market hours information"""
        with vcr_instance.use_cassette("market/market_hours.yaml"):
            hours = self._handle_rate_limit(
                fmp_client.market.get_market_hours,
            )
            assert isinstance(hours, MarketHours)
            assert hours.stockExchangeName
            assert hours.stockMarketHours
            assert isinstance(hours.stockMarketHolidays, list)
            assert isinstance(hours.isTheStockMarketOpen, bool)
            assert isinstance(hours.isTheEuronextMarketOpen, bool)
            assert isinstance(hours.isTheForexMarketOpen, bool)
            assert isinstance(hours.isTheCryptoMarketOpen, bool)

    def test_get_gainers(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting market gainers"""
        with vcr_instance.use_cassette("market/gainers.yaml"):
            gainers = self._handle_rate_limit(
                fmp_client.market.get_gainers,
            )
            assert isinstance(gainers, list)
            assert len(gainers) > 0

            for gainer in gainers:
                assert isinstance(gainer, MarketMover), "gainer type is not MarketMover"
                assert gainer.symbol, "gainer symbol is empty"
                assert gainer.name, "gainer name is empty"
                assert isinstance(gainer.change, float), "gainer change is not float"
                assert isinstance(gainer.price, float), "gainer price is not float"
                if gainer.change_percentage:
                    assert isinstance(
                        gainer.change_percentage, float
                    ), "gainer change_percentage is not float"
                if gainer.change_percentage:
                    assert (
                        gainer.change_percentage > 0
                    ), "gainer change_percentage is not positive"

    def test_get_losers(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting market losers"""
        with vcr_instance.use_cassette("market/losers.yaml"):
            losers = self._handle_rate_limit(
                fmp_client.market.get_losers,
            )

            assert isinstance(losers, list), "losers type is not list"
            assert len(losers) > 0

            for loser in losers:
                assert isinstance(loser, MarketMover), "loser type is not MarketMover"
                assert loser.symbol, "loser symbol is empty"
                assert loser.name, "loser name is empty"
                if loser.change_percentage:
                    assert isinstance(
                        loser.change_percentage,
                        float,
                    ), "loser change_percentage is not float"
                if loser.change:
                    assert loser.change < 0, "loser change is not negative"
                if loser.price:
                    assert isinstance(loser.price, float), "loser price is not float"

    def test_get_most_active(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting most active stocks"""
        with vcr_instance.use_cassette("market/most_active.yaml"):
            actives = self._handle_rate_limit(
                fmp_client.market.get_most_active,
            )

            assert isinstance(actives, list)
            assert len(actives) > 0

            for active in actives:
                assert isinstance(active, MarketMover)
                assert active.symbol
                assert active.name
                if active.change:
                    assert isinstance(
                        active.change, float
                    ), "active change is not float"
                if active.price:
                    assert isinstance(active.price, float), "active price is not float"
                if active.change_percentage:
                    assert isinstance(
                        active.change_percentage,
                        float,
                    ), "active change_percentage is not float"

    def test_get_sector_performance(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting sector performance data"""
        with vcr_instance.use_cassette("market/sector_performance.yaml"):
            sectors = self._handle_rate_limit(fmp_client.market.get_sector_performance)

            assert isinstance(sectors, list)
            assert len(sectors) > 0

            for sector in sectors:
                assert isinstance(sector, SectorPerformance)
                assert isinstance(sector.change_percentage, float)

    def test_get_pre_post_market(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting pre/post market data"""
        with vcr_instance.use_cassette("market/pre_post_market.yaml"):
            quotes = self._handle_rate_limit(
                fmp_client.market.get_pre_post_market,
            )

            assert isinstance(quotes, list)
            assert len(quotes) >= 0  # May be empty outside trading hours

            for quote in quotes:
                assert isinstance(quote, PrePostMarketQuote)
                assert quote.symbol
                assert isinstance(quote.timestamp, datetime)
                assert isinstance(quote.price, float)
                assert isinstance(quote.volume, int)
                assert quote.session in ("pre", "post")

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(3),
    )
    def test_search(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test company search"""
        with vcr_instance.use_cassette("market/search.yaml"):
            results = self._handle_rate_limit(
                fmp_client.market.search, "Apple", limit=5
            )
            assert isinstance(results, list)
            assert len(results) <= 5
            assert all(isinstance(r, CompanySearchResult) for r in results)

    def test_get_stock_list(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test getting stock list"""
        with vcr_instance.use_cassette("market/stock_list.yaml"):
            stocks = self._handle_rate_limit(fmp_client.market.get_stock_list)
            assert isinstance(stocks, list)
            assert len(stocks) > 0
            for stock in stocks:
                assert isinstance(stock, CompanySymbol)
                assert hasattr(stock, "symbol")  # Only check required field
                assert isinstance(stock.symbol, str)

    def test_get_etf_list(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test getting ETF list"""
        with vcr_instance.use_cassette("market/etf_list.yaml"):
            etfs = self._handle_rate_limit(
                fmp_client.market.get_etf_list,
            )
            assert isinstance(etfs, list)
            assert all(isinstance(e, CompanySymbol) for e in etfs)
            assert len(etfs) > 0

    def test_get_available_indexes(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test getting available indexes"""
        with vcr_instance.use_cassette("market/indexes.yaml"):
            indexes = self._handle_rate_limit(fmp_client.market.get_available_indexes)
            assert isinstance(indexes, list)
            assert all(isinstance(i, AvailableIndex) for i in indexes)
            assert any(i.symbol == "^GSPC" for i in indexes)

    def test_get_exchange_symbols(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test getting exchange symbols"""
        with vcr_instance.use_cassette("market/exchange_symbols.yaml"):
            # Capture warnings during test
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")

                symbols = self._handle_rate_limit(
                    fmp_client.market.get_exchange_symbols, "NASDAQ"
                )

                # Basic validation
                assert isinstance(symbols, list)
                assert len(symbols) > 0

                # Test symbol attributes
                for symbol in symbols:
                    assert isinstance(symbol, ExchangeSymbol)
                    # Only check presence of attributes, not values
                    assert hasattr(symbol, "name")
                    assert hasattr(symbol, "price")
                    assert hasattr(symbol, "exchange")

                # Verify we got some data
                valid_symbols = [
                    s for s in symbols if s.name is not None and s.price is not None
                ]
                assert len(valid_symbols) > 0

                # Log warnings if any
                if len(w) > 0:
                    print(f"\nCaptured {len(w)} validation warnings:")
                    for warning in w:
                        print(f"  - {warning.message}")

    @pytest.mark.parametrize(
        "search_type,method,model,test_value",
        [
            ("cik", "search_by_cik", CIKResult, "0000320193"),
            ("cusip", "search_by_cusip", CUSIPResult, "037833100"),
            ("isin", "search_by_isin", ISINResult, "US0378331005"),
        ],
    )
    def test_identifier_searches(
        self,
        fmp_client: FMPDataClient,
        vcr_instance: vcr.VCR,
        search_type: str,
        method: str,
        model: Any,
        test_value: str,
    ):
        """Test searching by different identifiers"""
        with vcr_instance.use_cassette(f"market/search_{search_type}.yaml"):
            search_method = getattr(fmp_client.market, method)
            results = self._handle_rate_limit(search_method, test_value)
            assert isinstance(results, list)
            assert all(isinstance(r, model) for r in results)

    def test_get_all_shares_float(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test getting all companies share float data"""
        with vcr_instance.use_cassette("market/all_shares_float.yaml"):
            all_float_data = self._handle_rate_limit(
                fmp_client.market.get_all_shares_float
            )
            assert isinstance(all_float_data, list)
            assert len(all_float_data) > 0
            assert all(isinstance(d, ShareFloat) for d in all_float_data)
