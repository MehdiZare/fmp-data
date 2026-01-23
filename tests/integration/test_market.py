from datetime import date, datetime
from typing import Any

import pytest
import tenacity
import vcr

from fmp_data import FMPDataClient
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
            assert hours.exchange
            assert hours.name
            assert hours.opening_hour
            assert hours.closing_hour
            assert hours.timezone
            assert isinstance(hours.is_market_open, bool)

    def test_get_all_exchange_market_hours(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting market hours for all exchanges"""
        with vcr_instance.use_cassette("market/all_exchange_market_hours.yaml"):
            hours = self._handle_rate_limit(
                fmp_client.market.get_all_exchange_market_hours,
            )
            assert isinstance(hours, list)
            assert len(hours) > 0
            assert isinstance(hours[0], MarketHours)
            assert hours[0].exchange
            assert hours[0].opening_hour
            assert hours[0].closing_hour

    def test_get_holidays_by_exchange(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting market holidays for an exchange"""
        with vcr_instance.use_cassette("market/holidays_by_exchange.yaml"):
            holidays = self._handle_rate_limit(
                fmp_client.market.get_holidays_by_exchange,
                "NYSE",
            )
            assert isinstance(holidays, list)
            if holidays:
                assert isinstance(holidays[0], MarketHoliday)
                assert holidays[0].exchange
                assert holidays[0].holiday or holidays[0].date

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
            sectors = self._handle_rate_limit(
                fmp_client.market.get_sector_performance,
                date=date(2024, 2, 1),
                exchange="NASDAQ",
            )

            assert isinstance(sectors, list)
            assert len(sectors) > 0

            for sector in sectors:
                assert isinstance(sector, SectorPerformance)
                assert isinstance(sector.change_percentage, float)

    def test_get_industry_performance_snapshot(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting industry performance snapshot data"""
        with vcr_instance.use_cassette("market/industry_performance_snapshot.yaml"):
            industries = self._handle_rate_limit(
                fmp_client.market.get_industry_performance_snapshot,
                date=date(2024, 2, 1),
                industry="Biotechnology",
                exchange="NASDAQ",
            )

            assert isinstance(industries, list)
            assert len(industries) > 0

            for industry in industries:
                assert isinstance(industry, IndustryPerformance)
                assert isinstance(industry.change_percentage, float)

    def test_get_historical_sector_performance(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting historical sector performance data"""
        with vcr_instance.use_cassette("market/historical_sector_performance.yaml"):
            sectors = self._handle_rate_limit(
                fmp_client.market.get_historical_sector_performance,
                sector="Energy",
                from_date=date(2024, 2, 1),
                to_date=date(2024, 3, 1),
                exchange="NASDAQ",
            )

            assert isinstance(sectors, list)
            assert len(sectors) > 0

            for sector in sectors:
                assert isinstance(sector, SectorPerformance)
                assert isinstance(sector.change_percentage, float)

    def test_get_historical_industry_performance(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting historical industry performance data"""
        with vcr_instance.use_cassette("market/historical_industry_performance.yaml"):
            industries = self._handle_rate_limit(
                fmp_client.market.get_historical_industry_performance,
                industry="Biotechnology",
                from_date=date(2024, 2, 1),
                to_date=date(2024, 3, 1),
                exchange="NASDAQ",
            )

            assert isinstance(industries, list)
            assert len(industries) > 0

            for industry in industries:
                assert isinstance(industry, IndustryPerformance)
                assert isinstance(industry.change_percentage, float)

    def test_get_sector_pe_snapshot(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting sector PE snapshot data"""
        with vcr_instance.use_cassette("market/sector_pe_snapshot.yaml"):
            sectors = self._handle_rate_limit(
                fmp_client.market.get_sector_pe_snapshot,
                date=date(2024, 2, 1),
                sector="Energy",
                exchange="NASDAQ",
            )

            assert isinstance(sectors, list)
            assert len(sectors) > 0

            for sector in sectors:
                assert isinstance(sector, SectorPESnapshot)
                assert isinstance(sector.pe, float)

    def test_get_industry_pe_snapshot(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting industry PE snapshot data"""
        with vcr_instance.use_cassette("market/industry_pe_snapshot.yaml"):
            industries = self._handle_rate_limit(
                fmp_client.market.get_industry_pe_snapshot,
                date=date(2024, 2, 1),
                industry="Biotechnology",
                exchange="NASDAQ",
            )

            assert isinstance(industries, list)
            assert len(industries) > 0

            for industry in industries:
                assert isinstance(industry, IndustryPESnapshot)
                assert isinstance(industry.pe, float)

    def test_get_historical_sector_pe(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical sector PE data"""
        with vcr_instance.use_cassette("market/historical_sector_pe.yaml"):
            sectors = self._handle_rate_limit(
                fmp_client.market.get_historical_sector_pe,
                sector="Energy",
                from_date=date(2024, 2, 1),
                to_date=date(2024, 3, 1),
                exchange="NASDAQ",
            )

            assert isinstance(sectors, list)
            assert len(sectors) > 0

            for sector in sectors:
                assert isinstance(sector, SectorPESnapshot)
                assert isinstance(sector.pe, float)

    def test_get_historical_industry_pe(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical industry PE data"""
        with vcr_instance.use_cassette("market/historical_industry_pe.yaml"):
            industries = self._handle_rate_limit(
                fmp_client.market.get_historical_industry_pe,
                industry="Biotechnology",
                from_date=date(2024, 2, 1),
                to_date=date(2024, 3, 1),
                exchange="NASDAQ",
            )

            assert isinstance(industries, list)
            assert len(industries) > 0

            for industry in industries:
                assert isinstance(industry, IndustryPESnapshot)
                assert isinstance(industry.pe, float)

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
                fmp_client.market.search_company, "Apple", limit=5
            )
            assert isinstance(results, list)
            assert len(results) <= 5
            assert all(isinstance(r, CompanySearchResult) for r in results)

    def test_search_symbol(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test symbol search"""
        with vcr_instance.use_cassette("market/search_symbol.yaml"):
            results = self._handle_rate_limit(
                fmp_client.market.search_symbol, "Apple", limit=5
            )
            assert isinstance(results, list)
            assert len(results) <= 5
            assert all(isinstance(r, CompanySearchResult) for r in results)

    def test_search_exchange_variants(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test exchange variants search"""
        with vcr_instance.use_cassette("market/search_exchange_variants.yaml"):
            results = self._handle_rate_limit(
                fmp_client.market.search_exchange_variants, "Apple"
            )
            assert isinstance(results, list)
            assert len(results) > 0
            assert all(isinstance(r, CompanySearchResult) for r in results)

    def test_get_stock_list(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test getting stock list"""
        with vcr_instance.use_cassette("market/stock_list.yaml"):
            stocks = self._handle_rate_limit(fmp_client.market.get_stock_list)
            assert isinstance(stocks, list)
            assert len(stocks) > 0
            for stock in stocks:
                assert isinstance(stock, CompanySymbol)
                # Verify symbol attribute exists and is a string
                assert isinstance(stock.symbol, str)

    def test_get_financial_statement_symbol_list(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test getting financial statement symbol list"""
        with vcr_instance.use_cassette("market/financial_statement_symbol_list.yaml"):
            symbols = self._handle_rate_limit(
                fmp_client.market.get_financial_statement_symbol_list
            )
            assert isinstance(symbols, list)
            assert len(symbols) > 0
            assert all(isinstance(symbol, CompanySymbol) for symbol in symbols)

    def test_get_actively_trading_list(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test getting actively trading list"""
        with vcr_instance.use_cassette("market/actively_trading_list.yaml"):
            symbols = self._handle_rate_limit(
                fmp_client.market.get_actively_trading_list
            )
            assert isinstance(symbols, list)
            assert len(symbols) > 0
            assert all(isinstance(symbol, CompanySymbol) for symbol in symbols)

    def test_get_tradable_list(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test getting tradable list"""
        with vcr_instance.use_cassette("market/tradable_list.yaml"):
            symbols = self._handle_rate_limit(
                fmp_client.market.get_tradable_list, limit=5, offset=0
            )
            assert isinstance(symbols, list)
            if symbols:
                assert all(isinstance(symbol, CompanySymbol) for symbol in symbols)

    def test_get_cik_list(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test getting CIK list"""
        with vcr_instance.use_cassette("market/cik_list.yaml"):
            results = self._handle_rate_limit(
                fmp_client.market.get_cik_list, page=0, limit=10
            )
            assert isinstance(results, list)
            assert len(results) > 0
            assert all(isinstance(r, CIKListEntry) for r in results)

    def test_get_company_screener(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test getting company screener results"""
        with vcr_instance.use_cassette("market/company_screener.yaml"):
            results = self._handle_rate_limit(
                fmp_client.market.get_company_screener,
                sector="Technology",
                limit=5,
            )
            assert isinstance(results, list)
            assert len(results) > 0
            assert all(isinstance(r, CompanySearchResult) for r in results)

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

    def test_get_available_exchanges(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test getting available exchanges"""
        with vcr_instance.use_cassette("market/available_exchanges.yaml"):
            exchanges = self._handle_rate_limit(
                fmp_client.market.get_available_exchanges
            )

            assert isinstance(exchanges, list)
            assert len(exchanges) > 0
            assert all(isinstance(e, ExchangeSymbol) for e in exchanges)

    def test_get_available_sectors(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test getting available sectors"""
        with vcr_instance.use_cassette("market/available_sectors.yaml"):
            sectors = self._handle_rate_limit(fmp_client.market.get_available_sectors)
            assert isinstance(sectors, list)
            assert len(sectors) > 0
            assert all(isinstance(s, str) for s in sectors)

    def test_get_available_industries(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test getting available industries"""
        with vcr_instance.use_cassette("market/available_industries.yaml"):
            industries = self._handle_rate_limit(
                fmp_client.market.get_available_industries
            )
            assert isinstance(industries, list)
            assert len(industries) > 0
            assert all(isinstance(i, str) for i in industries)

    def test_get_available_countries(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test getting available countries"""
        with vcr_instance.use_cassette("market/available_countries.yaml"):
            countries = self._handle_rate_limit(
                fmp_client.market.get_available_countries
            )
            assert isinstance(countries, list)
            assert len(countries) > 0
            assert all(isinstance(c, str) for c in countries)

    def test_get_ipo_disclosure(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test getting IPO disclosure data"""
        with vcr_instance.use_cassette("market/ipo_disclosure.yaml"):
            results = self._handle_rate_limit(
                fmp_client.market.get_ipo_disclosure,
                from_date=date(2023, 1, 1),
                to_date=date(2023, 1, 31),
                limit=5,
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], IPODisclosure)

    def test_get_ipo_prospectus(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test getting IPO prospectus data"""
        with vcr_instance.use_cassette("market/ipo_prospectus.yaml"):
            results = self._handle_rate_limit(
                fmp_client.market.get_ipo_prospectus,
                from_date=date(2023, 1, 1),
                to_date=date(2023, 1, 31),
                limit=5,
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], IPOProspectus)

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
