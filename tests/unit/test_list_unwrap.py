"""Mechanical _unwrap_list coverage for remaining domains (#242)."""

from unittest.mock import AsyncMock, Mock

import pytest

from fmp_data.alternative.async_client import AsyncAlternativeMarketsClient
from fmp_data.alternative.client import AlternativeMarketsClient
from fmp_data.alternative.endpoints import CRYPTO_HISTORICAL, CRYPTO_LIST
from fmp_data.alternative.models import CryptoHistoricalPrice, CryptoPair
from fmp_data.economics.client import EconomicsClient
from fmp_data.economics.endpoints import ECONOMIC_INDICATORS, TREASURY_RATES
from fmp_data.economics.models import EconomicIndicator, TreasuryRate
from fmp_data.fundamental.client import FundamentalClient
from fmp_data.fundamental.endpoints import INCOME_STATEMENT, KEY_METRICS
from fmp_data.fundamental.models import IncomeStatement, KeyMetrics
from fmp_data.institutional.client import InstitutionalClient
from fmp_data.institutional.endpoints import FORM_13F_DATES, INSTITUTIONAL_HOLDERS
from fmp_data.institutional.models import Form13FDate, InstitutionalHolder
from fmp_data.intelligence.client import MarketIntelligenceClient
from fmp_data.intelligence.endpoints import EARNINGS_CALENDAR, GENERAL_NEWS_ENDPOINT
from fmp_data.intelligence.models import EarningEvent, GeneralNewsArticle
from fmp_data.investment.client import InvestmentClient
from fmp_data.investment.endpoints import ETF_HOLDINGS, ETF_SECTOR_WEIGHTINGS
from fmp_data.investment.models import ETFHolding, ETFSectorWeighting
from fmp_data.market.client import MarketClient
from fmp_data.market.endpoints import (
    ALL_EXCHANGE_MARKET_HOURS,
    AVAILABLE_SECTORS,
    STOCK_LIST,
)
from fmp_data.market.models import MarketHours
from fmp_data.models import CompanySymbol
from fmp_data.technical.client import TechnicalClient
from fmp_data.technical.endpoints import SMA
from fmp_data.technical.models import SMAIndicator


@pytest.fixture
def mock_client():
    client = Mock()
    client.logger = Mock()
    return client


_MARKET_CASES: list[tuple[str, dict[str, object]]] = [
    ("get_all_exchange_market_hours", {}),
    ("get_available_sectors", {}),
    ("get_stock_list", {}),
    ("get_gainers", {}),
]

_FUNDAMENTAL_CASES = [
    ("get_income_statement", {"symbol": "AAPL"}),
    ("get_key_metrics", {"symbol": "AAPL"}),
]

_INSTITUTIONAL_CASES = [
    ("get_form_13f_dates", {"cik": "0001067983"}),
    ("get_form_13f_by_quarter", {"cik": "0001067983", "year": 2023, "quarter": 3}),
    ("get_institutional_holders", {}),
]

_INVESTMENT_CASES = [
    ("get_etf_holdings", {"symbol": "SPY"}),
    ("get_etf_sector_weightings", {"symbol": "SPY"}),
]

_INTELLIGENCE_CASES: list[tuple[str, dict[str, object]]] = [
    ("get_earnings_calendar", {}),
    ("get_general_news", {}),
]

_ALTERNATIVE_CASES = [
    ("get_crypto_list", {}),
    ("get_crypto_intraday", {"symbol": "BTCUSD"}),
]

_ECONOMICS_CASES = [
    ("get_market_risk_premium", {}),
    ("get_economic_indicators", {"indicator_name": "GDP"}),
]

_TECHNICAL_CASES = [
    ("get_sma", {"symbol": "AAPL"}),
]


def _assert_wrap_single_and_empty(client, method_name, kwargs):
    row = object()
    method = getattr(client, method_name)

    client.client.request.return_value = row
    assert method(**kwargs) == [row]

    client.client.request.return_value = []
    assert method(**kwargs) == []
    client.client.request.assert_called()


