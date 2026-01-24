from datetime import date, datetime
from unittest.mock import patch

import pytest

from fmp_data.client import FMPDataClient
from fmp_data.exceptions import RateLimitError
from fmp_data.technical.models import EMAIndicator, RSIIndicator, SMAIndicator


class TestTechnicalClient:
    """Tests for TechnicalClient and related technical indicator functionality"""

    @pytest.fixture
    def sma_data(self):
        """Mock SMA indicator data"""
        return {
            "date": "2024-01-01T00:00:00",
            "open": 150.0,
            "high": 155.0,
            "low": 148.0,
            "close": 152.0,
            "volume": 100000,
            "sma": 151.5,
        }

    @pytest.fixture
    def rsi_data(self):
        """Mock RSI indicator data"""
        return {
            "date": "2024-01-01T00:00:00",
            "open": 150.0,
            "high": 155.0,
            "low": 148.0,
            "close": 152.0,
            "volume": 100000,
            "rsi": 70.5,
        }

    @pytest.fixture
    def ema_data(self):
        """Mock EMA indicator data"""
        return {
            "date": "2024-01-01T00:00:00",
            "open": 150.0,
            "high": 155.0,
            "low": 148.0,
            "close": 152.0,
            "volume": 100000,
            "ema": 151.2,
        }

    def test_sma_model_validation(self, sma_data):
        """Test SMAIndicator model validation with full data"""
        sma = SMAIndicator.model_validate(sma_data)
        assert sma.date == datetime(2024, 1, 1)
        assert sma.open == 150.0
        assert sma.high == 155.0
        assert sma.sma == 151.5

    def test_ema_model_validation(self, ema_data):
        """Test EMAIndicator model validation with full data"""
        ema = EMAIndicator.model_validate(ema_data)
        assert ema.date == datetime(2024, 1, 1)
        assert ema.ema == 151.2

    def test_rsi_model_validation(self, rsi_data):
        """Test RSIIndicator model validation with full data"""
        rsi = RSIIndicator.model_validate(rsi_data)
        assert rsi.date == datetime(2024, 1, 1)
        assert rsi.rsi == 70.5

    def test_invalid_indicator_data(self):
        """Test model validation with missing required fields"""
        invalid_data = {
            "date": "2024-01-01T00:00:00",
        }
        with pytest.raises(ValueError):
            SMAIndicator.model_validate(invalid_data)

    @patch("httpx.Client.request")
    def test_get_sma_indicator(self, mock_request, fmp_client, mock_response, sma_data):
        """Test fetching SMA indicator data"""
        mock_request.return_value = mock_response(status_code=200, json_data=[sma_data])
        result = fmp_client.technical.get_sma(
            symbol="AAPL",
            period_length=20,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        assert len(result) == 1
        sma = result[0]
        assert isinstance(sma, SMAIndicator)
        assert sma.sma == 151.5

    @patch("httpx.Client.request")
    def test_get_ema_indicator(self, mock_request, fmp_client, mock_response, ema_data):
        """Test fetching EMA indicator data"""
        mock_request.return_value = mock_response(status_code=200, json_data=[ema_data])
        result = fmp_client.technical.get_ema(
            symbol="AAPL",
            period_length=20,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        assert len(result) == 1
        ema = result[0]
        assert isinstance(ema, EMAIndicator)
        assert ema.ema == 151.2

    @patch("httpx.Client.request")
    def test_get_rsi_indicator(self, mock_request, fmp_client, mock_response, rsi_data):
        """Test fetching RSI indicator data"""
        mock_request.return_value = mock_response(status_code=200, json_data=[rsi_data])
        result = fmp_client.technical.get_rsi(
            symbol="AAPL",
            period_length=14,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        assert len(result) == 1
        rsi = result[0]
        assert isinstance(rsi, RSIIndicator)
        assert rsi.rsi == 70.5

    def test_invalid_api_response(self):
        """Test invalid API response handling"""
        invalid_data = [{"invalid_field": "value"}]
        with pytest.raises(ValueError):
            SMAIndicator.model_validate(invalid_data[0])

    @staticmethod
    @patch("httpx.Client.request")
    def test_rate_limit_handling(mock_request, fmp_client):
        """Test handling rate limit errors from the API with retries"""
        client = FMPDataClient(
            config=fmp_client.config.model_copy(update={"max_retries": 3})
        )
        with (
            patch.object(
                client._rate_limiter, "should_allow_request", return_value=False
            ),
            patch.object(client._rate_limiter, "get_wait_time", return_value=0.0),
            patch.object(
                client, "_handle_rate_limit", side_effect=RateLimitError("rl")
            ),
        ):
            with pytest.raises(RateLimitError):
                client.technical.get_sma(
                    symbol="AAPL",
                    period_length=20,
                    start_date=date(2024, 1, 1),
                    end_date=date(2024, 1, 31),
                )
        client.close()
