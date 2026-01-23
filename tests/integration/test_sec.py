# tests/integration/test_sec.py
from datetime import date

from fmp_data import FMPDataClient
from fmp_data.sec.models import (
    IndustryClassification,
    SECCompanySearchResult,
    SECFiling8K,
    SECFilingSearchResult,
    SECFinancialFiling,
    SECProfile,
    SICCode,
)
from tests.integration.base import BaseTestCase


class TestSECClientEndpoints(BaseTestCase):
    """Integration tests for SECClient endpoints using VCR"""

    def test_get_latest_8k(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting latest 8-K filings"""
        with vcr_instance.use_cassette("sec/latest_8k.yaml"):
            filings = self._handle_rate_limit(
                fmp_client.sec.get_latest_8k,
                page=0,
                limit=5,
                from_date=date(2024, 1, 1),
                to_date=date(2024, 3, 1),
            )
            assert isinstance(filings, list)
            if filings:
                assert isinstance(filings[0], SECFiling8K)

    def test_get_latest_financials(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting latest financial filings"""
        with vcr_instance.use_cassette("sec/latest_financials.yaml"):
            filings = self._handle_rate_limit(
                fmp_client.sec.get_latest_financials,
                page=0,
                limit=5,
                from_date=date(2024, 1, 1),
                to_date=date(2024, 3, 1),
            )
            assert isinstance(filings, list)
            if filings:
                assert isinstance(filings[0], SECFinancialFiling)

    def test_search_by_form_type(self, fmp_client: FMPDataClient, vcr_instance):
        """Test searching by form type"""
        with vcr_instance.use_cassette("sec/search_form_type.yaml"):
            results = self._handle_rate_limit(
                fmp_client.sec.search_by_form_type, "10-K", page=0, limit=5
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], SECFilingSearchResult)

    def test_search_by_symbol(self, fmp_client: FMPDataClient, vcr_instance):
        """Test searching filings by symbol"""
        with vcr_instance.use_cassette("sec/search_by_symbol.yaml"):
            results = self._handle_rate_limit(
                fmp_client.sec.search_by_symbol, "AAPL", page=0, limit=5
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], SECFilingSearchResult)

    def test_search_by_cik(self, fmp_client: FMPDataClient, vcr_instance):
        """Test searching filings by CIK"""
        with vcr_instance.use_cassette("sec/search_by_cik.yaml"):
            results = self._handle_rate_limit(
                fmp_client.sec.search_by_cik, "0000320193", page=0, limit=5
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], SECFilingSearchResult)

    def test_search_company_by_name(self, fmp_client: FMPDataClient, vcr_instance):
        """Test searching companies by name"""
        with vcr_instance.use_cassette("sec/search_company_name.yaml"):
            results = self._handle_rate_limit(
                fmp_client.sec.search_company_by_name, "Apple", page=0, limit=5
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], SECCompanySearchResult)

    def test_search_company_by_symbol(self, fmp_client: FMPDataClient, vcr_instance):
        """Test searching companies by symbol"""
        with vcr_instance.use_cassette("sec/search_company_symbol.yaml"):
            results = self._handle_rate_limit(
                fmp_client.sec.search_company_by_symbol, "AAPL"
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], SECCompanySearchResult)

    def test_search_company_by_cik(self, fmp_client: FMPDataClient, vcr_instance):
        """Test searching companies by CIK"""
        with vcr_instance.use_cassette("sec/search_company_cik.yaml"):
            results = self._handle_rate_limit(
                fmp_client.sec.search_company_by_cik, "0000320193"
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], SECCompanySearchResult)

    def test_get_profile(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting SEC profile"""
        with vcr_instance.use_cassette("sec/profile.yaml"):
            profile = self._handle_rate_limit(fmp_client.sec.get_profile, "AAPL")
            assert profile is None or isinstance(profile, SECProfile)

    def test_get_sic_codes(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting SIC codes"""
        with vcr_instance.use_cassette("sec/sic_codes.yaml"):
            results = self._handle_rate_limit(fmp_client.sec.get_sic_codes)
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], SICCode)

    def test_search_industry_classification(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test searching industry classification data"""
        with vcr_instance.use_cassette("sec/industry_classification_search.yaml"):
            results = self._handle_rate_limit(
                fmp_client.sec.search_industry_classification, symbol="AAPL"
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], IndustryClassification)

    def test_get_all_industry_classification(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting all industry classification records"""
        with vcr_instance.use_cassette("sec/all_industry_classification.yaml"):
            results = self._handle_rate_limit(
                fmp_client.sec.get_all_industry_classification, page=0, limit=5
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], IndustryClassification)
