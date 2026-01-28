# tests/integration/test_company.py
from datetime import date, datetime
import logging
import time

import pytest
import vcr

from fmp_data import FMPDataClient
from fmp_data.company.models import (
    AnalystEstimate,
    AnalystRecommendation,
    CompanyCoreInformation,
    CompanyExecutive,
    CompanyNote,
    CompanyPeer,
    CompanyProfile,
    EmployeeCount,
    ExecutiveCompensation,
    ExecutiveCompensationBenchmark,
    GeographicRevenueSegment,
    HistoricalData,
    HistoricalShareFloat,
    IntradayPrice,
    MergerAcquisition,
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
from fmp_data.exceptions import FMPError, InvalidSymbolError
from fmp_data.fundamental.models import (
    AsReportedBalanceSheet,
    AsReportedCashFlowStatement,
    AsReportedIncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    EnterpriseValue,
    FinancialGrowth,
    FinancialRatiosTTM,
    FinancialScore,
    IncomeStatement,
    KeyMetricsTTM,
)
from fmp_data.intelligence.models import DividendEvent, EarningEvent, StockSplitEvent
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
                from_date=date(2023, 1, 1),
                to_date=date(2023, 1, 31),
            )

            assert isinstance(prices, HistoricalData)

            # Validate successful response (not empty from 404)
            assert len(prices.historical) > 0, (
                "Expected historical price data but got empty list. "
                "This may indicate a 404 - check the VCR cassette for status code."
            )

            for price in prices.historical:
                assert isinstance(price.date, datetime)
                assert isinstance(price.open, float)
                assert isinstance(price.high, float)
                assert isinstance(price.low, float)
                assert isinstance(price.close, float)
                assert isinstance(price.volume, int)
                # Note: /full endpoint returns open/high/low/close/volume but may
                # omit adj_close
                # Only check adj_close if present
                if price.adj_close is not None:
                    assert isinstance(price.adj_close, float)

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
                logger.error(f"Request failed: {e!s}")
                # Print the actual request details if available (with redaction)
                request = getattr(e, "request", None)
                if request:
                    # Redact sensitive data from URL (remove query params)
                    from urllib.parse import urlparse

                    parsed = urlparse(str(request.url))
                    safe_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    logger.error(f"Request URL: {safe_url} [query params redacted]")

                    # Redact sensitive headers
                    sensitive_keys = {"authorization", "api", "key", "token", "secret"}
                    safe_headers = {}
                    for key, value in dict(request.headers).items():
                        key_lower = key.lower()
                        if any(sensitive in key_lower for sensitive in sensitive_keys):
                            safe_headers[key] = "[REDACTED]"
                        else:
                            safe_headers[key] = value
                    logger.error(f"Request headers: {safe_headers}")
                raise

    def test_get_core_information(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR, test_symbol
    ):
        """Test getting core company information"""
        with vcr_instance.use_cassette("company/core_information.yaml"):
            info = self._handle_rate_limit(
                fmp_client.company.get_core_information, test_symbol
            )
            if info is not None:
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
        base_url = fmp_client.config.base_url.rstrip("/")
        assert url == f"{base_url}/image-stock/{test_symbol}.png"

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
        with pytest.raises(InvalidSymbolError):
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
            if targets:
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
                fmp_client.company.get_analyst_estimates,
                "AAPL",
                period="annual",
                page=0,
                limit=10,
            )

            assert isinstance(estimates, list)
            if estimates:
                for estimate in estimates:
                    assert isinstance(estimate, AnalystEstimate)
                    assert isinstance(estimate.date, datetime)
                    if estimate.estimated_revenue_high is not None:
                        assert isinstance(estimate.estimated_revenue_high, float)
                    assert estimate.symbol == "AAPL"
                    if estimate.estimated_ebitda_avg is not None:
                        assert isinstance(estimate.estimated_ebitda_avg, float)
                    if estimate.number_analyst_estimated_revenue is not None:
                        assert isinstance(
                            estimate.number_analyst_estimated_revenue, int
                        )

    def test_get_analyst_recommendations(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting analyst recommendations"""
        with vcr_instance.use_cassette("intelligence/analyst_recommendations.yaml"):
            recommendations = self._handle_rate_limit(
                fmp_client.company.get_analyst_recommendations, "AAPL"
            )

            assert isinstance(recommendations, list)
            if recommendations:
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
            if changes:
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

            if consensus is not None:
                assert isinstance(consensus, UpgradeDowngradeConsensus)
                assert consensus.symbol == "AAPL"
                assert isinstance(consensus.strong_buy, int)
                assert isinstance(consensus.buy, int)
                assert isinstance(consensus.hold, int)
                assert isinstance(consensus.sell, int)
                assert isinstance(consensus.strong_sell, int)


class TestCompanyAdditionalEndpoints(BaseTestCase):
    """Additional company endpoints coverage"""

    TEST_SYMBOL = "AAPL"

    @pytest.mark.parametrize(
        "method_name,cassette,kwargs,expected_type",
        [
            ("get_company_peers", "company/peers.yaml", {}, CompanyPeer),
            (
                "get_dividends",
                "company/dividends.yaml",
                {"from_date": date(2023, 1, 1), "to_date": date(2023, 12, 31)},
                DividendEvent,
            ),
            ("get_earnings", "company/earnings.yaml", {"limit": 5}, EarningEvent),
            (
                "get_stock_splits",
                "company/stock_splits.yaml",
                {"from_date": date(2020, 1, 1), "to_date": date(2023, 12, 31)},
                StockSplitEvent,
            ),
            (
                "get_income_statement_ttm",
                "company/income_statement_ttm.yaml",
                {},
                IncomeStatement,
            ),
            (
                "get_balance_sheet_ttm",
                "company/balance_sheet_ttm.yaml",
                {},
                BalanceSheet,
            ),
            (
                "get_cash_flow_ttm",
                "company/cash_flow_ttm.yaml",
                {},
                CashFlowStatement,
            ),
            (
                "get_key_metrics_ttm",
                "company/key_metrics_ttm.yaml",
                {},
                KeyMetricsTTM,
            ),
            (
                "get_financial_ratios_ttm",
                "company/financial_ratios_ttm.yaml",
                {},
                FinancialRatiosTTM,
            ),
            (
                "get_financial_scores",
                "company/financial_scores.yaml",
                {},
                FinancialScore,
            ),
            (
                "get_enterprise_values",
                "company/enterprise_values.yaml",
                {"period": "annual", "limit": 5},
                EnterpriseValue,
            ),
            (
                "get_income_statement_growth",
                "company/income_statement_growth.yaml",
                {"period": "annual", "limit": 5},
                FinancialGrowth,
            ),
            (
                "get_balance_sheet_growth",
                "company/balance_sheet_growth.yaml",
                {"period": "annual", "limit": 5},
                FinancialGrowth,
            ),
            (
                "get_cash_flow_growth",
                "company/cash_flow_growth.yaml",
                {"period": "annual", "limit": 5},
                FinancialGrowth,
            ),
            (
                "get_financial_growth",
                "company/financial_growth.yaml",
                {"period": "annual", "limit": 5},
                FinancialGrowth,
            ),
            (
                "get_income_statement_as_reported",
                "company/income_statement_as_reported.yaml",
                {"period": "annual", "limit": 2},
                AsReportedIncomeStatement,
            ),
            (
                "get_balance_sheet_as_reported",
                "company/balance_sheet_as_reported.yaml",
                {"period": "annual", "limit": 2},
                AsReportedBalanceSheet,
            ),
            (
                "get_cash_flow_as_reported",
                "company/cash_flow_as_reported.yaml",
                {"period": "annual", "limit": 2},
                AsReportedCashFlowStatement,
            ),
        ],
    )
    def test_company_symbol_list_endpoints(
        self,
        fmp_client: FMPDataClient,
        vcr_instance,
        method_name: str,
        cassette: str,
        kwargs: dict,
        expected_type: type,
    ):
        """Test company endpoints returning lists for a symbol"""
        with vcr_instance.use_cassette(cassette):
            method = getattr(fmp_client.company, method_name)
            results = self._handle_rate_limit(method, self.TEST_SYMBOL, **kwargs)
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], expected_type)

    def test_get_executive_compensation_benchmark(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting executive compensation benchmark"""
        with vcr_instance.use_cassette("company/executive_compensation_benchmark.yaml"):
            results = self._handle_rate_limit(
                fmp_client.company.get_executive_compensation_benchmark, 2023
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], ExecutiveCompensationBenchmark)

    def test_get_mergers_acquisitions_latest(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting latest mergers and acquisitions"""
        with vcr_instance.use_cassette("company/mergers_acquisitions_latest.yaml"):
            results = self._handle_rate_limit(
                fmp_client.company.get_mergers_acquisitions_latest, page=0, limit=5
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], MergerAcquisition)

    def test_get_mergers_acquisitions_search(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test searching mergers and acquisitions"""
        with vcr_instance.use_cassette("company/mergers_acquisitions_search.yaml"):
            results = self._handle_rate_limit(
                fmp_client.company.get_mergers_acquisitions_search,
                "Apple",
                page=0,
                limit=5,
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], MergerAcquisition)

    @pytest.mark.parametrize(
        "method_name,cassette",
        [
            ("get_historical_prices_light", "company/historical_prices_light.yaml"),
            (
                "get_historical_prices_non_split_adjusted",
                "company/historical_prices_non_split_adjusted.yaml",
            ),
            (
                "get_historical_prices_dividend_adjusted",
                "company/historical_prices_dividend_adjusted.yaml",
            ),
        ],
    )
    def test_historical_price_variants(
        self,
        fmp_client: FMPDataClient,
        vcr_instance,
        method_name: str,
        cassette: str,
    ):
        """Test historical price variants"""
        with vcr_instance.use_cassette(cassette):
            method = getattr(fmp_client.company, method_name)
            data = self._handle_rate_limit(
                method,
                self.TEST_SYMBOL,
                from_date=date(2023, 1, 1),
                to_date=date(2023, 2, 1),
            )
            assert isinstance(data, HistoricalData)
            assert isinstance(data.historical, list)

            # Validate non-empty response
            assert len(data.historical) > 0, (
                f"{method_name}: Expected price data but got empty list. "
                "Check VCR cassette for 404 status."
            )

    def test_get_financial_reports_json(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting financial reports JSON"""
        with vcr_instance.use_cassette("company/financial_reports_json.yaml"):
            report = self._handle_rate_limit(
                fmp_client.company.get_financial_reports_json,
                self.TEST_SYMBOL,
                year=2023,
                period="FY",
            )
            assert isinstance(report, dict)

    def test_get_financial_reports_xlsx(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting financial reports XLSX"""
        with vcr_instance.use_cassette("company/financial_reports_xlsx.yaml"):
            report = self._handle_rate_limit(
                fmp_client.company.get_financial_reports_xlsx,
                self.TEST_SYMBOL,
                year=2023,
                period="FY",
            )
            assert isinstance(report, bytes)
            assert len(report) > 0
