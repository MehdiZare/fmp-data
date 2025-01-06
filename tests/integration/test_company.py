# tests/integration/test_company.py
import logging
import time
from datetime import date, datetime

import pytest
import vcr

from fmp_data import FMPDataClient
from fmp_data.company.models import (
    AnalystEstimate,
    AnalystRecommendation,
    CompanyCoreInformation,
    CompanyExecutive,
    CompanyNote,
    CompanyProfile,
    EmployeeCount,
    ExecutiveCompensation,
    GeographicRevenueSegment,
    HistoricalData,
    HistoricalShareFloat,
    IntradayPrice,
    PriceTarget,
    PriceTargetConsensus,
    PriceTargetSummary,
    ProductRevenueSegment,
    Quote,
    SimpleQuote,
    SymbolChange,
    UpgradeDowngrade,
    UpgradeDowngradeConsensus,
)
from fmp_data.exceptions import FMPError
from fmp_data.models import MarketCapitalization, ShareFloat

from .base import BaseTestCase

logger = logging.getLogger(__name__)


class TestCompanyEndpoints(BaseTestCase):
    """Test company endpoints"""

    def test_get_quote(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting real-time stock quote"""
        with vcr_instance.use_cassette("market/quote.yaml"):
            quote = self._handle_rate_limit(fmp_client.company.get_quote, "AAPL")

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
            quote = self._handle_rate_limit(fmp_client.company.get_simple_quote, "AAPL")

            assert isinstance(quote, SimpleQuote)
            assert quote.symbol == "AAPL"
            assert isinstance(quote.price, float)
            assert isinstance(quote.volume, int)

    def test_get_historical_prices(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical price data"""
        with vcr_instance.use_cassette("market/historical_prices.yaml"):
            prices = self._handle_rate_limit(
                fmp_client.company.get_historical_prices,
                "AAPL",
                from_date="2023-01-01",
                to_date="2023-01-31",
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
            prices = self._handle_rate_limit(
                fmp_client.company.get_intraday_prices, "AAPL", interval="5min"
            )

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

    def test_get_market_cap(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting market capitalization data"""
        with vcr_instance.use_cassette("market/market_cap.yaml"):
            cap = self._handle_rate_limit(fmp_client.company.get_market_cap, "AAPL")

            assert isinstance(cap, MarketCapitalization)
            assert cap.symbol == "AAPL"
            assert isinstance(cap.date, datetime)
            assert isinstance(cap.market_cap, float)
            assert cap.market_cap > 0

    def test_get_historical_market_cap(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical market capitalization data"""
        with vcr_instance.use_cassette("market/historical_market_cap.yaml"):
            caps = self._handle_rate_limit(
                fmp_client.company.get_historical_market_cap, "AAPL"
            )

            assert isinstance(caps, list)
            assert len(caps) > 0

            for cap in caps:
                assert isinstance(cap, MarketCapitalization)
                assert cap.symbol == "AAPL"
                assert isinstance(cap.date, datetime)
                assert isinstance(cap.market_cap, float)
                assert cap.market_cap > 0

    def test_get_profile(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR, test_symbol
    ):
        """Test getting company profile"""
        logger.info(f"Testing profile for symbol: {test_symbol}")

        cassette_path = "company/profile.yaml"
        with vcr_instance.use_cassette(cassette_path):
            try:
                profile = self._handle_rate_limit(
                    fmp_client.company.get_profile, test_symbol
                )
                logger.info(f"Got profile response: {profile.symbol}")

                assert isinstance(profile, CompanyProfile)
                assert profile.symbol == test_symbol

            except Exception as e:
                logger.error(f"Request failed: {str(e)}")
                # Print the actual request details
                if hasattr(e, "request"):
                    logger.error(f"Request URL: {e.request.url}")
                    logger.error(f"Request headers: {e.request.headers}")
                raise

    def test_get_core_information(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR, test_symbol
    ):
        """Test getting core company information"""
        with vcr_instance.use_cassette("company/core_information.yaml"):
            info = self._handle_rate_limit(
                fmp_client.company.get_core_information, test_symbol
            )
            assert isinstance(info, CompanyCoreInformation)
            assert info.symbol == test_symbol

    def test_get_executives(self, fmp_client: FMPDataClient, vcr_instance, test_symbol):
        """Test getting company executives"""
        with vcr_instance.use_cassette("company/executives.yaml"):
            executives = self._handle_rate_limit(
                fmp_client.company.get_executives, test_symbol
            )
            assert isinstance(executives, list)
            assert len(executives) > 0
            assert all(isinstance(e, CompanyExecutive) for e in executives)
            # Look for CEO with correct title from API
            assert any(
                e.title == "Chief Executive Officer & Director" for e in executives
            )

    def test_get_employee_count(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR, test_symbol
    ):
        """Test getting employee count history"""
        with vcr_instance.use_cassette("company/employee_count.yaml"):
            counts = self._handle_rate_limit(
                fmp_client.company.get_employee_count, test_symbol
            )
            assert isinstance(counts, list)
            if len(counts) > 0:
                assert all(isinstance(c, EmployeeCount) for c in counts)

    def test_get_company_notes(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR, test_symbol
    ):
        """Test getting company notes"""
        with vcr_instance.use_cassette("company/notes.yaml"):
            notes = self._handle_rate_limit(
                fmp_client.company.get_company_notes, test_symbol
            )
            assert isinstance(notes, list)
            if len(notes) > 0:
                assert all(isinstance(n, CompanyNote) for n in notes)

    def test_get_company_logo_url(self, fmp_client: FMPDataClient, test_symbol: str):
        """Test getting company logo URL"""
        url = self._handle_rate_limit(
            fmp_client.company.get_company_logo_url, test_symbol
        )

        # Check URL format
        assert isinstance(url, str)
        assert url == f"https://financialmodelingprep.com/image-stock/{test_symbol}.png"

        # Verify URL components
        from urllib.parse import urlparse

        parsed_url = urlparse(url)
        assert parsed_url.scheme == "https"
        assert parsed_url.netloc == "financialmodelingprep.com"
        assert parsed_url.path.startswith("/image-stock/")
        assert parsed_url.path.endswith(".png")
        assert test_symbol in parsed_url.path

        # Verify no API-related parameters
        assert "apikey" not in url
        assert "api" not in url

        # Test error case
        with pytest.raises(ValueError):
            fmp_client.company.get_company_logo_url("")

    def test_rate_limiting(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test rate limiting handling"""
        with vcr_instance.use_cassette("company/rate_limit.yaml"):
            symbols = ["AAPL", "MSFT", "GOOGL"]
            results = []

            for symbol in symbols:
                profile = self._handle_rate_limit(
                    fmp_client.company.get_profile, symbol
                )
                results.append(profile)
                time.sleep(0.5)  # Add delay between requests

            assert len(results) == len(symbols)
            assert all(isinstance(r, CompanyProfile) for r in results)

    def test_error_handling(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test error handling"""
        with vcr_instance.use_cassette("company/error_invalid_symbol.yaml"):
            with pytest.raises(FMPError) as exc_info:  # Use specific exception
                fmp_client.company.get_profile("INVALID-SYMBOL")
            assert "not found" in str(exc_info.value).lower()

    # tests/integration/test_company.py - Add to existing TestCompanyEndpoints class

    def test_get_executive_compensation(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR, test_symbol: str
    ):
        """Test getting executive compensation data"""
        with vcr_instance.use_cassette("company/executive_compensation.yaml"):
            compensation = self._handle_rate_limit(
                fmp_client.company.get_executive_compensation, test_symbol
            )
            assert isinstance(compensation, list)
            if len(compensation) > 0:
                assert all(isinstance(c, ExecutiveCompensation) for c in compensation)
                for comp in compensation:
                    assert comp.symbol == test_symbol
                    assert isinstance(comp.name_and_position, str)
                    assert isinstance(comp.company_name, str)
                    assert isinstance(comp.salary, float)
                    assert isinstance(comp.filing_date, date)

    def test_get_share_float(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR, test_symbol: str
    ):
        """Test getting current share float data"""
        with vcr_instance.use_cassette("company/share_float.yaml"):
            float_data = self._handle_rate_limit(
                fmp_client.company.get_share_float, test_symbol
            )
            assert isinstance(float_data, ShareFloat)
            assert float_data.symbol == test_symbol
            assert isinstance(float_data.float_shares, float)
            assert isinstance(float_data.outstanding_shares, float)
            assert isinstance(float_data.date, datetime)

    def test_get_historical_share_float(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR, test_symbol: str
    ):
        """Test getting historical share float data"""
        with vcr_instance.use_cassette("company/historical_share_float.yaml"):
            historical_data = self._handle_rate_limit(
                fmp_client.company.get_historical_share_float, test_symbol
            )
            assert isinstance(historical_data, list)
            if len(historical_data) > 0:
                assert all(isinstance(d, HistoricalShareFloat) for d in historical_data)
                # Check first entry in detail
                first_entry = historical_data[0]
                assert first_entry.symbol == test_symbol
                assert isinstance(first_entry.float_shares, float)
                assert isinstance(first_entry.outstanding_shares, float)
                assert isinstance(first_entry.date, datetime)

    def test_get_product_revenue_segmentation(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR, test_symbol: str
    ):
        """Test getting product revenue segmentation data"""
        with vcr_instance.use_cassette("company/product_revenue_segmentation.yaml"):
            segment_data = self._handle_rate_limit(
                fmp_client.company.get_product_revenue_segmentation, test_symbol
            )
            assert isinstance(segment_data, list)
            if len(segment_data) > 0:
                assert all(isinstance(d, ProductRevenueSegment) for d in segment_data)
                first_entry = segment_data[0]
                assert isinstance(first_entry.date, str)
                assert isinstance(first_entry.segments, dict)
                if len(first_entry.segments) > 0:
                    first_segment_name = next(iter(first_entry.segments))
                    assert isinstance(
                        first_entry.segments.get(first_segment_name), float
                    )

    def test_get_geographic_revenue_segmentation(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR, test_symbol: str
    ):
        """Test getting geographic revenue segmentation data"""
        with vcr_instance.use_cassette("company/geographic_revenue_segmentation.yaml"):
            geo_data = self._handle_rate_limit(
                fmp_client.company.get_geographic_revenue_segmentation, test_symbol
            )
            assert isinstance(geo_data, list)
            if len(geo_data) > 0:
                assert all(isinstance(d, GeographicRevenueSegment) for d in geo_data)
                first_entry = geo_data[0]
                assert isinstance(first_entry.segments, dict)
                if len(first_entry.segments) > 0:
                    one_segment_key = next(iter(first_entry.segments))
                    assert isinstance(first_entry.segments.get(one_segment_key), float)

    def test_get_symbol_changes(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test getting symbol change history"""
        with vcr_instance.use_cassette("company/symbol_changes.yaml"):
            changes = self._handle_rate_limit(fmp_client.company.get_symbol_changes)
            assert isinstance(changes, list)
            if len(changes) > 0:
                assert all(isinstance(c, SymbolChange) for c in changes)
                first_change = changes[0]
                assert isinstance(first_change.old_symbol, str)
                assert isinstance(first_change.new_symbol, str)
                assert isinstance(first_change.change_date, date)
                assert isinstance(first_change.name, str)

    def test_get_price_target(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting price targets"""
        with vcr_instance.use_cassette("intelligence/price_target.yaml"):
            targets = self._handle_rate_limit(
                fmp_client.company.get_price_target, "AAPL"
            )

            assert isinstance(targets, list)
            assert len(targets) > 0

            for target in targets:
                assert isinstance(target, PriceTarget)
                assert isinstance(target.published_date, datetime)
                assert isinstance(target.price_target, float)
                assert target.symbol == "AAPL"
                assert isinstance(target.adj_price_target, float)
                assert isinstance(target.price_when_posted, float)

    def test_get_price_target_summary(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting price target summary"""
        with vcr_instance.use_cassette("company/price_target_summary.yaml"):
            summary = self._handle_rate_limit(
                fmp_client.company.get_price_target_summary, "AAPL"
            )

            assert isinstance(summary, PriceTargetSummary)
            assert summary.symbol == "AAPL"
            assert isinstance(summary.last_month, int)
            assert isinstance(summary.last_month_avg_price_target, float)
            assert isinstance(summary.last_quarter_avg_price_target, float)
            assert isinstance(summary.last_year, int)
            assert isinstance(summary.all_time_avg_price_target, float)

    def test_get_price_target_consensus(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting price target consensus"""
        with vcr_instance.use_cassette("intelligence/price_target_consensus.yaml"):
            consensus = fmp_client.company.get_price_target_consensus("AAPL")

            assert isinstance(consensus, PriceTargetConsensus)
            assert consensus.symbol == "AAPL"
            assert isinstance(consensus.target_consensus, float)
            assert isinstance(consensus.target_high, float)
            assert isinstance(consensus.target_low, float)

    def test_get_analyst_estimates(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting analyst estimates"""
        with vcr_instance.use_cassette("intelligence/analyst_estimates.yaml"):
            estimates = self._handle_rate_limit(
                fmp_client.company.get_analyst_estimates, "AAPL"
            )

            assert isinstance(estimates, list)
            assert len(estimates) > 0

            for estimate in estimates:
                assert isinstance(estimate, AnalystEstimate)
                assert isinstance(estimate.date, datetime)
                assert isinstance(estimate.estimated_revenue_high, float)
                assert estimate.symbol == "AAPL"
                assert isinstance(estimate.estimated_ebitda_avg, float)
                assert isinstance(estimate.number_analyst_estimated_revenue, int)

    def test_get_analyst_recommendations(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting analyst recommendations"""
        with vcr_instance.use_cassette("intelligence/analyst_recommendations.yaml"):
            recommendations = self._handle_rate_limit(
                fmp_client.company.get_analyst_recommendations, "AAPL"
            )

            assert isinstance(recommendations, list)
            assert len(recommendations) > 0

            for rec in recommendations:
                assert isinstance(rec, AnalystRecommendation)
                assert isinstance(rec.date, datetime)
                assert rec.symbol == "AAPL"
                assert isinstance(rec.analyst_ratings_buy, int)
                assert isinstance(rec.analyst_ratings_strong_sell, int)

    def test_get_upgrades_downgrades(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting upgrades and downgrades"""
        with vcr_instance.use_cassette("intelligence/upgrades_downgrades.yaml"):
            changes = self._handle_rate_limit(
                fmp_client.company.get_upgrades_downgrades, "AAPL"
            )

            assert isinstance(changes, list)
            assert len(changes) > 0

            for change in changes:
                assert isinstance(change, UpgradeDowngrade)
                assert isinstance(change.published_date, datetime)
                assert change.symbol == "AAPL"
                assert isinstance(change.action, str)
                assert (
                    isinstance(change.previous_grade, str)
                    if change.previous_grade is not None
                    else True
                )
                assert isinstance(change.new_grade, str)

    def test_get_upgrades_downgrades_consensus(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting upgrades/downgrades consensus"""
        with vcr_instance.use_cassette(
            "intelligence/upgrades_downgrades_consensus.yaml"
        ):
            consensus = self._handle_rate_limit(
                fmp_client.company.get_upgrades_downgrades_consensus, "AAPL"
            )

            assert isinstance(consensus, UpgradeDowngradeConsensus)
            assert consensus.symbol == "AAPL"
            assert isinstance(consensus.strong_buy, int)
            assert isinstance(consensus.buy, int)
            assert isinstance(consensus.hold, int)
            assert isinstance(consensus.sell, int)
            assert isinstance(consensus.strong_sell, int)
