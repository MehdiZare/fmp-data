# tests/unit/test_transcripts.py
"""Tests for the transcripts module endpoints"""

from unittest.mock import patch

import pytest

from fmp_data.transcripts.models import (
    EarningsTranscript,
    TranscriptDate,
    TranscriptSymbol,
)


class TestTranscriptsModels:
    """Tests for transcript model validation"""

    @pytest.fixture
    def transcript_data(self):
        """Mock earnings transcript data"""
        return {
            "symbol": "AAPL",
            "quarter": 4,
            "year": 2023,
            "date": "2024-02-01T16:30:00.000+0000",
            "content": "Good afternoon, everyone. Thank you for joining us...",
        }

    @pytest.fixture
    def transcript_date_data(self):
        """Mock transcript date data"""
        return {
            "symbol": "AAPL",
            "quarter": 4,
            "year": 2023,
            "date": "2024-02-01T16:30:00.000+0000",
        }

    @pytest.fixture
    def transcript_symbol_data(self):
        """Mock transcript symbol data"""
        return {"symbol": "AAPL"}

    def test_earnings_transcript_model(self, transcript_data):
        """Test EarningsTranscript model validation"""
        transcript = EarningsTranscript.model_validate(transcript_data)
        assert transcript.symbol == "AAPL"
        assert transcript.quarter == 4
        assert transcript.year == 2023
        assert transcript.content is not None
        assert "Thank you" in transcript.content

    def test_earnings_transcript_minimal(self):
        """Test EarningsTranscript with only required fields"""
        transcript = EarningsTranscript.model_validate(
            {"symbol": "TEST", "quarter": 1, "year": 2024}
        )
        assert transcript.symbol == "TEST"
        assert transcript.quarter == 1
        assert transcript.year == 2024
        assert transcript.date is None
        assert transcript.content is None

    def test_transcript_date_model(self, transcript_date_data):
        """Test TranscriptDate model validation"""
        td = TranscriptDate.model_validate(transcript_date_data)
        assert td.symbol == "AAPL"
        assert td.quarter == 4
        assert td.year == 2023

    def test_transcript_symbol_model(self, transcript_symbol_data):
        """Test TranscriptSymbol model validation"""
        ts = TranscriptSymbol.model_validate(transcript_symbol_data)
        assert ts.symbol == "AAPL"


class TestTranscriptsClient:
    """Tests for TranscriptsClient methods"""

    @pytest.fixture
    def transcript_data(self):
        """Mock transcript data"""
        return {
            "symbol": "AAPL",
            "quarter": 4,
            "year": 2023,
            "content": "Earnings call content...",
        }

    @patch("httpx.Client.request")
    def test_get_latest(self, mock_request, fmp_client, mock_response, transcript_data):
        """Test fetching latest transcripts"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[transcript_data]
        )
        result = fmp_client.transcripts.get_latest(page=0, limit=10)
        assert len(result) == 1
        assert isinstance(result[0], EarningsTranscript)
        assert result[0].symbol == "AAPL"

    @patch("httpx.Client.request")
    def test_get_transcript(
        self, mock_request, fmp_client, mock_response, transcript_data
    ):
        """Test fetching transcript for specific symbol"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[transcript_data]
        )
        result = fmp_client.transcripts.get_transcript(
            "AAPL", year=2023, quarter=4, limit=1
        )
        assert len(result) == 1
        assert isinstance(result[0], EarningsTranscript)
        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["limit"] == 1
        assert call_args.kwargs["params"]["year"] == 2023
        assert call_args.kwargs["params"]["quarter"] == 4

    @patch("httpx.Client.request")
    def test_get_transcript_with_year_quarter(
        self, mock_request, fmp_client, mock_response, transcript_data
    ):
        """Test fetching transcript for specific year and quarter"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[transcript_data]
        )
        result = fmp_client.transcripts.get_transcript("AAPL", year=2023, quarter=4)
        assert len(result) == 1
        assert result[0].year == 2023
        assert result[0].quarter == 4

    @patch("httpx.Client.request")
    def test_get_available_dates(self, mock_request, fmp_client, mock_response):
        """Test fetching available transcript dates"""
        date_data = {"symbol": "AAPL", "quarter": 4, "year": 2023}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[date_data]
        )
        result = fmp_client.transcripts.get_available_dates("AAPL")
        assert len(result) == 1
        assert isinstance(result[0], TranscriptDate)

    @patch("httpx.Client.request")
    def test_get_available_symbols(self, mock_request, fmp_client, mock_response):
        """Test fetching available symbols"""
        symbol_data = {"symbol": "AAPL"}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[symbol_data, {"symbol": "MSFT"}]
        )
        result = fmp_client.transcripts.get_available_symbols()
        assert len(result) == 2
        assert isinstance(result[0], TranscriptSymbol)
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "MSFT"
