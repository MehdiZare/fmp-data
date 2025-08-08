"""Additional tests for technical client to improve coverage"""

from datetime import date
from unittest.mock import patch

import pytest

from fmp_data.technical.models import (
    ADXIndicator,
    DEMAIndicator,
    StandardDeviationIndicator,
    TEMAIndicator,
    WilliamsIndicator,
    WMAIndicator,
)


class TestTechnicalClientCoverage:
    """Additional tests to improve coverage for TechnicalClient"""

    @pytest.fixture
    def wma_data(self):
        """Mock WMA indicator data"""
        return {
            "date": "2024-01-01T00:00:00",
            "open": 150.0,
            "high": 155.0,
            "low": 148.0,
            "close": 152.0,
            "volume": 100000,
            "wma": 151.8,
        }

    @pytest.fixture
    def dema_data(self):
        """Mock DEMA indicator data"""
        return {
            "date": "2024-01-01T00:00:00",
            "open": 150.0,
            "high": 155.0,
            "low": 148.0,
            "close": 152.0,
            "volume": 100000,
            "dema": 151.3,
        }

    @pytest.fixture
    def tema_data(self):
        """Mock TEMA indicator data"""
        return {
            "date": "2024-01-01T00:00:00",
            "open": 150.0,
            "high": 155.0,
            "low": 148.0,
            "close": 152.0,
            "volume": 100000,
            "tema": 151.4,
        }

    @pytest.fixture
    def williams_data(self):
        """Mock Williams %R indicator data"""
        return {
            "date": "2024-01-01T00:00:00",
            "open": 150.0,
            "high": 155.0,
            "low": 148.0,
            "close": 152.0,
            "volume": 100000,
            "williams": -30.5,
        }

    @pytest.fixture
    def adx_data(self):
        """Mock ADX indicator data"""
        return {
            "date": "2024-01-01T00:00:00",
            "open": 150.0,
            "high": 155.0,
            "low": 148.0,
            "close": 152.0,
            "volume": 100000,
            "adx": 25.5,
        }

    @pytest.fixture
    def std_dev_data(self):
        """Mock Standard Deviation indicator data"""
        return {
            "date": "2024-01-01T00:00:00",
            "open": 150.0,
            "high": 155.0,
            "low": 148.0,
            "close": 152.0,
            "volume": 100000,
            "standardDeviation": 2.5,
        }

    @patch("httpx.Client.request")
    def test_get_wma(self, mock_request, fmp_client, mock_response, wma_data):
        """Test fetching WMA indicator data"""
        mock_request.return_value = mock_response(status_code=200, json_data=[wma_data])
        result = fmp_client.technical.get_wma(
            symbol="AAPL",
            period_length=20,
            timeframe="1day",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        assert len(result) == 1
        wma = result[0]
        assert isinstance(wma, WMAIndicator)
        assert wma.wma == 151.8

    @patch("httpx.Client.request")
    def test_get_dema(self, mock_request, fmp_client, mock_response, dema_data):
        """Test fetching DEMA indicator data"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[dema_data]
        )
        result = fmp_client.technical.get_dema(
            symbol="AAPL",
            period_length=20,
            timeframe="1day",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        assert len(result) == 1
        dema = result[0]
        assert isinstance(dema, DEMAIndicator)
        assert dema.dema == 151.3

    @patch("httpx.Client.request")
    def test_get_tema(self, mock_request, fmp_client, mock_response, tema_data):
        """Test fetching TEMA indicator data"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[tema_data]
        )
        result = fmp_client.technical.get_tema(
            symbol="AAPL",
            period_length=20,
            timeframe="1day",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        assert len(result) == 1
        tema = result[0]
        assert isinstance(tema, TEMAIndicator)
        assert tema.tema == 151.4

    @patch("httpx.Client.request")
    def test_get_williams(self, mock_request, fmp_client, mock_response, williams_data):
        """Test fetching Williams %R indicator data"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[williams_data]
        )
        result = fmp_client.technical.get_williams(
            symbol="AAPL",
            period_length=14,
            timeframe="1day",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        assert len(result) == 1
        williams = result[0]
        assert isinstance(williams, WilliamsIndicator)
        assert williams.williams == -30.5

    @patch("httpx.Client.request")
    def test_get_adx(self, mock_request, fmp_client, mock_response, adx_data):
        """Test fetching ADX indicator data"""
        mock_request.return_value = mock_response(status_code=200, json_data=[adx_data])
        result = fmp_client.technical.get_adx(
            symbol="AAPL",
            period_length=14,
            timeframe="1day",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        assert len(result) == 1
        adx = result[0]
        assert isinstance(adx, ADXIndicator)
        assert adx.adx == 25.5

    @patch("httpx.Client.request")
    def test_get_standard_deviation(
        self, mock_request, fmp_client, mock_response, std_dev_data
    ):
        """Test fetching Standard Deviation indicator data"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[std_dev_data]
        )
        result = fmp_client.technical.get_standard_deviation(
            symbol="AAPL",
            period_length=20,
            timeframe="1day",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        assert len(result) == 1
        std_dev = result[0]
        assert isinstance(std_dev, StandardDeviationIndicator)
        assert std_dev.standard_deviation == 2.5

    @patch("httpx.Client.request")
    def test_technical_methods_without_dates(
        self, mock_request, fmp_client, mock_response, wma_data
    ):
        """Test technical methods without date parameters"""
        mock_request.return_value = mock_response(status_code=200, json_data=[wma_data])

        # Test without any date parameters
        result = fmp_client.technical.get_wma(
            symbol="AAPL", period_length=20, timeframe="1day"
        )
        assert len(result) == 1

    @patch("httpx.Client.request")
    def test_technical_methods_with_different_timeframes(
        self, mock_request, fmp_client, mock_response, wma_data
    ):
        """Test technical methods with different timeframes"""
        mock_request.return_value = mock_response(status_code=200, json_data=[wma_data])

        # Test with different timeframes
        for timeframe in ["1min", "5min", "15min", "30min", "1hour", "4hour", "1day"]:
            result = fmp_client.technical.get_wma(
                symbol="AAPL", period_length=20, timeframe=timeframe
            )
            assert len(result) == 1