class TestMarketListUnwrap:
    @pytest.mark.parametrize("method_name,kwargs", _MARKET_CASES)
    def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        _assert_wrap_single_and_empty(MarketClient(mock_client), method_name, kwargs)


class TestFundamentalListUnwrap:
    @pytest.mark.parametrize("method_name,kwargs", _FUNDAMENTAL_CASES)
    def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        _assert_wrap_single_and_empty(
            FundamentalClient(mock_client), method_name, kwargs
        )


class TestInstitutionalListUnwrap:
    @pytest.mark.parametrize("method_name,kwargs", _INSTITUTIONAL_CASES)
    def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        _assert_wrap_single_and_empty(
            InstitutionalClient(mock_client), method_name, kwargs
        )


class TestInvestmentListUnwrap:
    @pytest.mark.parametrize("method_name,kwargs", _INVESTMENT_CASES)
    def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        _assert_wrap_single_and_empty(
            InvestmentClient(mock_client), method_name, kwargs
        )


class TestIntelligenceListUnwrap:
    @pytest.mark.parametrize("method_name,kwargs", _INTELLIGENCE_CASES)
    def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        _assert_wrap_single_and_empty(
            MarketIntelligenceClient(mock_client), method_name, kwargs
        )


class TestAlternativeListUnwrap:
    @pytest.mark.parametrize("method_name,kwargs", _ALTERNATIVE_CASES)
    def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        _assert_wrap_single_and_empty(
            AlternativeMarketsClient(mock_client), method_name, kwargs
        )


class TestEconomicsListUnwrap:
    @pytest.mark.parametrize("method_name,kwargs", _ECONOMICS_CASES)
    def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        _assert_wrap_single_and_empty(EconomicsClient(mock_client), method_name, kwargs)


class TestTechnicalListUnwrap:
    @pytest.mark.parametrize("method_name,kwargs", _TECHNICAL_CASES)
    def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        _assert_wrap_single_and_empty(TechnicalClient(mock_client), method_name, kwargs)


class TestAsyncAlternativeListUnwrap:
    @pytest.mark.asyncio
    async def test_crypto_list_wraps_single_and_keeps_empty(self, mock_client):
        mock_client.request_async = AsyncMock()
        client = AsyncAlternativeMarketsClient(mock_client)
        row = object()

        mock_client.request_async.return_value = row
        assert await client.get_crypto_list() == [row]

        mock_client.request_async.return_value = []
        assert await client.get_crypto_list() == []


class TestPreviouslyUntypedEndpointRowBindings:
    @pytest.mark.parametrize(
        "endpoint,row_type",
        [
            (STOCK_LIST, CompanySymbol),
            (ALL_EXCHANGE_MARKET_HOURS, MarketHours),
            (AVAILABLE_SECTORS, str),
            (INCOME_STATEMENT, IncomeStatement),
            (KEY_METRICS, KeyMetrics),
            (FORM_13F_DATES, Form13FDate),
            (INSTITUTIONAL_HOLDERS, InstitutionalHolder),
            (ETF_HOLDINGS, ETFHolding),
            (ETF_SECTOR_WEIGHTINGS, ETFSectorWeighting),
            (EARNINGS_CALENDAR, EarningEvent),
            (GENERAL_NEWS_ENDPOINT, GeneralNewsArticle),
            (CRYPTO_LIST, CryptoPair),
            (CRYPTO_HISTORICAL, CryptoHistoricalPrice),
            (TREASURY_RATES, TreasuryRate),
            (ECONOMIC_INDICATORS, EconomicIndicator),
            (SMA, SMAIndicator),
        ],
    )
    def test_list_endpoints_bind_row_type(self, endpoint, row_type):
        """List endpoints bind T as the row, not list[T]."""
        assert endpoint.response_model is row_type
