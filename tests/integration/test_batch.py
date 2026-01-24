# tests/integration/test_batch.py
from typing import ClassVar

import pytest

from fmp_data import FMPDataClient
from fmp_data.batch.models import (
    AftermarketQuote,
    AftermarketTrade,
    BatchMarketCap,
    BatchQuote,
    BatchQuoteShort,
)
from fmp_data.company.models import CompanyProfile
from fmp_data.fundamental.models import (
    DCF,
    CompanyRating,
    FinancialRatiosTTM,
    FinancialScore,
)
from tests.integration.base import BaseTestCase


class TestBatchClientEndpoints(BaseTestCase):
    """Integration tests for BatchClient endpoints using VCR"""

    SYMBOLS: ClassVar[list[str]] = ["AAPL", "MSFT"]

    @pytest.mark.parametrize(
        "method_name,cassette,expected_type",
        [
            ("get_quotes", "quotes", BatchQuote),
            ("get_quotes_short", "quotes_short", BatchQuoteShort),
            ("get_aftermarket_trades", "aftermarket_trades", AftermarketTrade),
            ("get_aftermarket_quotes", "aftermarket_quotes", AftermarketQuote),
            ("get_market_caps", "market_caps", BatchMarketCap),
        ],
    )
    def test_symbol_batches(
        self,
        fmp_client: FMPDataClient,
        vcr_instance,
        method_name: str,
        cassette: str,
        expected_type: type,
    ):
        """Test batch endpoints that accept symbols list"""
        with vcr_instance.use_cassette(f"batch/{cassette}.yaml"):
            method = getattr(fmp_client.batch, method_name)
            results = self._handle_rate_limit(method, self.SYMBOLS)
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], expected_type)

    def test_get_exchange_quotes(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting exchange quotes"""
        with vcr_instance.use_cassette("batch/exchange_quotes.yaml"):
            quotes = self._handle_rate_limit(
                fmp_client.batch.get_exchange_quotes, "NASDAQ"
            )
            assert isinstance(quotes, list)
            if quotes:
                assert isinstance(quotes[0], BatchQuote)

    @pytest.mark.parametrize(
        "method_name,cassette",
        [
            ("get_mutualfund_quotes", "mutualfund_quotes"),
            ("get_etf_quotes", "etf_quotes"),
            ("get_commodity_quotes", "commodity_quotes"),
            ("get_crypto_quotes", "crypto_quotes"),
            ("get_forex_quotes", "forex_quotes"),
            ("get_index_quotes", "index_quotes"),
        ],
    )
    def test_asset_class_quotes(
        self,
        fmp_client: FMPDataClient,
        vcr_instance,
        method_name: str,
        cassette: str,
    ):
        """Test batch endpoints that return full asset class quotes"""
        with vcr_instance.use_cassette(f"batch/{cassette}.yaml"):
            method = getattr(fmp_client.batch, method_name)
            quotes = self._handle_rate_limit(method)
            assert isinstance(quotes, list)
            if quotes:
                assert isinstance(quotes[0], BatchQuote)

    def test_get_profile_bulk(self, fmp_client: FMPDataClient, vcr_instance):
        """Test bulk company profiles"""
        with vcr_instance.use_cassette("batch/profile_bulk.yaml"):
            profiles = self._handle_rate_limit(fmp_client.batch.get_profile_bulk, "0")
            assert isinstance(profiles, list)
            if profiles:
                assert isinstance(profiles[0], CompanyProfile)

    def test_get_dcf_bulk(self, fmp_client: FMPDataClient, vcr_instance):
        """Test bulk DCF values"""
        with vcr_instance.use_cassette("batch/dcf_bulk.yaml"):
            results = self._handle_rate_limit(fmp_client.batch.get_dcf_bulk)
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], DCF)

    def test_get_rating_bulk(self, fmp_client: FMPDataClient, vcr_instance):
        """Test bulk ratings"""
        with vcr_instance.use_cassette("batch/rating_bulk.yaml"):
            results = self._handle_rate_limit(fmp_client.batch.get_rating_bulk)
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], CompanyRating)

    def test_get_scores_bulk(self, fmp_client: FMPDataClient, vcr_instance):
        """Test bulk financial scores"""
        with vcr_instance.use_cassette("batch/scores_bulk.yaml"):
            results = self._handle_rate_limit(fmp_client.batch.get_scores_bulk)
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], FinancialScore)

    def test_get_ratios_ttm_bulk(self, fmp_client: FMPDataClient, vcr_instance):
        """Test bulk financial ratios TTM"""
        with vcr_instance.use_cassette("batch/ratios_ttm_bulk.yaml"):
            results = self._handle_rate_limit(fmp_client.batch.get_ratios_ttm_bulk)
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], FinancialRatiosTTM)
