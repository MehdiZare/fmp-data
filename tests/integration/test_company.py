# tests/integration/test_company.py
import logging
import time
from typing import Any

import pytest
import tenacity

from fmp_data import FMPDataClient
from fmp_data.company.models import (
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
    ISINResult,
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

    def test_get_profile(self, fmp_client: FMPDataClient, vcr_instance, test_symbol):
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
        self, fmp_client: FMPDataClient, vcr_instance, test_symbol
    ):
        """Test getting core company information"""
        with vcr_instance.use_cassette("company/core_information.yaml"):
            info = fmp_client.company.get_core_information(test_symbol)
            # Check first item since API returns a list
            assert isinstance(info[0], CompanyCoreInformation)
            assert info[0].symbol == test_symbol

    def test_search(self, fmp_client: FMPDataClient, vcr_instance):
        # Add retry mechanism or rate limit handling
        with vcr_instance.use_cassette("company/search.yaml"):
            with tenacity.retry(wait=tenacity.wait_exponential()):
                # Test basic search
                results = fmp_client.company.search("Apple", limit=5)
                assert isinstance(results, list)
                assert len(results) <= 5
                assert all(isinstance(r, CompanySearchResult) for r in results)

                # Test with exchange filter (using exchangeShortName)
                nasdaq_results = fmp_client.company.search("Apple", exchange="NASDAQ")
                assert any(r.exchange_short_name == "NASDAQ" for r in nasdaq_results)

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
        self, fmp_client: FMPDataClient, vcr_instance, test_symbol
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
        self, fmp_client: FMPDataClient, vcr_instance, test_symbol
    ):
        """Test getting company notes"""
        with vcr_instance.use_cassette("company/notes.yaml"):
            notes = self._handle_rate_limit(
                fmp_client.company.get_company_notes, test_symbol
            )
            assert isinstance(notes, list)
            if len(notes) > 0:
                assert all(isinstance(n, CompanyNote) for n in notes)

    def test_get_company_logo_url(
        self, fmp_client: FMPDataClient, vcr_instance, test_symbol
    ):
        """Test getting company logo URL"""
        with vcr_instance.use_cassette("company/logo.yaml"):
            url = fmp_client.company.get_company_logo_url(test_symbol)
            assert isinstance(url, str)
            assert url.startswith("http")
            assert url.endswith((".png", ".jpg", ".jpeg"))

    def test_get_stock_list(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting stock list"""
        with vcr_instance.use_cassette("company/stock_list.yaml"):
            stocks = fmp_client.company.get_stock_list()
            assert isinstance(stocks, list)
            assert all(isinstance(s, CompanySymbol) for s in stocks)
            assert len(stocks) > 0

    def test_get_etf_list(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ETF list"""
        with vcr_instance.use_cassette("company/etf_list.yaml"):
            etfs = fmp_client.company.get_etf_list()
            assert isinstance(etfs, list)
            assert all(isinstance(e, CompanySymbol) for e in etfs)
            assert len(etfs) > 0

    def test_get_available_indexes(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting available indexes"""
        with vcr_instance.use_cassette("company/indexes.yaml"):
            indexes = fmp_client.company.get_available_indexes()
            assert isinstance(indexes, list)
            assert all(isinstance(i, str) for i in indexes)
            assert "^GSPC" in indexes  # S&P 500

    def test_get_exchange_symbols(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting exchange symbols"""
        with vcr_instance.use_cassette("company/exchange_symbols.yaml"):
            symbols = fmp_client.company.get_exchange_symbols("NASDAQ")
            assert isinstance(symbols, list)
            assert all(isinstance(s, ExchangeSymbol) for s in symbols)
            assert len(symbols) > 0

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
        vcr_instance,
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

    def test_rate_limiting(self, fmp_client: FMPDataClient, vcr_instance):
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

    def test_error_handling(self, fmp_client: FMPDataClient, vcr_instance):
        """Test error handling"""
        with vcr_instance.use_cassette("company/error_invalid_symbol.yaml"):
            with pytest.raises(FMPError) as exc_info:  # Use specific exception
                fmp_client.company.get_profile("INVALID-SYMBOL")
            assert "not found" in str(exc_info.value).lower()
