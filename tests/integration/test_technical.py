from fmp_data import FMPDataClient
from fmp_data.technical.models import (
    ADXIndicator,
    DEMAIndicator,
    EMAIndicator,
    RSIIndicator,
    SMAIndicator,
    StandardDeviationIndicator,
    TEMAIndicator,
    WilliamsIndicator,
    WMAIndicator,
)

from .base import BaseTestCase


class TestTechnicalClientEndpoints(BaseTestCase):
    """Integration tests for TechnicalClient endpoints using VCR"""

    def test_get_sma(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Simple Moving Average (SMA)"""
        with vcr_instance.use_cassette("technical/sma.yaml"):
            sma_data = self._handle_rate_limit(
                fmp_client.technical.get_sma,
                symbol="AAPL",
                period_length=20,
                interval="daily",
            )

            assert isinstance(sma_data, list)
            assert len(sma_data) > 0
            for item in sma_data:
                assert isinstance(item, SMAIndicator)

    def test_get_ema(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Exponential Moving Average (EMA)"""
        with vcr_instance.use_cassette("technical/ema.yaml"):
            ema_data = self._handle_rate_limit(
                fmp_client.technical.get_ema,
                symbol="AAPL",
                period_length=20,
                interval="daily",
            )

            assert isinstance(ema_data, list)
            assert len(ema_data) > 0
            for item in ema_data:
                assert isinstance(item, EMAIndicator)

    def test_get_wma(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Weighted Moving Average (WMA)"""
        with vcr_instance.use_cassette("technical/wma.yaml"):
            wma_data = self._handle_rate_limit(
                fmp_client.technical.get_wma,
                symbol="AAPL",
                period_length=20,
                interval="daily",
            )

            assert isinstance(wma_data, list)
            assert len(wma_data) > 0
            for item in wma_data:
                assert isinstance(item, WMAIndicator)

    def test_get_dema(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Double Exponential Moving Average (DEMA)"""
        with vcr_instance.use_cassette("technical/dema.yaml"):
            dema_data = self._handle_rate_limit(
                fmp_client.technical.get_dema,
                symbol="AAPL",
                period_length=20,
                interval="daily",
            )

            assert isinstance(dema_data, list)
            assert len(dema_data) > 0
            for item in dema_data:
                assert isinstance(item, DEMAIndicator)

    def test_get_tema(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Triple Exponential Moving Average (TEMA)"""
        with vcr_instance.use_cassette("technical/tema.yaml"):
            tema_data = self._handle_rate_limit(
                fmp_client.technical.get_tema,
                symbol="AAPL",
                period_length=20,
                interval="daily",
            )

            assert isinstance(tema_data, list)
            assert len(tema_data) > 0
            for item in tema_data:
                assert isinstance(item, TEMAIndicator)

    def test_get_williams(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Williams %R"""
        with vcr_instance.use_cassette("technical/williams.yaml"):
            williams_data = self._handle_rate_limit(
                fmp_client.technical.get_williams,
                symbol="AAPL",
                period_length=14,
                interval="daily",
            )

            assert isinstance(williams_data, list)
            assert len(williams_data) > 0
            for item in williams_data:
                assert isinstance(item, WilliamsIndicator)

    def test_get_rsi(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Relative Strength Index (RSI)"""
        with vcr_instance.use_cassette("technical/rsi.yaml"):
            rsi_data = self._handle_rate_limit(
                fmp_client.technical.get_rsi,
                symbol="AAPL",
                period_length=14,
                interval="daily",
            )

            assert isinstance(rsi_data, list)
            assert len(rsi_data) > 0
            for item in rsi_data:
                assert isinstance(item, RSIIndicator)

    def test_get_adx(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Average Directional Index (ADX)"""
        with vcr_instance.use_cassette("technical/adx.yaml"):
            adx_data = self._handle_rate_limit(
                fmp_client.technical.get_adx,
                symbol="AAPL",
                period_length=14,
                interval="daily",
            )

            assert isinstance(adx_data, list)
            assert len(adx_data) > 0
            for item in adx_data:
                assert isinstance(item, ADXIndicator)

    def test_get_standard_deviation(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Standard Deviation"""
        with vcr_instance.use_cassette("technical/standard_deviation.yaml"):
            sd_data = self._handle_rate_limit(
                fmp_client.technical.get_standard_deviation,
                symbol="AAPL",
                period_length=20,
                interval="daily",
            )

            assert isinstance(sd_data, list)
            assert len(sd_data) > 0
            for item in sd_data:
                assert isinstance(item, StandardDeviationIndicator)
