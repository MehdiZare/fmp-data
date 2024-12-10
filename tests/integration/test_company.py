# tests/integration/test_company.py
import logging
import time
import warnings
from datetime import date, datetime
from typing import Any

import pytest
import tenacity
import vcr

from fmp_data import FMPDataClient
from fmp_data.company.models import (
    AvailableIndex,
    CIKResult,
    CompanyCoreInformation,
    CompanyExecutive,
    CompanyNote,
    CompanyProfile,
    CompanySearchResult,
    CompanySymbol,
    CUSIPResult,
    EmployeeCount,
    ExchangeSymbol,
    ExecutiveCompensation,
    GeographicRevenueSegment,
    HistoricalShareFloat,
    ISINResult,
    ProductRevenueSegment,
    ShareFloat,
    SymbolChange,
)
from fmp_data.exceptions import FMPError, RateLimitError

logger = logging.getLogger(__name__)


class TestCompanyEndpoints:
    """Test company endpoints"""

    def _handle_rate_limit(self, func, *args, **kwargs):
        """Helper to handle rate limiting"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(e.retry_after or 1)
                continue

    def test_get_profile(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR, test_symbol
    ):
        """Test getting company profile"""
        logger.info(f"Testing profile for symbol: {test_symbol}")

        cassette_path = "company/profile.yaml"
        with vcr_instance.use_cassette(cassette_path):
            try:
                profile = fmp_client.company.get_profile(test_symbol)
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
            info = fmp_client.company.get_core_information(test_symbol)
            assert isinstance(info, CompanyCoreInformation)
            assert info.symbol == test_symbol

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(3),
    )
    def test_search(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test company search"""
        with vcr_instance.use_cassette("company/search.yaml"):
            results = fmp_client.company.search("Apple", limit=5)
            assert isinstance(results, list)
            assert len(results) <= 5
            assert all(isinstance(r, CompanySearchResult) for r in results)

    def test_get_executives(self, fmp_client: FMPDataClient, vcr_instance, test_symbol):
        """Test getting company executives"""
        with vcr_instance.use_cassette("company/executives.yaml"):
            executives = fmp_client.company.get_executives(test_symbol)
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
        url = fmp_client.company.get_company_logo_url(test_symbol)

        # Check URL format
        assert isinstance(url, str)
        assert url == f"https://financialmodelingprep.com/image-stock/{test_symbol}.png"

        # Verify URL components
        assert url.startswith("https://financialmodelingprep.com")
        assert "/image-stock/" in url
        assert url.endswith(".png")
        assert test_symbol in url

        # Verify no API-related parameters
        assert "apikey" not in url
        assert "api" not in url

        # Test error case
        with pytest.raises(ValueError):
            fmp_client.company.get_company_logo_url("")

    def test_get_stock_list(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test getting stock list"""
        with vcr_instance.use_cassette("company/stock_list.yaml"):
            stocks = fmp_client.company.get_stock_list()
            assert isinstance(stocks, list)
            assert len(stocks) > 0
            for stock in stocks:
                assert isinstance(stock, CompanySymbol)
                assert hasattr(stock, "symbol")  # Only check required field
                assert isinstance(stock.symbol, str)

    def test_get_etf_list(self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR):
        """Test getting ETF list"""
        with vcr_instance.use_cassette("company/etf_list.yaml"):
            etfs = fmp_client.company.get_etf_list()
            assert isinstance(etfs, list)
            assert all(isinstance(e, CompanySymbol) for e in etfs)
            assert len(etfs) > 0

    def test_get_available_indexes(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test getting available indexes"""
        with vcr_instance.use_cassette("company/indexes.yaml"):
            indexes = fmp_client.company.get_available_indexes()
            assert isinstance(indexes, list)
            assert all(isinstance(i, AvailableIndex) for i in indexes)
            assert any(i.symbol == "^GSPC" for i in indexes)

    def test_get_exchange_symbols(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test getting exchange symbols"""
        with vcr_instance.use_cassette("company/exchange_symbols.yaml"):
            # Capture warnings during test
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")

                symbols = fmp_client.company.get_exchange_symbols("NASDAQ")

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
        with vcr_instance.use_cassette(f"company/search_{search_type}.yaml"):
            search_method = getattr(fmp_client.company, method)
            results = self._handle_rate_limit(search_method, test_value)
            assert isinstance(results, list)
            assert all(isinstance(r, model) for r in results)

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

    def test_get_all_shares_float(
        self, fmp_client: FMPDataClient, vcr_instance: vcr.VCR
    ):
        """Test getting all companies share float data"""
        with vcr_instance.use_cassette("company/all_shares_float.yaml"):
            all_float_data = self._handle_rate_limit(
                fmp_client.company.get_all_shares_float
            )
            assert isinstance(all_float_data, list)
            assert len(all_float_data) > 0
            assert all(isinstance(d, ShareFloat) for d in all_float_data)

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
