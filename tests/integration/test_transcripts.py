# tests/integration/test_transcripts.py
from fmp_data import FMPDataClient
from fmp_data.transcripts.models import (
    EarningsTranscript,
    TranscriptDate,
    TranscriptSymbol,
)
from tests.integration.base import BaseTestCase


class TestTranscriptsClientEndpoints(BaseTestCase):
    """Integration tests for TranscriptsClient endpoints using VCR"""

    def test_get_latest(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting latest transcripts"""
        with vcr_instance.use_cassette("transcripts/latest.yaml"):
            results = self._handle_rate_limit(
                fmp_client.transcripts.get_latest, page=0, limit=5
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], EarningsTranscript)

    def test_get_transcript(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting transcript by symbol and period"""
        with vcr_instance.use_cassette("transcripts/transcript.yaml"):
            results = self._handle_rate_limit(
                fmp_client.transcripts.get_transcript, "AAPL", year=2023, quarter=4
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], EarningsTranscript)

    def test_get_available_dates(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting available transcript dates"""
        with vcr_instance.use_cassette("transcripts/available_dates.yaml"):
            results = self._handle_rate_limit(
                fmp_client.transcripts.get_available_dates, "AAPL"
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], TranscriptDate)

    def test_get_available_symbols(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting available transcript symbols"""
        with vcr_instance.use_cassette("transcripts/available_symbols.yaml"):
            results = self._handle_rate_limit(
                fmp_client.transcripts.get_available_symbols
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], TranscriptSymbol)
