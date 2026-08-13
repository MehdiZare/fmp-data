"""Mechanical _unwrap_list coverage for remaining domains (#242)."""

from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from fmp_data.alternative.async_client import AsyncAlternativeMarketsClient
from fmp_data.alternative.client import AlternativeMarketsClient
from fmp_data.alternative.endpoints import CRYPTO_HISTORICAL, CRYPTO_LIST
from fmp_data.alternative.models import (
    CommodityPriceHistory,
    CryptoHistoricalData,
    CryptoHistoricalPrice,
    CryptoPair,
    ForexPriceHistory,
)
from fmp_data.economics.async_client import AsyncEconomicsClient
from fmp_data.economics.client import EconomicsClient
from fmp_data.economics.endpoints import ECONOMIC_INDICATORS, TREASURY_RATES
from fmp_data.economics.models import EconomicIndicator, TreasuryRate
from fmp_data.fundamental.async_client import AsyncFundamentalClient
from fmp_data.fundamental.client import FundamentalClient
from fmp_data.fundamental.endpoints import INCOME_STATEMENT, KEY_METRICS
from fmp_data.fundamental.models import IncomeStatement, KeyMetrics
from fmp_data.institutional.async_client import AsyncInstitutionalClient
from fmp_data.institutional.client import InstitutionalClient
from fmp_data.institutional.endpoints import FORM_13F_DATES, INSTITUTIONAL_HOLDERS
from fmp_data.institutional.models import Form13FDate, InstitutionalHolder
from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient
from fmp_data.intelligence.client import MarketIntelligenceClient
from fmp_data.intelligence.endpoints import EARNINGS_CALENDAR, GENERAL_NEWS_ENDPOINT
from fmp_data.intelligence.models import EarningEvent, GeneralNewsArticle
from fmp_data.investment.async_client import AsyncInvestmentClient
from fmp_data.investment.client import InvestmentClient
from fmp_data.investment.endpoints import ETF_HOLDINGS, ETF_SECTOR_WEIGHTINGS
from fmp_data.investment.models import ETFHolding, ETFSectorWeighting
from fmp_data.market.async_client import AsyncMarketClient
from fmp_data.market.client import MarketClient
from fmp_data.market.endpoints import (
    ALL_EXCHANGE_MARKET_HOURS,
    AVAILABLE_SECTORS,
    STOCK_LIST,
)
from fmp_data.market.models import MarketHours
from fmp_data.models import CompanySymbol
from fmp_data.technical.async_client import AsyncTechnicalClient
from fmp_data.technical.client import TechnicalClient
from fmp_data.technical.endpoints import SMA
from fmp_data.technical.models import SMAIndicator


@pytest.fixture
def mock_client():
    client = Mock()
    client.logger = Mock()
    client.request_async = AsyncMock()
    return client


_MARKET_CASES: list[tuple[str, dict[str, object]]] = [
    ("get_all_exchange_market_hours", {}),
    ("get_available_sectors", {}),
    ("get_available_industries", {}),
    ("get_stock_list", {}),
    ("get_gainers", {}),
    ("get_losers", {}),
    ("get_most_active", {}),
]

_FUNDAMENTAL_CASES = [
    ("get_income_statement", {"symbol": "AAPL"}),
    ("get_balance_sheet", {"symbol": "AAPL"}),
    ("get_cash_flow", {"symbol": "AAPL"}),
    ("get_key_metrics", {"symbol": "AAPL"}),
    ("get_financial_ratios", {"symbol": "AAPL"}),
    ("get_financial_reports_dates", {"symbol": "AAPL"}),
]

_INSTITUTIONAL_CASES = [
    ("get_form_13f_dates", {"cik": "0001067983"}),
    ("get_form_13f_by_quarter", {"cik": "0001067983", "year": 2023, "quarter": 3}),
    ("get_institutional_holders", {}),
    ("get_insider_trades", {"symbol": "AAPL"}),
    ("get_insider_roster", {"symbol": "AAPL"}),
]

_INVESTMENT_CASES = [
    ("get_etf_holdings", {"symbol": "SPY"}),
    ("get_etf_sector_weightings", {"symbol": "SPY"}),
    ("get_etf_country_weightings", {"symbol": "SPY"}),
    ("get_mutual_fund_dates", {"symbol": "VTSAX"}),
]

_INTELLIGENCE_CASES: list[tuple[str, dict[str, object]]] = [
    ("get_earnings_calendar", {}),
    ("get_dividends_calendar", {}),
    ("get_stock_splits_calendar", {}),
    ("get_ipo_calendar", {}),
    ("get_general_news", {}),
    ("get_esg_benchmark", {}),
    ("get_senate_latest", {}),
    ("get_house_latest", {}),
    ("get_press_releases", {}),
]

_ALTERNATIVE_CASES = [
    ("get_crypto_list", {}),
    ("get_crypto_intraday", {"symbol": "BTCUSD"}),
    ("get_forex_list", {}),
    ("get_forex_intraday", {"symbol": "EURUSD"}),
    ("get_commodities_list", {}),
    ("get_commodity_intraday", {"symbol": "GCUSD"}),
]

_ECONOMICS_CASES = [
    ("get_market_risk_premium", {}),
    ("get_economic_indicators", {"indicator_name": "GDP"}),
    ("get_treasury_rates", {}),
    ("get_economic_calendar", {}),
]

