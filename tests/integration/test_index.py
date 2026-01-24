# tests/integration/test_index.py
from fmp_data import FMPDataClient
from fmp_data.index.models import HistoricalIndexConstituent, IndexConstituent
from tests.integration.base import BaseTestCase


class TestIndexClientEndpoints(BaseTestCase):
    """Integration tests for IndexClient endpoints using VCR"""

    def test_get_sp500_constituents(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting S&P 500 constituents"""
        with vcr_instance.use_cassette("index/sp500_constituents.yaml"):
            results = self._handle_rate_limit(fmp_client.index.get_sp500_constituents)
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], IndexConstituent)

    def test_get_nasdaq_constituents(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Nasdaq constituents"""
        with vcr_instance.use_cassette("index/nasdaq_constituents.yaml"):
            results = self._handle_rate_limit(fmp_client.index.get_nasdaq_constituents)
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], IndexConstituent)

    def test_get_dowjones_constituents(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Dow Jones constituents"""
        with vcr_instance.use_cassette("index/dowjones_constituents.yaml"):
            results = self._handle_rate_limit(
                fmp_client.index.get_dowjones_constituents
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], IndexConstituent)

    def test_get_historical_sp500(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical S&P 500 changes"""
        with vcr_instance.use_cassette("index/historical_sp500.yaml"):
            results = self._handle_rate_limit(fmp_client.index.get_historical_sp500)
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], HistoricalIndexConstituent)

    def test_get_historical_nasdaq(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical Nasdaq changes"""
        with vcr_instance.use_cassette("index/historical_nasdaq.yaml"):
            results = self._handle_rate_limit(fmp_client.index.get_historical_nasdaq)
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], HistoricalIndexConstituent)

    def test_get_historical_dowjones(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical Dow Jones changes"""
        with vcr_instance.use_cassette("index/historical_dowjones.yaml"):
            results = self._handle_rate_limit(fmp_client.index.get_historical_dowjones)
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], HistoricalIndexConstituent)