_TECHNICAL_CASES = [
    ("get_sma", {"symbol": "AAPL"}),
    ("get_ema", {"symbol": "AAPL"}),
    ("get_rsi", {"symbol": "AAPL"}),
]


def _assert_wrap_single_and_empty(client, method_name, kwargs):
    row = object()
    method = getattr(client, method_name)

    client.client.request.return_value = row
    assert method(**kwargs) == [row]

    client.client.request.return_value = []
    assert method(**kwargs) == []
    client.client.request.assert_called()


async def _assert_wrap_single_and_empty_async(client, method_name, kwargs):
    row = object()
    method = getattr(client, method_name)

    client.client.request_async.return_value = row
    assert await method(**kwargs) == [row]

    client.client.request_async.return_value = []
    assert await method(**kwargs) == []
    client.client.request_async.assert_called()


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


class TestAsyncMarketListUnwrap:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,kwargs", _MARKET_CASES)
    async def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        await _assert_wrap_single_and_empty_async(
            AsyncMarketClient(mock_client), method_name, kwargs
        )


class TestAsyncFundamentalListUnwrap:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,kwargs", _FUNDAMENTAL_CASES)
    async def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        await _assert_wrap_single_and_empty_async(
            AsyncFundamentalClient(mock_client), method_name, kwargs
        )


class TestAsyncInstitutionalListUnwrap:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,kwargs", _INSTITUTIONAL_CASES)
    async def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        await _assert_wrap_single_and_empty_async(
            AsyncInstitutionalClient(mock_client), method_name, kwargs
        )


class TestAsyncInvestmentListUnwrap:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,kwargs", _INVESTMENT_CASES)
    async def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        await _assert_wrap_single_and_empty_async(
            AsyncInvestmentClient(mock_client), method_name, kwargs
        )


class TestAsyncIntelligenceListUnwrap:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,kwargs", _INTELLIGENCE_CASES)
    async def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        await _assert_wrap_single_and_empty_async(
            AsyncMarketIntelligenceClient(mock_client), method_name, kwargs
        )


class TestAsyncAlternativeListUnwrap:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,kwargs", _ALTERNATIVE_CASES)
    async def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        await _assert_wrap_single_and_empty_async(
            AsyncAlternativeMarketsClient(mock_client), method_name, kwargs
        )


class TestAsyncEconomicsListUnwrap:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,kwargs", _ECONOMICS_CASES)
    async def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        await _assert_wrap_single_and_empty_async(
            AsyncEconomicsClient(mock_client), method_name, kwargs
        )


class TestAsyncTechnicalListUnwrap:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,kwargs", _TECHNICAL_CASES)
    async def test_list_methods_wrap_single_and_keep_empty(
        self, mock_client, method_name, kwargs
    ):
        await _assert_wrap_single_and_empty_async(
            AsyncTechnicalClient(mock_client), method_name, kwargs
        )


class TestAlternativeHistoryUnwrap:
    """_wrap_history now unwraps rows then builds the container (#242)."""

    @pytest.mark.parametrize(
        "method_name,kwargs,container",
        [
            ("get_crypto_historical", {"symbol": "BTCUSD"}, CryptoHistoricalData),
            ("get_forex_historical", {"symbol": "EURUSD"}, ForexPriceHistory),
            ("get_commodity_historical", {"symbol": "GCUSD"}, CommodityPriceHistory),
        ],
    )
    def test_wrap_history_lone_row_and_empty(
        self, mock_client, monkeypatch, method_name, kwargs, container
    ):
        sentinel = object()
        mock_validate = MagicMock(return_value=sentinel)
        monkeypatch.setattr(container, "model_validate", mock_validate)
        client = AlternativeMarketsClient(mock_client)
        method = getattr(client, method_name)

        row = {"date": "2024-01-01"}
        mock_client.request.return_value = row
        assert method(**kwargs) is sentinel
        mock_validate.assert_called_with(
            {"symbol": kwargs["symbol"], "historical": [row]}
        )

        mock_validate.reset_mock()
        mock_client.request.return_value = []
        assert method(**kwargs) is sentinel
        mock_validate.assert_called_with({"symbol": kwargs["symbol"], "historical": []})

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method_name,kwargs,container",
        [
            ("get_crypto_historical", {"symbol": "BTCUSD"}, CryptoHistoricalData),
            ("get_forex_historical", {"symbol": "EURUSD"}, ForexPriceHistory),
            ("get_commodity_historical", {"symbol": "GCUSD"}, CommodityPriceHistory),
        ],
    )
    async def test_async_wrap_history_lone_row_and_empty(
        self, mock_client, monkeypatch, method_name, kwargs, container
    ):
        sentinel = object()
        mock_validate = MagicMock(return_value=sentinel)
        monkeypatch.setattr(container, "model_validate", mock_validate)
        client = AsyncAlternativeMarketsClient(mock_client)
        method = getattr(client, method_name)

        row = {"date": "2024-01-01"}
        mock_client.request_async.return_value = row
        assert await method(**kwargs) is sentinel
        mock_validate.assert_called_with(
            {"symbol": kwargs["symbol"], "historical": [row]}
        )

        mock_validate.reset_mock()
        mock_client.request_async.return_value = []
        assert await method(**kwargs) is sentinel
        mock_validate.assert_called_with({"symbol": kwargs["symbol"], "historical": []})


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
