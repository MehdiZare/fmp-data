# tests/unit/test_async_clients.py
"""Tests for async endpoint group clients."""

from datetime import date as dt_date
from unittest.mock import AsyncMock, MagicMock

import pytest

from fmp_data.alternative.models import CryptoQuote, ForexQuote
from fmp_data.batch._csv_utils import parse_csv_rows
from fmp_data.batch.models import BatchQuote, BatchQuoteShort
from fmp_data.company.models import (
    AftermarketQuote,
    AftermarketTrade,
    CompanyProfile,
    IntradayPrice,
    Quote,
    SimpleQuote,
    StockPriceChange,
)
from fmp_data.economics.models import TreasuryRate
from fmp_data.exceptions import InvalidSymbolError
from fmp_data.fundamental.models import BalanceSheet, IncomeStatement, OwnerEarnings
from fmp_data.index.models import IndexConstituent
from fmp_data.institutional.models import CIKMapping, InsiderTrade
from fmp_data.intelligence.models import (
    DividendEvent,
    StockNewsArticle,
    StockSplitEvent,
)
from fmp_data.investment.models import ETFInfo
from fmp_data.market.models import (
    CIKListEntry,
    CompanySearchResult,
    MarketMover,
)
from fmp_data.models import CompanySymbol
from fmp_data.sec.models import SECFiling8K
from fmp_data.technical.models import SMAIndicator
from fmp_data.transcripts.endpoints import EARNINGS_TRANSCRIPT
from fmp_data.transcripts.models import EarningsTranscript


@pytest.fixture
def mock_client():
    """Create a mock base client for testing async endpoint groups."""
    client = MagicMock()
    client.request_async = AsyncMock()
    return client


class TestAsyncCompanyClient:
    """Tests for AsyncCompanyClient."""

    @pytest.mark.asyncio
    async def test_get_profile(self, mock_client):
        """Test async get_profile method."""
        from fmp_data.company.async_client import AsyncCompanyClient

        profile_data = {
            "symbol": "AAPL",
            "companyName": "Apple Inc.",
            "price": 150.0,
            "mktCap": 2500000000000,
            "currency": "USD",
            "exchangeShortName": "NASDAQ",
        }
        mock_client.request_async.return_value = [CompanyProfile(**profile_data)]

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_profile("AAPL")

        assert isinstance(result, CompanyProfile)
        assert result.symbol == "AAPL"

    @pytest.mark.asyncio
    async def test_get_profile_raises_for_empty_result(self, mock_client):
        """Test get_profile raises when no profile is returned."""
        from fmp_data.company.async_client import AsyncCompanyClient
        from fmp_data.exceptions import FMPError

        mock_client.request_async.return_value = []

        async_client = AsyncCompanyClient(mock_client)
        with pytest.raises(FMPError, match="Symbol AAPL not found"):
            await async_client.get_profile("AAPL")

    @pytest.mark.asyncio
    async def test_get_quote(self, mock_client):
        """Test async get_quote method."""
        from fmp_data.company.async_client import AsyncCompanyClient

        quote_data = {
            "symbol": "AAPL",
            "price": 150.0,
            "changesPercentage": 1.5,
            "changePercentage": 1.5,
            "change": 2.25,
            "dayLow": 148.0,
            "dayHigh": 152.0,
            "yearHigh": 180.0,
            "yearLow": 120.0,
            "priceAvg50": 155.0,
            "priceAvg200": 160.0,
            "volume": 50000000,
            "avgVolume": 45000000,
            "open": 149.0,
            "previousClose": 147.75,
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "marketCap": 2500000000000,
            "timestamp": 1704067200,
        }
        mock_client.request_async.return_value = [Quote(**quote_data)]

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_quote("AAPL")

        assert isinstance(result, Quote)
        assert result.symbol == "AAPL"

    @pytest.mark.asyncio
    async def test_get_simple_quote(self, mock_client):
        """Test async get_simple_quote method."""
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.request_async.return_value = [
            SimpleQuote(symbol="AAPL", price=150.0, volume=50000000)
        ]

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_simple_quote("AAPL")

        assert isinstance(result, SimpleQuote)
        assert result.symbol == "AAPL"

    @pytest.mark.asyncio
    async def test_get_core_information_empty_returns_none(self, mock_client):
        """Test get_core_information returns None on empty response."""
        from fmp_data.company import endpoints as company_endpoints
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.request_async.return_value = []

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_core_information("AAPL")

        assert result is None
        mock_client.request_async.assert_called_once_with(
            company_endpoints.CORE_INFORMATION, symbol="AAPL"
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method_name,endpoint_name",
        [
            ("get_executives", "KEY_EXECUTIVES"),
            ("get_employee_count", "EMPLOYEE_COUNT"),
            ("get_company_notes", "COMPANY_NOTES"),
        ],
    )
    async def test_company_simple_list_endpoints(
        self, mock_client, method_name, endpoint_name
    ):
        """Test company list endpoints forward symbol."""
        from fmp_data.company import endpoints as company_endpoints
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.request_async.return_value = []

        async_client = AsyncCompanyClient(mock_client)
        method = getattr(async_client, method_name)
        result = await method("AAPL")

        assert result == []
        endpoint = getattr(company_endpoints, endpoint_name)
        mock_client.request_async.assert_called_once_with(endpoint, symbol="AAPL")

    @pytest.mark.asyncio
    async def test_get_aftermarket_trade(self, mock_client):
        """Test async get_aftermarket_trade method."""
        from fmp_data.company.async_client import AsyncCompanyClient

        trade_data = {
            "symbol": "AAPL",
            "price": 232.53,
            "tradeSize": 132,
            "timestamp": 1738715334311,
        }
        mock_client.request_async.return_value = [AftermarketTrade(**trade_data)]

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_aftermarket_trade("AAPL")

        assert isinstance(result, AftermarketTrade)
        assert result.symbol == "AAPL"

    @pytest.mark.asyncio
    async def test_get_aftermarket_quote(self, mock_client):
        """Test async get_aftermarket_quote method."""
        from fmp_data.company.async_client import AsyncCompanyClient

        quote_data = {
            "symbol": "AAPL",
            "bidSize": 1,
            "bidPrice": 232.45,
            "askSize": 3,
            "askPrice": 232.64,
            "volume": 41647042,
            "timestamp": 1738715334311,
        }
        mock_client.request_async.return_value = [AftermarketQuote(**quote_data)]

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_aftermarket_quote("AAPL")

        assert isinstance(result, AftermarketQuote)
        assert result.symbol == "AAPL"

    @pytest.mark.asyncio
    async def test_get_stock_price_change(self, mock_client):
        """Test async get_stock_price_change method."""
        from fmp_data.company.async_client import AsyncCompanyClient

        change_data = {
            "symbol": "AAPL",
            "1D": 2.1008,
            "5D": -2.45946,
            "1M": -4.33925,
            "3M": 4.86014,
            "6M": 5.88556,
            "ytd": -4.53147,
            "1Y": 24.04092,
            "3Y": 35.04264,
            "5Y": 192.05871,
            "10Y": 678.8558,
            "max": 181279.04168,
        }
        mock_client.request_async.return_value = [StockPriceChange(**change_data)]

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_stock_price_change("AAPL")

        assert isinstance(result, StockPriceChange)
        assert result.one_day == 2.1008

    @pytest.mark.asyncio
    async def test_get_dividends_with_limit(self, mock_client):
        """Test async get_dividends with limit."""
        from fmp_data.company import endpoints as company_endpoints
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_dividend = MagicMock(spec=DividendEvent)
        mock_client.request_async.return_value = [mock_dividend]

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_dividends("AAPL", limit=5)

        assert len(result) == 1
        mock_client.request_async.assert_called_once_with(
            company_endpoints.COMPANY_DIVIDENDS, symbol="AAPL", limit=5
        )

    @pytest.mark.asyncio
    async def test_get_stock_splits_with_limit(self, mock_client):
        """Test async get_stock_splits with limit."""
        from fmp_data.company import endpoints as company_endpoints
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_split = MagicMock(spec=StockSplitEvent)
        mock_client.request_async.return_value = [mock_split]

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_stock_splits("AAPL", limit=5)

        assert len(result) == 1
        mock_client.request_async.assert_called_once_with(
            company_endpoints.COMPANY_SPLITS, symbol="AAPL", limit=5
        )

    @pytest.mark.asyncio
    async def test_get_intraday_prices_with_filters(self, mock_client):
        """Test async get_intraday_prices with filters."""
        from fmp_data.company import endpoints as company_endpoints
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_price = MagicMock(spec=IntradayPrice)
        mock_client.request_async.return_value = [mock_price]

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_intraday_prices(
            "AAPL",
            interval="1min",
            from_date=dt_date(2025, 2, 1),
            to_date=dt_date(2025, 2, 4),
            nonadjusted=True,
        )

        assert len(result) == 1
        mock_client.request_async.assert_called_once_with(
            company_endpoints.INTRADAY_PRICE,
            symbol="AAPL",
            interval="1min",
            start_date="2025-02-01",
            end_date="2025-02-04",
            nonadjusted=True,
        )

    def test_get_company_logo_url_strips_trailing_slash(self, mock_client):
        """Test get_company_logo_url normalizes the base URL."""
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.config = MagicMock(base_url="https://example.com/")
        async_client = AsyncCompanyClient(mock_client)

        result = async_client.get_company_logo_url("AAPL")

        assert result == "https://example.com/image-stock/AAPL.png"

    def test_get_company_logo_url_requires_symbol(self, mock_client):
        """Test get_company_logo_url rejects empty symbols."""
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.config = MagicMock(base_url="https://example.com/")
        async_client = AsyncCompanyClient(mock_client)

        with pytest.raises(InvalidSymbolError, match="Symbol is required"):
            async_client.get_company_logo_url(" ")

    @pytest.mark.asyncio
    async def test_get_historical_prices_wraps_single_result(self, mock_client):
        """Test get_historical_prices wraps non-list results."""
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.request_async.return_value = {"date": "2024-01-01"}

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_historical_prices("AAPL")

        assert result.symbol == "AAPL"
        assert len(result.historical) == 1
        assert result.historical[0].date.date() == dt_date(2024, 1, 1)

    @pytest.mark.asyncio
    async def test_get_historical_prices_with_date_filters(self, mock_client):
        """Test get_historical_prices forwards date filters."""
        from fmp_data.company import endpoints as company_endpoints
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.request_async.return_value = [{"date": "2024-01-01"}]

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_historical_prices(
            "AAPL", from_date=dt_date(2024, 1, 1), to_date=dt_date(2024, 1, 31)
        )

        assert result.symbol == "AAPL"
        assert len(result.historical) == 1
        mock_client.request_async.assert_called_once_with(
            company_endpoints.HISTORICAL_PRICE,
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method_name,endpoint_name,response",
        [
            (
                "get_historical_prices_light",
                "HISTORICAL_PRICE_LIGHT",
                {"date": "2024-01-02"},
            ),
            (
                "get_historical_prices_non_split_adjusted",
                "HISTORICAL_PRICE_NON_SPLIT_ADJUSTED",
                [{"date": "2024-01-03"}],
            ),
            (
                "get_historical_prices_dividend_adjusted",
                "HISTORICAL_PRICE_DIVIDEND_ADJUSTED",
                [{"date": "2024-01-04"}],
            ),
        ],
    )
    async def test_historical_price_variants(
        self, mock_client, method_name, endpoint_name, response
    ):
        """Test historical price variants handle list and dict results."""
        from fmp_data.company import endpoints as company_endpoints
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.request_async.return_value = response

        async_client = AsyncCompanyClient(mock_client)
        method = getattr(async_client, method_name)
        result = await method(
            "AAPL",
            from_date=dt_date(2024, 1, 1),
            to_date=dt_date(2024, 1, 10),
        )

        assert result.symbol == "AAPL"
        assert len(result.historical) == 1
        endpoint = getattr(company_endpoints, endpoint_name)
        mock_client.request_async.assert_called_once_with(
            endpoint,
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-01-10",
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method_name,endpoint_name",
        [
            ("get_product_revenue_segmentation", "PRODUCT_REVENUE_SEGMENTATION"),
            ("get_geographic_revenue_segmentation", "GEOGRAPHIC_REVENUE_SEGMENTATION"),
        ],
    )
    async def test_revenue_segmentation_params(
        self, mock_client, method_name, endpoint_name
    ):
        """Test revenue segmentation uses flat structure and period."""
        from fmp_data.company import endpoints as company_endpoints
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.request_async.return_value = []
        async_client = AsyncCompanyClient(mock_client)

        method = getattr(async_client, method_name)
        result = await method("AAPL", period="quarter")

        assert result == []
        endpoint = getattr(company_endpoints, endpoint_name)
        mock_client.request_async.assert_called_once_with(
            endpoint,
            symbol="AAPL",
            structure="flat",
            period="quarter",
        )

    @pytest.mark.asyncio
    async def test_get_analyst_estimates_params(self, mock_client):
        """Test analyst estimates parameter forwarding."""
        from fmp_data.company import endpoints as company_endpoints
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.request_async.return_value = []
        async_client = AsyncCompanyClient(mock_client)

        result = await async_client.get_analyst_estimates(
            "AAPL", period="quarter", page=2, limit=5
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            company_endpoints.ANALYST_ESTIMATES,
            symbol="AAPL",
            period="quarter",
            page=2,
            limit=5,
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method_name,endpoint_name",
        [
            ("get_dividends", "COMPANY_DIVIDENDS"),
            ("get_stock_splits", "COMPANY_SPLITS"),
        ],
    )
    async def test_company_date_range_endpoints(
        self, mock_client, method_name, endpoint_name
    ):
        """Test dividend and split endpoints include date filters."""
        from fmp_data.company import endpoints as company_endpoints
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.request_async.return_value = []
        async_client = AsyncCompanyClient(mock_client)

        method = getattr(async_client, method_name)
        result = await method(
            "AAPL",
            from_date=dt_date(2024, 1, 1),
            to_date=dt_date(2024, 2, 1),
            limit=3,
        )

        assert result == []
        endpoint = getattr(company_endpoints, endpoint_name)
        mock_client.request_async.assert_called_once_with(
            endpoint,
            symbol="AAPL",
            from_date="2024-01-01",
            to_date="2024-02-01",
            limit=3,
        )

    @pytest.mark.asyncio
    async def test_get_upgrades_downgrades_consensus_empty_list(self, mock_client):
        """Test upgrades/downgrades consensus returns None on empty list."""
        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.request_async.return_value = []

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_upgrades_downgrades_consensus("AAPL")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_upgrades_downgrades_consensus_list_returns_first(
        self, mock_client
    ):
        """Test upgrades/downgrades consensus returns first list item."""
        from fmp_data.company.async_client import AsyncCompanyClient

        sentinel = MagicMock()
        mock_client.request_async.return_value = [sentinel]

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_upgrades_downgrades_consensus("AAPL")

        assert result is sentinel

    @pytest.mark.asyncio
    async def test_get_upgrades_downgrades_consensus_object(self, mock_client):
        """Test upgrades/downgrades consensus accepts non-list response."""
        from fmp_data.company.async_client import AsyncCompanyClient

        sentinel = MagicMock()
        mock_client.request_async.return_value = sentinel

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_upgrades_downgrades_consensus("AAPL")

        assert result is sentinel


class TestAsyncMarketClient:
    """Tests for AsyncMarketClient."""

    @pytest.mark.asyncio
    async def test_get_gainers(self, mock_client):
        """Test async get_gainers method."""
        from fmp_data.market.async_client import AsyncMarketClient

        mock_client.request_async.return_value = [
            MarketMover(
                symbol="AAPL",
                name="Apple Inc.",
                change=5.0,
                price=155.0,
                changesPercentage=3.5,
            )
        ]

        async_client = AsyncMarketClient(mock_client)
        result = await async_client.get_gainers()

        assert len(result) == 1
        assert isinstance(result[0], MarketMover)

    @pytest.mark.asyncio
    async def test_search_symbol(self, mock_client):
        """Test async search_symbol method."""
        from fmp_data.market.async_client import AsyncMarketClient
        from fmp_data.market.endpoints import SEARCH_SYMBOL

        mock_client.request_async.return_value = [
            CompanySearchResult(symbol="AAPL", name="Apple Inc.")
        ]

        async_client = AsyncMarketClient(mock_client)
        result = await async_client.search_symbol("Apple", limit=5, exchange="NASDAQ")

        assert len(result) == 1
        assert isinstance(result[0], CompanySearchResult)
        mock_client.request_async.assert_called_once_with(
            SEARCH_SYMBOL, query="Apple", limit=5, exchange="NASDAQ"
        )

    @pytest.mark.asyncio
    async def test_search_exchange_variants(self, mock_client):
        """Test async search_exchange_variants method."""
        from fmp_data.market.async_client import AsyncMarketClient
        from fmp_data.market.endpoints import SEARCH_EXCHANGE_VARIANTS

        mock_client.request_async.return_value = [
            CompanySearchResult(symbol="AAPL", name="Apple Inc.")
        ]

        async_client = AsyncMarketClient(mock_client)
        result = await async_client.search_exchange_variants("Apple")

        assert len(result) == 1
        assert isinstance(result[0], CompanySearchResult)
        mock_client.request_async.assert_called_once_with(
            SEARCH_EXCHANGE_VARIANTS, query="Apple"
        )

    @pytest.mark.asyncio
    async def test_get_financial_statement_symbol_list(self, mock_client):
        """Test async get_financial_statement_symbol_list method."""
        from fmp_data.market.async_client import AsyncMarketClient
        from fmp_data.market.endpoints import FINANCIAL_STATEMENT_SYMBOL_LIST

        mock_client.request_async.return_value = [
            CompanySymbol(symbol="AAPL", name="Apple Inc.")
        ]

        async_client = AsyncMarketClient(mock_client)
        result = await async_client.get_financial_statement_symbol_list()

        assert len(result) == 1
        assert isinstance(result[0], CompanySymbol)
        mock_client.request_async.assert_called_once_with(
            FINANCIAL_STATEMENT_SYMBOL_LIST
        )

    @pytest.mark.asyncio
    async def test_get_actively_trading_list(self, mock_client):
        """Test async get_actively_trading_list method."""
        from fmp_data.market.async_client import AsyncMarketClient
        from fmp_data.market.endpoints import ACTIVELY_TRADING_LIST

        mock_client.request_async.return_value = [
            CompanySymbol(symbol="AAPL", name="Apple Inc.")
        ]

        async_client = AsyncMarketClient(mock_client)
        result = await async_client.get_actively_trading_list()

        assert len(result) == 1
        assert isinstance(result[0], CompanySymbol)
        mock_client.request_async.assert_called_once_with(ACTIVELY_TRADING_LIST)

    @pytest.mark.asyncio
    async def test_get_tradable_list(self, mock_client):
        """Test async get_tradable_list method."""
        from fmp_data.market.async_client import AsyncMarketClient
        from fmp_data.market.endpoints import TRADABLE_SEARCH

        mock_client.request_async.return_value = [
            CompanySymbol(symbol="AAPL", name="Apple Inc.")
        ]

        async_client = AsyncMarketClient(mock_client)
        result = await async_client.get_tradable_list(limit=5, offset=10)

        assert len(result) == 1
        assert isinstance(result[0], CompanySymbol)
        mock_client.request_async.assert_called_once_with(
            TRADABLE_SEARCH, limit=5, offset=10
        )

    @pytest.mark.asyncio
    async def test_get_cik_list(self, mock_client):
        """Test async get_cik_list method."""
        from fmp_data.market.async_client import AsyncMarketClient
        from fmp_data.market.endpoints import CIK_LIST

        mock_client.request_async.return_value = [
            CIKListEntry(cik="0000320193", company_name="Apple Inc.")
        ]

        async_client = AsyncMarketClient(mock_client)
        result = await async_client.get_cik_list(page=1, limit=20)

        assert len(result) == 1
        assert isinstance(result[0], CIKListEntry)
        mock_client.request_async.assert_called_once_with(CIK_LIST, page=1, limit=20)

    @pytest.mark.asyncio
    async def test_get_company_screener(self, mock_client):
        """Test async get_company_screener method."""
        from fmp_data.market.async_client import AsyncMarketClient
        from fmp_data.market.endpoints import COMPANY_SCREENER

        mock_client.request_async.return_value = [
            CompanySearchResult(symbol="AAPL", name="Apple Inc.")
        ]

        async_client = AsyncMarketClient(mock_client)
        result = await async_client.get_company_screener(
            market_cap_more_than=1_000_000_000,
            is_etf=False,
            sector="Technology",
            limit=5,
        )

        assert len(result) == 1
        assert isinstance(result[0], CompanySearchResult)
        mock_client.request_async.assert_called_once_with(
            COMPANY_SCREENER,
            market_cap_more_than=1_000_000_000,
            is_etf=False,
            sector="Technology",
            limit=5,
        )

    @pytest.mark.asyncio
    async def test_search_company_with_filters(self, mock_client):
        """Test async search_company method with optional filters."""
        from fmp_data.market.async_client import AsyncMarketClient
        from fmp_data.market.endpoints import SEARCH_COMPANY

        mock_client.request_async.return_value = [
            CompanySearchResult(symbol="AAPL", name="Apple Inc.")
        ]

        async_client = AsyncMarketClient(mock_client)
        result = await async_client.search_company("Apple", limit=3, exchange="NASDAQ")

        assert len(result) == 1
        mock_client.request_async.assert_called_once_with(
            SEARCH_COMPANY,
            query="Apple",
            limit=3,
            exchange="NASDAQ",
        )

    @pytest.mark.asyncio
    async def test_get_market_hours_success(self, mock_client):
        """Test get_market_hours returns the first entry."""
        from fmp_data.market.async_client import AsyncMarketClient
        from fmp_data.market.endpoints import MARKET_HOURS

        mock_hours = MagicMock()
        mock_client.request_async.return_value = [mock_hours]

        async_client = AsyncMarketClient(mock_client)
        result = await async_client.get_market_hours(exchange="NASDAQ")

        assert result is mock_hours
        mock_client.request_async.assert_called_once_with(
            MARKET_HOURS, exchange="NASDAQ"
        )

    @pytest.mark.asyncio
    async def test_get_market_hours_empty_raises(self, mock_client):
        """Test get_market_hours raises when API returns no data."""
        from fmp_data.market.async_client import AsyncMarketClient

        mock_client.request_async.return_value = []

        async_client = AsyncMarketClient(mock_client)
        with pytest.raises(ValueError, match="No market hours data"):
            await async_client.get_market_hours(exchange="NYSE")

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method_name,kwargs,endpoint_name,expected_kwargs",
        [
            ("get_stock_list", {}, "STOCK_LIST", {}),
            ("get_etf_list", {}, "ETF_LIST", {}),
            ("get_available_indexes", {}, "AVAILABLE_INDEXES", {}),
            (
                "search_by_cik",
                {"query": "0000320193"},
                "CIK_SEARCH",
                {"query": "0000320193"},
            ),
            (
                "search_by_cusip",
                {"query": "037833100"},
                "CUSIP_SEARCH",
                {"query": "037833100"},
            ),
            (
                "search_by_isin",
                {"query": "US0378331005"},
                "ISIN_SEARCH",
                {"query": "US0378331005"},
            ),
            (
                "get_all_exchange_market_hours",
                {},
                "ALL_EXCHANGE_MARKET_HOURS",
                {},
            ),
            (
                "get_holidays_by_exchange",
                {"exchange": "NASDAQ"},
                "HOLIDAYS_BY_EXCHANGE",
                {"exchange": "NASDAQ"},
            ),
            ("get_losers", {}, "LOSERS", {}),
            ("get_most_active", {}, "MOST_ACTIVE", {}),
            ("get_pre_post_market", {}, "PRE_POST_MARKET", {}),
            ("get_all_shares_float", {}, "ALL_SHARES_FLOAT", {}),
            ("get_available_exchanges", {}, "AVAILABLE_EXCHANGES", {}),
            ("get_available_sectors", {}, "AVAILABLE_SECTORS", {}),
            ("get_available_industries", {}, "AVAILABLE_INDUSTRIES", {}),
            ("get_available_countries", {}, "AVAILABLE_COUNTRIES", {}),
        ],
    )
    async def test_market_simple_endpoints(
        self, mock_client, method_name, kwargs, endpoint_name, expected_kwargs
    ):
        """Test async market endpoints that only forward params."""
        from fmp_data.market import endpoints as market_endpoints
        from fmp_data.market.async_client import AsyncMarketClient

        mock_client.request_async.return_value = []
        async_client = AsyncMarketClient(mock_client)

        method = getattr(async_client, method_name)
        result = await method(**kwargs)

        assert result == []
        endpoint = getattr(market_endpoints, endpoint_name)
        if expected_kwargs:
            mock_client.request_async.assert_called_once_with(
                endpoint, **expected_kwargs
            )
        else:
            mock_client.request_async.assert_called_once_with(endpoint)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method_name,kwargs,endpoint_name,expected_kwargs",
        [
            (
                "get_sector_performance",
                {
                    "sector": "Technology",
                    "exchange": "NYSE",
                    "date": dt_date(2024, 1, 2),
                },
                "SECTOR_PERFORMANCE",
                {"sector": "Technology", "exchange": "NYSE", "date": "2024-01-02"},
            ),
            (
                "get_industry_performance_snapshot",
                {
                    "industry": "Software",
                    "exchange": "NASDAQ",
                    "date": dt_date(2024, 2, 3),
                },
                "INDUSTRY_PERFORMANCE_SNAPSHOT",
                {"industry": "Software", "exchange": "NASDAQ", "date": "2024-02-03"},
            ),
            (
                "get_historical_sector_performance",
                {
                    "sector": "Technology",
                    "from_date": dt_date(2024, 1, 1),
                    "to_date": dt_date(2024, 1, 31),
                    "exchange": "NYSE",
                },
                "HISTORICAL_SECTOR_PERFORMANCE",
                {
                    "sector": "Technology",
                    "from": "2024-01-01",
                    "to": "2024-01-31",
                    "exchange": "NYSE",
                },
            ),
            (
                "get_historical_industry_performance",
                {
                    "industry": "Software",
                    "from_date": dt_date(2024, 1, 1),
                    "to_date": dt_date(2024, 1, 31),
                    "exchange": "NASDAQ",
                },
                "HISTORICAL_INDUSTRY_PERFORMANCE",
                {
                    "industry": "Software",
                    "from": "2024-01-01",
                    "to": "2024-01-31",
                    "exchange": "NASDAQ",
                },
            ),
            (
                "get_sector_pe_snapshot",
                {
                    "sector": "Energy",
                    "exchange": "NYSE",
                    "date": dt_date(2024, 3, 1),
                },
                "SECTOR_PE_SNAPSHOT",
                {"sector": "Energy", "exchange": "NYSE", "date": "2024-03-01"},
            ),
            (
                "get_industry_pe_snapshot",
                {
                    "industry": "Banks",
                    "exchange": "NYSE",
                    "date": dt_date(2024, 3, 1),
                },
                "INDUSTRY_PE_SNAPSHOT",
                {"industry": "Banks", "exchange": "NYSE", "date": "2024-03-01"},
            ),
            (
                "get_historical_sector_pe",
                {
                    "sector": "Energy",
                    "from_date": dt_date(2024, 1, 1),
                    "to_date": dt_date(2024, 1, 31),
                    "exchange": "NYSE",
                },
                "HISTORICAL_SECTOR_PE",
                {
                    "sector": "Energy",
                    "from": "2024-01-01",
                    "to": "2024-01-31",
                    "exchange": "NYSE",
                },
            ),
            (
                "get_historical_industry_pe",
                {
                    "industry": "Banks",
                    "from_date": dt_date(2024, 1, 1),
                    "to_date": dt_date(2024, 1, 31),
                    "exchange": "NYSE",
                },
                "HISTORICAL_INDUSTRY_PE",
                {
                    "industry": "Banks",
                    "from": "2024-01-01",
                    "to": "2024-01-31",
                    "exchange": "NYSE",
                },
            ),
            (
                "get_ipo_disclosure",
                {
                    "from_date": dt_date(2024, 1, 1),
                    "to_date": dt_date(2024, 1, 31),
                    "limit": 50,
                },
                "IPO_DISCLOSURE",
                {"from": "2024-01-01", "to": "2024-01-31", "limit": 50},
            ),
            (
                "get_ipo_prospectus",
                {
                    "from_date": dt_date(2024, 1, 1),
                    "to_date": dt_date(2024, 1, 31),
                    "limit": 75,
                },
                "IPO_PROSPECTUS",
                {"from": "2024-01-01", "to": "2024-01-31", "limit": 75},
            ),
        ],
    )
    async def test_market_date_param_endpoints(
        self, mock_client, method_name, kwargs, endpoint_name, expected_kwargs
    ):
        """Test market endpoints that format dates or build params."""
        from fmp_data.market import endpoints as market_endpoints
        from fmp_data.market.async_client import AsyncMarketClient

        mock_client.request_async.return_value = []
        async_client = AsyncMarketClient(mock_client)

        method = getattr(async_client, method_name)
        result = await method(**kwargs)

        assert result == []
        endpoint = getattr(market_endpoints, endpoint_name)
        mock_client.request_async.assert_called_once_with(endpoint, **expected_kwargs)


class TestAsyncFundamentalClient:
    """Tests for AsyncFundamentalClient."""

    @pytest.mark.asyncio
    async def test_get_income_statement(self, mock_client):
        """Test async get_income_statement method."""
        from fmp_data.fundamental.async_client import AsyncFundamentalClient

        # Use MagicMock for complex models to avoid validation issues
        mock_income = MagicMock(spec=IncomeStatement)
        mock_income.symbol = "AAPL"
        mock_client.request_async.return_value = [mock_income]

        async_client = AsyncFundamentalClient(mock_client)
        result = await async_client.get_income_statement("AAPL")

        assert len(result) == 1
        assert result[0].symbol == "AAPL"
        mock_client.request_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_balance_sheet(self, mock_client):
        """Test async get_balance_sheet method."""
        from fmp_data.fundamental.async_client import AsyncFundamentalClient

        # Use MagicMock for complex models to avoid validation issues
        mock_balance = MagicMock(spec=BalanceSheet)
        mock_balance.symbol = "AAPL"
        mock_client.request_async.return_value = [mock_balance]

        async_client = AsyncFundamentalClient(mock_client)
        result = await async_client.get_balance_sheet("AAPL")

        assert len(result) == 1
        assert result[0].symbol == "AAPL"
        mock_client.request_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_latest_financial_statements(self, mock_client):
        """Test async get_latest_financial_statements method."""
        from fmp_data.fundamental import endpoints as fundamental_endpoints
        from fmp_data.fundamental.async_client import AsyncFundamentalClient

        mock_client.request_async.return_value = []
        async_client = AsyncFundamentalClient(mock_client)
        result = await async_client.get_latest_financial_statements(page=0, limit=250)

        assert result == []
        mock_client.request_async.assert_called_once_with(
            fundamental_endpoints.LATEST_FINANCIAL_STATEMENTS, page=0, limit=250
        )

    @pytest.mark.asyncio
    async def test_get_owner_earnings(self, mock_client):
        """Test async get_owner_earnings method."""
        from fmp_data.fundamental import endpoints as fundamental_endpoints
        from fmp_data.fundamental.async_client import AsyncFundamentalClient

        mock_owner = MagicMock(spec=OwnerEarnings)
        mock_owner.symbol = "AAPL"
        mock_client.request_async.return_value = [mock_owner]

        async_client = AsyncFundamentalClient(mock_client)
        result = await async_client.get_owner_earnings("AAPL", limit=5)

        assert len(result) == 1
        assert result[0].symbol == "AAPL"
        mock_client.request_async.assert_called_once_with(
            fundamental_endpoints.OWNER_EARNINGS, symbol="AAPL", limit=5
        )


class TestAsyncTechnicalClient:
    """Tests for AsyncTechnicalClient."""

    @pytest.mark.asyncio
    async def test_get_sma(self, mock_client):
        """Test async get_sma method."""
        from fmp_data.technical.async_client import AsyncTechnicalClient

        mock_client.request_async.return_value = [
            SMAIndicator(
                date="2024-01-01",
                open=150.0,
                high=155.0,
                low=148.0,
                close=152.0,
                volume=50000000,
                sma=151.5,
            )
        ]

        async_client = AsyncTechnicalClient(mock_client)
        result = await async_client.get_sma("AAPL", period_length=20)

        assert len(result) == 1
        assert isinstance(result[0], SMAIndicator)

    @pytest.mark.asyncio
    async def test_get_sma_normalizes_interval(self, mock_client):
        """Test interval normalization for SMA requests."""
        from fmp_data.technical import endpoints as technical_endpoints
        from fmp_data.technical.async_client import AsyncTechnicalClient

        mock_client.request_async.return_value = []

        async_client = AsyncTechnicalClient(mock_client)
        result = await async_client.get_sma(
            "AAPL",
            period_length=14,
            timeframe="4hour",
            interval="daily",
            start_date=dt_date(2024, 1, 1),
            end_date=dt_date(2024, 1, 10),
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            technical_endpoints.SMA,
            symbol="AAPL",
            periodLength=14,
            timeframe="1day",
            **{"from": "2024-01-01", "to": "2024-01-10"},
        )


class TestAsyncIntelligenceClient:
    """Tests for AsyncMarketIntelligenceClient."""

    @pytest.mark.asyncio
    async def test_get_stock_news(self, mock_client):
        """Test async get_stock_news method."""
        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient

        mock_client.request_async.return_value = [
            StockNewsArticle(
                symbol="AAPL",
                publishedDate="2024-01-01T12:00:00",
                title="Test News",
                text="Test news content",
                url="https://example.com",
                site="Example Site",
            )
        ]

        async_client = AsyncMarketIntelligenceClient(mock_client)
        result = await async_client.get_stock_news()

        assert len(result) == 1
        assert isinstance(result[0], StockNewsArticle)

    @pytest.mark.asyncio
    async def test_get_stock_news_delegates_to_symbol_news(self, mock_client):
        """Test get_stock_news uses symbol-specific endpoint."""
        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient

        async_client = AsyncMarketIntelligenceClient(mock_client)
        async_client.get_stock_symbol_news = AsyncMock(return_value=["sentinel"])

        result = await async_client.get_stock_news(
            symbol="AAPL",
            page=2,
            limit=5,
        )

        assert result == ["sentinel"]
        async_client.get_stock_symbol_news.assert_awaited_once_with(
            symbol="AAPL",
            page=2,
            from_date=None,
            to_date=None,
            limit=5,
        )

    @pytest.mark.asyncio
    async def test_get_earnings_calendar_formats_dates(self, mock_client):
        """Test earnings calendar date formatting."""
        from fmp_data.intelligence import endpoints as intelligence_endpoints
        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient

        mock_client.request_async.return_value = []
        async_client = AsyncMarketIntelligenceClient(mock_client)

        result = await async_client.get_earnings_calendar(
            dt_date(2024, 1, 1), dt_date(2024, 1, 15)
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            intelligence_endpoints.EARNINGS_CALENDAR,
            start_date="2024-01-01",
            end_date="2024-01-15",
        )

    def test_build_date_params_custom_keys(self):
        """Test _build_date_params supports custom keys."""
        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient

        params = AsyncMarketIntelligenceClient._build_date_params(
            start_date=dt_date(2024, 1, 1),
            end_date=dt_date(2024, 1, 2),
            start_key="from",
            end_key="to",
        )

        assert params == {"from": "2024-01-01", "to": "2024-01-02"}

    @pytest.mark.asyncio
    async def test_get_fmp_articles_size_alias(self, mock_client):
        """Test size alias overrides limit for FMP articles."""
        from datetime import datetime

        from fmp_data.intelligence import endpoints as intelligence_endpoints
        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient
        from fmp_data.intelligence.models import FMPArticle, FMPArticlesResponse

        article = FMPArticle(
            title="Test",
            date=datetime(2024, 1, 1, 12, 0, 0),
            content="content",
            link="https://example.com/article",
            image="https://example.com/image.png",
            author="Author",
            site="Example",
        )
        mock_client.request_async.return_value = FMPArticlesResponse(content=[article])

        async_client = AsyncMarketIntelligenceClient(mock_client)
        result = await async_client.get_fmp_articles(page=2, limit=20, size=5)

        assert result == [article]
        mock_client.request_async.assert_called_once_with(
            intelligence_endpoints.FMP_ARTICLES_ENDPOINT,
            page=2,
            limit=5,
        )

    @pytest.mark.asyncio
    async def test_get_fmp_articles_returns_list_response(self, mock_client):
        """Test get_fmp_articles returns list responses."""
        from datetime import datetime

        from fmp_data.intelligence import endpoints as intelligence_endpoints
        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient
        from fmp_data.intelligence.models import FMPArticle

        article = FMPArticle(
            title="Test",
            date=datetime(2024, 1, 1, 12, 0, 0),
            content="content",
            link="https://example.com/article",
            image="https://example.com/image.png",
            author="Author",
            site="Example",
        )
        mock_client.request_async.return_value = [article]

        async_client = AsyncMarketIntelligenceClient(mock_client)
        result = await async_client.get_fmp_articles()

        assert result == [article]
        mock_client.request_async.assert_called_once_with(
            intelligence_endpoints.FMP_ARTICLES_ENDPOINT,
            page=0,
            limit=20,
        )

    @pytest.mark.asyncio
    async def test_get_general_news_formats_dates(self, mock_client):
        """Test general news date formatting."""
        from fmp_data.intelligence import endpoints as intelligence_endpoints
        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient

        mock_client.request_async.return_value = []
        async_client = AsyncMarketIntelligenceClient(mock_client)

        result = await async_client.get_general_news(
            page=1,
            from_date=dt_date(2024, 1, 1),
            to_date=dt_date(2024, 1, 5),
            limit=10,
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            intelligence_endpoints.GENERAL_NEWS_ENDPOINT,
            page=1,
            start_date="2024-01-01",
            end_date="2024-01-05",
            limit=10,
        )

    @pytest.mark.asyncio
    async def test_get_stock_symbol_news_formats_dates(self, mock_client):
        """Test stock symbol news date formatting."""
        from fmp_data.intelligence import endpoints as intelligence_endpoints
        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient

        mock_client.request_async.return_value = []
        async_client = AsyncMarketIntelligenceClient(mock_client)

        result = await async_client.get_stock_symbol_news(
            "AAPL",
            page=2,
            from_date=dt_date(2024, 1, 3),
            to_date=dt_date(2024, 1, 7),
            limit=15,
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            intelligence_endpoints.STOCK_SYMBOL_NEWS_ENDPOINT,
            symbol="AAPL",
            page=2,
            start_date="2024-01-03",
            end_date="2024-01-07",
            limit=15,
        )

    @pytest.mark.asyncio
    async def test_get_forex_news_delegates_to_symbol(self, mock_client):
        """Test forex news delegates when symbol provided."""
        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient

        async_client = AsyncMarketIntelligenceClient(mock_client)
        async_client.get_forex_symbol_news = AsyncMock(return_value=["sentinel"])

        result = await async_client.get_forex_news(symbol="EURUSD", page=1, limit=5)

        assert result == ["sentinel"]
        async_client.get_forex_symbol_news.assert_awaited_once_with(
            symbol="EURUSD",
            page=1,
            from_date=None,
            to_date=None,
            limit=5,
        )

    @pytest.mark.asyncio
    async def test_get_crypto_news_defaults_to_today(self, mock_client, monkeypatch):
        """Test crypto news defaults end_date when from_date is set."""
        from fmp_data.intelligence import async_client as intelligence_async
        from fmp_data.intelligence import endpoints as intelligence_endpoints
        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient

        class FixedDate(dt_date):
            @classmethod
            def today(cls):  # type: ignore[override]
                return dt_date(2024, 2, 1)

        monkeypatch.setattr(intelligence_async, "date", FixedDate)
        mock_client.request_async.return_value = []

        async_client = AsyncMarketIntelligenceClient(mock_client)
        result = await async_client.get_crypto_news(from_date=dt_date(2024, 1, 15))

        assert result == []
        mock_client.request_async.assert_called_once_with(
            intelligence_endpoints.CRYPTO_NEWS_ENDPOINT,
            page=0,
            start_date="2024-01-15",
            end_date="2024-02-01",
            limit=20,
        )

    @pytest.mark.asyncio
    async def test_get_crypto_news_delegates_to_symbol(self, mock_client, monkeypatch):
        """Test crypto news delegates to symbol endpoint."""
        from fmp_data.intelligence import async_client as intelligence_async
        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient

        class FixedDate(dt_date):
            @classmethod
            def today(cls):  # type: ignore[override]
                return dt_date(2024, 2, 1)

        monkeypatch.setattr(intelligence_async, "date", FixedDate)

        async_client = AsyncMarketIntelligenceClient(mock_client)
        async_client.get_crypto_symbol_news = AsyncMock(return_value=["sentinel"])

        result = await async_client.get_crypto_news(
            symbol="BTCUSD", from_date=dt_date(2024, 1, 15)
        )

        assert result == ["sentinel"]
        async_client.get_crypto_symbol_news.assert_awaited_once_with(
            symbol="BTCUSD",
            page=0,
            from_date=dt_date(2024, 1, 15),
            to_date=dt_date(2024, 2, 1),
            limit=20,
        )

    @pytest.mark.asyncio
    async def test_get_ratings_snapshot_empty_list(self, mock_client):
        """Test ratings snapshot returns None on empty results."""
        from fmp_data.intelligence import endpoints as intelligence_endpoints
        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient

        mock_client.request_async.return_value = []
        async_client = AsyncMarketIntelligenceClient(mock_client)

        result = await async_client.get_ratings_snapshot("AAPL")

        assert result is None
        mock_client.request_async.assert_called_once_with(
            intelligence_endpoints.RATINGS_SNAPSHOT,
            symbol="AAPL",
        )


class TestAsyncInstitutionalClient:
    """Tests for AsyncInstitutionalClient."""

    @pytest.mark.asyncio
    async def test_get_insider_trades(self, mock_client):
        """Test async get_insider_trades method."""
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        # Use MagicMock for complex models to avoid validation issues
        mock_trade = MagicMock(spec=InsiderTrade)
        mock_trade.symbol = "AAPL"
        mock_client.request_async.return_value = [mock_trade]

        async_client = AsyncInstitutionalClient(mock_client)
        result = await async_client.get_insider_trades("AAPL")

        assert len(result) == 1
        assert result[0].symbol == "AAPL"
        mock_client.request_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_form_13f_wraps_non_list_result(self, mock_client):
        """Test get_form_13f wraps single result in a list."""
        from fmp_data.institutional import endpoints as institutional_endpoints
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mock_form = MagicMock()
        mock_client.request_async.return_value = mock_form

        async_client = AsyncInstitutionalClient(mock_client)
        report_date = dt_date(2024, 6, 30)
        result = await async_client.get_form_13f("0000320193", report_date)

        assert result == [mock_form]
        mock_client.request_async.assert_called_once_with(
            institutional_endpoints.FORM_13F,
            cik="0000320193",
            year=2024,
            quarter=2,
        )

    @pytest.mark.asyncio
    async def test_get_form_13f_handles_exception(self, mock_client):
        """Test get_form_13f returns empty list on errors."""
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mock_client.logger = MagicMock()
        from fmp_data.exceptions import FMPError

        mock_client.request_async.side_effect = FMPError("boom")

        async_client = AsyncInstitutionalClient(mock_client)
        report_date = dt_date(2024, 6, 30)
        result = await async_client.get_form_13f("0000320193", report_date)

        assert result == []
        mock_client.logger.warning.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_form_13f_dates_wraps_non_list_result(self, mock_client):
        """Test get_form_13f_dates wraps single result in a list."""
        from fmp_data.institutional import endpoints as institutional_endpoints
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mock_date = MagicMock()
        mock_client.request_async.return_value = mock_date

        async_client = AsyncInstitutionalClient(mock_client)
        result = await async_client.get_form_13f_dates("0000320193")

        assert result == [mock_date]
        mock_client.request_async.assert_called_once_with(
            institutional_endpoints.FORM_13F_DATES, cik="0000320193"
        )

    @pytest.mark.asyncio
    async def test_get_institutional_holdings_uses_report_date(self, mock_client):
        """Test get_institutional_holdings derives year/quarter from date."""
        from fmp_data.institutional import endpoints as institutional_endpoints
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mock_client.request_async.return_value = []
        async_client = AsyncInstitutionalClient(mock_client)

        report_date = dt_date(2024, 5, 15)
        result = await async_client.get_institutional_holdings("AAPL", report_date)

        assert result == []
        mock_client.request_async.assert_called_once_with(
            institutional_endpoints.INSTITUTIONAL_HOLDINGS,
            symbol="AAPL",
            year=2024,
            quarter=2,
        )

    @pytest.mark.asyncio
    async def test_search_cik_by_name_filters_results(self, mock_client):
        """Test search_cik_by_name filters by uppercased name."""
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mapping_match = CIKMapping(
            reporting_cik="0000000001", reporting_name="Acme Corp"
        )
        mapping_other = CIKMapping(
            reporting_cik="0000000002", reporting_name="Other Corp"
        )
        mock_client.request_async.return_value = [mapping_match, mapping_other]

        async_client = AsyncInstitutionalClient(mock_client)
        result = await async_client.search_cik_by_name("acme")

        assert result == [mapping_match]

    @pytest.mark.asyncio
    async def test_search_cik_by_name_wraps_non_list(self, mock_client):
        """Test search_cik_by_name wraps non-list results."""
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mapping = CIKMapping(reporting_cik="0000000001", reporting_name="Acme Corp")
        mock_client.request_async.return_value = mapping

        async_client = AsyncInstitutionalClient(mock_client)
        result = await async_client.search_cik_by_name("acme")

        assert result == [mapping]

    @pytest.mark.asyncio
    async def test_get_insider_trading_latest_includes_date(self, mock_client):
        """Test get_insider_trading_latest includes trade_date."""
        from fmp_data.institutional import endpoints as institutional_endpoints
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mock_client.request_async.return_value = []
        async_client = AsyncInstitutionalClient(mock_client)

        trade_date = dt_date(2024, 1, 15)
        result = await async_client.get_insider_trading_latest(
            page=1, limit=10, trade_date=trade_date
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            institutional_endpoints.INSIDER_TRADING_LATEST,
            page=1,
            limit=10,
            date=trade_date,
        )

    @pytest.mark.asyncio
    async def test_search_insider_trading_builds_params(self, mock_client):
        """Test search_insider_trading forwards optional filters."""
        from fmp_data.institutional import endpoints as institutional_endpoints
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mock_client.request_async.return_value = []
        async_client = AsyncInstitutionalClient(mock_client)

        result = await async_client.search_insider_trading(
            symbol="AAPL",
            page=2,
            limit=25,
            reporting_cik="0000000001",
            company_cik="0000000002",
            transaction_type="P",
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            institutional_endpoints.INSIDER_TRADING_SEARCH,
            page=2,
            limit=25,
            symbol="AAPL",
            reportingCik="0000000001",
            companyCik="0000000002",
            transactionType="P",
        )

    @pytest.mark.asyncio
    async def test_get_insider_statistics_returns_first(self, mock_client):
        """Test get_insider_statistics returns first element."""
        from fmp_data.institutional import endpoints as institutional_endpoints
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mock_stat = MagicMock()
        mock_client.request_async.return_value = [mock_stat]

        async_client = AsyncInstitutionalClient(mock_client)
        result = await async_client.get_insider_statistics("AAPL")

        assert result is mock_stat
        mock_client.request_async.assert_called_once_with(
            institutional_endpoints.INSIDER_STATISTICS,
            symbol="AAPL",
        )

    @pytest.mark.asyncio
    async def test_get_insider_trading_statistics_enhanced_list(self, mock_client):
        """Test get_insider_trading_statistics_enhanced returns first element."""
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mock_stat = MagicMock()
        mock_client.request_async.return_value = [mock_stat]

        async_client = AsyncInstitutionalClient(mock_client)
        result = await async_client.get_insider_trading_statistics_enhanced("AAPL")

        assert result is mock_stat

    @pytest.mark.asyncio
    async def test_get_institutional_ownership_latest_with_cik(self, mock_client):
        """Test get_institutional_ownership_latest includes cik param."""
        from fmp_data.institutional import endpoints as institutional_endpoints
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mock_client.request_async.return_value = []
        async_client = AsyncInstitutionalClient(mock_client)

        result = await async_client.get_institutional_ownership_latest(
            cik="0000320193", page=1, limit=5
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            institutional_endpoints.INSTITUTIONAL_OWNERSHIP_LATEST,
            cik="0000320193",
            page=1,
            limit=5,
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method_name,kwargs,endpoint_name,expected_kwargs",
        [
            (
                "get_asset_allocation",
                {"report_date": dt_date(2024, 6, 30)},
                "ASSET_ALLOCATION",
                {"date": "2024-06-30"},
            ),
            (
                "get_institutional_holders",
                {"page": 1, "limit": 10},
                "INSTITUTIONAL_HOLDERS",
                {"page": 1, "limit": 10},
            ),
            ("get_transaction_types", {}, "TRANSACTION_TYPES", {}),
            (
                "get_insider_roster",
                {"symbol": "AAPL"},
                "INSIDER_ROSTER",
                {"symbol": "AAPL"},
            ),
            (
                "get_cik_mappings",
                {"page": 2, "limit": 500},
                "CIK_MAPPER",
                {"page": 2, "limit": 500},
            ),
            (
                "get_beneficial_ownership",
                {"symbol": "AAPL"},
                "BENEFICIAL_OWNERSHIP",
                {"symbol": "AAPL"},
            ),
            (
                "get_fail_to_deliver",
                {"symbol": "AAPL", "page": 3},
                "FAIL_TO_DELIVER",
                {"symbol": "AAPL", "page": 3},
            ),
        ],
    )
    async def test_institutional_simple_endpoints(
        self, mock_client, method_name, kwargs, endpoint_name, expected_kwargs
    ):
        """Test institutional endpoints that forward params."""
        from fmp_data.institutional import endpoints as institutional_endpoints
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mock_client.request_async.return_value = []
        async_client = AsyncInstitutionalClient(mock_client)

        method = getattr(async_client, method_name)
        result = await method(**kwargs)

        assert result == []
        endpoint = getattr(institutional_endpoints, endpoint_name)
        if expected_kwargs:
            mock_client.request_async.assert_called_once_with(
                endpoint, **expected_kwargs
            )
        else:
            mock_client.request_async.assert_called_once_with(endpoint)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method_name,kwargs,endpoint_name,expected_kwargs",
        [
            (
                "get_institutional_ownership_extract",
                {"cik": "0000320193", "report_date": dt_date(2024, 3, 31)},
                "INSTITUTIONAL_OWNERSHIP_EXTRACT",
                {"cik": "0000320193", "year": 2024, "quarter": 1},
            ),
            (
                "get_institutional_ownership_analytics",
                {
                    "symbol": "AAPL",
                    "report_date": dt_date(2024, 3, 31),
                    "page": 2,
                    "limit": 50,
                },
                "INSTITUTIONAL_OWNERSHIP_ANALYTICS",
                {
                    "symbol": "AAPL",
                    "year": 2024,
                    "quarter": 1,
                    "page": 2,
                    "limit": 50,
                },
            ),
        ],
    )
    async def test_institutional_year_quarter_params(
        self, mock_client, method_name, kwargs, endpoint_name, expected_kwargs
    ):
        """Test institutional endpoints using year/quarter integers."""
        from fmp_data.institutional import endpoints as institutional_endpoints
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mock_client.request_async.return_value = []
        async_client = AsyncInstitutionalClient(mock_client)

        method = getattr(async_client, method_name)
        result = await method(**kwargs)

        assert result == []
        endpoint = getattr(institutional_endpoints, endpoint_name)
        mock_client.request_async.assert_called_once_with(endpoint, **expected_kwargs)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method_name,kwargs,endpoint_name,expected_kwargs",
        [
            (
                "get_holder_performance_summary",
                {
                    "cik": "0000320193",
                    "report_date": dt_date(2024, 3, 31),
                    "page": 1,
                },
                "HOLDER_PERFORMANCE_SUMMARY",
                {
                    "cik": "0000320193",
                    "page": 1,
                    "year": 2024,
                    "quarter": 1,
                },
            ),
            (
                "get_holder_industry_breakdown",
                {"cik": "0000320193", "report_date": dt_date(2024, 3, 31)},
                "HOLDER_INDUSTRY_BREAKDOWN",
                {
                    "cik": "0000320193",
                    "year": 2024,
                    "quarter": 1,
                },
            ),
            (
                "get_symbol_positions_summary",
                {"symbol": "AAPL", "report_date": dt_date(2024, 3, 31)},
                "SYMBOL_POSITIONS_SUMMARY",
                {"symbol": "AAPL", "year": 2024, "quarter": 1},
            ),
            (
                "get_industry_performance_summary",
                {"report_date": dt_date(2024, 3, 31)},
                "INDUSTRY_PERFORMANCE_SUMMARY",
                {"year": 2024, "quarter": 1},
            ),
        ],
    )
    async def test_institutional_integer_year_quarter_params(
        self, mock_client, method_name, kwargs, endpoint_name, expected_kwargs
    ):
        """Test institutional endpoints using year/quarter integers."""
        from fmp_data.institutional import endpoints as institutional_endpoints
        from fmp_data.institutional.async_client import AsyncInstitutionalClient

        mock_client.request_async.return_value = []
        async_client = AsyncInstitutionalClient(mock_client)

        method = getattr(async_client, method_name)
        result = await method(**kwargs)

        assert result == []
        endpoint = getattr(institutional_endpoints, endpoint_name)
        mock_client.request_async.assert_called_once_with(endpoint, **expected_kwargs)


class TestAsyncInvestmentClient:
    """Tests for AsyncInvestmentClient."""

    @pytest.mark.asyncio
    async def test_get_etf_info(self, mock_client):
        """Test async get_etf_info method."""
        from fmp_data.investment.async_client import AsyncInvestmentClient

        mock_client.request_async.return_value = [
            ETFInfo(
                symbol="SPY",
                name="SPDR S&P 500 ETF Trust",
                assetClass="Equity",
                expenseRatio=0.0945,
            )
        ]

        async_client = AsyncInvestmentClient(mock_client)
        result = await async_client.get_etf_info("SPY")

        assert isinstance(result, ETFInfo)
        assert result.symbol == "SPY"

    @pytest.mark.asyncio
    async def test_get_etf_info_warns_on_unexpected_type(self, mock_client):
        """Test get_etf_info warns on unexpected responses."""
        from fmp_data.investment.async_client import AsyncInvestmentClient

        mock_client.request_async.return_value = {"unexpected": "data"}

        async_client = AsyncInvestmentClient(mock_client)
        with pytest.warns(UserWarning, match="Unexpected result type"):
            result = await async_client.get_etf_info("SPY")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_etf_info_warns_on_exception(self, mock_client):
        """Test get_etf_info re-raises unexpected exceptions."""
        from fmp_data.investment.async_client import AsyncInvestmentClient

        mock_client.request_async.side_effect = RuntimeError("boom")

        async_client = AsyncInvestmentClient(mock_client)
        with pytest.raises(RuntimeError, match="boom"):
            await async_client.get_etf_info("SPY")

    @pytest.mark.asyncio
    async def test_get_etf_info_warns_on_fmp_error(self, mock_client):
        """Test get_etf_info warns and returns None for FMPError/ValidationError."""
        from fmp_data.exceptions import FMPError
        from fmp_data.investment.async_client import AsyncInvestmentClient

        mock_client.request_async.side_effect = FMPError("API error")

        async_client = AsyncInvestmentClient(mock_client)
        with pytest.warns(UserWarning, match="Error in get_etf_info"):
            result = await async_client.get_etf_info("SPY")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_etf_info_empty_list_returns_none(self, mock_client):
        """Test get_etf_info handles empty list responses."""
        from fmp_data.investment.async_client import AsyncInvestmentClient

        mock_client.request_async.return_value = []

        async_client = AsyncInvestmentClient(mock_client)
        result = await async_client.get_etf_info("SPY")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_etf_info_returns_instance(self, mock_client):
        """Test get_etf_info returns ETFInfo instances."""
        from fmp_data.investment.async_client import AsyncInvestmentClient

        mock_client.request_async.return_value = ETFInfo(
            symbol="SPY",
            name="SPDR S&P 500 ETF Trust",
            expenseRatio=0.0945,
        )

        async_client = AsyncInvestmentClient(mock_client)
        result = await async_client.get_etf_info("SPY")

        assert isinstance(result, ETFInfo)
        assert result.symbol == "SPY"

    @pytest.mark.asyncio
    async def test_get_mutual_fund_dates_with_cik(self, mock_client):
        """Test mutual fund dates include CIK when provided."""
        from fmp_data.investment import endpoints as investment_endpoints
        from fmp_data.investment.async_client import AsyncInvestmentClient

        mock_client.request_async.return_value = []
        async_client = AsyncInvestmentClient(mock_client)

        result = await async_client.get_mutual_fund_dates("VFIAX", cik="0000320193")

        assert result == []
        mock_client.request_async.assert_called_once_with(
            investment_endpoints.MUTUAL_FUND_DATES,
            symbol="VFIAX",
            cik="0000320193",
        )

    @pytest.mark.asyncio
    async def test_get_mutual_fund_holdings_formats_date(self, mock_client):
        """Test mutual fund holdings formats date parameter."""
        from fmp_data.investment import endpoints as investment_endpoints
        from fmp_data.investment.async_client import AsyncInvestmentClient

        mock_client.request_async.return_value = []
        async_client = AsyncInvestmentClient(mock_client)

        result = await async_client.get_mutual_fund_holdings(
            "VFIAX", dt_date(2024, 1, 15)
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            investment_endpoints.MUTUAL_FUND_HOLDINGS,
            symbol="VFIAX",
            date="2024-01-15",
        )

    @pytest.mark.asyncio
    async def test_get_fund_disclosure_with_cik(self, mock_client):
        """Test fund disclosure forwards optional CIK."""
        from fmp_data.investment import endpoints as investment_endpoints
        from fmp_data.investment.async_client import AsyncInvestmentClient

        mock_client.request_async.return_value = []
        async_client = AsyncInvestmentClient(mock_client)

        result = await async_client.get_fund_disclosure(
            "VFIAX", year=2024, quarter=1, cik="0000320193"
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            investment_endpoints.FUNDS_DISCLOSURE,
            symbol="VFIAX",
            year=2024,
            quarter=1,
            cik="0000320193",
        )


class TestAsyncAlternativeMarketsClient:
    """Tests for AsyncAlternativeMarketsClient."""

    @pytest.mark.asyncio
    async def test_get_crypto_quote(self, mock_client):
        """Test async get_crypto_quote method."""
        from fmp_data.alternative.async_client import AsyncAlternativeMarketsClient

        mock_client.request_async.return_value = [
            CryptoQuote(
                symbol="BTCUSD",
                name="Bitcoin",
                price=50000.0,
                changesPercentage=2.5,
                change=1250.0,
                dayLow=48000.0,
                dayHigh=51000.0,
                yearHigh=69000.0,
                yearLow=30000.0,
                volume=1000000000,
                open=49000.0,
                previousClose=48750.0,
                timestamp=1704067200,
            )
        ]

        async_client = AsyncAlternativeMarketsClient(mock_client)
        result = await async_client.get_crypto_quote("BTCUSD")

        assert isinstance(result, CryptoQuote)
        assert result.symbol == "BTCUSD"

    @pytest.mark.asyncio
    async def test_get_forex_quote(self, mock_client):
        """Test async get_forex_quote method."""
        from fmp_data.alternative.async_client import AsyncAlternativeMarketsClient

        mock_client.request_async.return_value = [
            ForexQuote(
                symbol="EURUSD",
                name="EUR/USD",
                price=1.10,
                changesPercentage=0.5,
                change=0.005,
                dayLow=1.09,
                dayHigh=1.11,
                yearHigh=1.15,
                yearLow=1.05,
                open=1.095,
                previousClose=1.095,
                timestamp=1704067200,
            )
        ]

        async_client = AsyncAlternativeMarketsClient(mock_client)
        result = await async_client.get_forex_quote("EURUSD")

        assert isinstance(result, ForexQuote)
        assert result.symbol == "EURUSD"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method_name,endpoint_name",
        [
            ("get_crypto_list", "CRYPTO_LIST"),
            ("get_crypto_quotes", "CRYPTO_QUOTES"),
            ("get_forex_list", "FOREX_LIST"),
            ("get_forex_quotes", "FOREX_QUOTES"),
            ("get_commodities_list", "COMMODITIES_LIST"),
            ("get_commodities_quotes", "COMMODITIES_QUOTES"),
        ],
    )
    async def test_alternative_list_endpoints(
        self, mock_client, method_name, endpoint_name
    ):
        """Test alternative list endpoints forward no params."""
        from fmp_data.alternative import endpoints as alternative_endpoints
        from fmp_data.alternative.async_client import AsyncAlternativeMarketsClient

        mock_client.request_async.return_value = []
        async_client = AsyncAlternativeMarketsClient(mock_client)

        method = getattr(async_client, method_name)
        result = await method()

        assert result == []
        endpoint = getattr(alternative_endpoints, endpoint_name)
        mock_client.request_async.assert_called_once_with(endpoint)

    @pytest.mark.asyncio
    async def test_get_crypto_historical_wraps_list_response(
        self, mock_client, monkeypatch
    ):
        """Test crypto historical list responses are wrapped."""
        from fmp_data.alternative.async_client import AsyncAlternativeMarketsClient
        from fmp_data.alternative.models import CryptoHistoricalData

        sentinel = MagicMock()
        mock_validate = MagicMock(return_value=sentinel)
        monkeypatch.setattr(CryptoHistoricalData, "model_validate", mock_validate)

        mock_client.request_async.return_value = [{"date": "2024-01-01"}]

        async_client = AsyncAlternativeMarketsClient(mock_client)
        result = await async_client.get_crypto_historical("BTCUSD")

        assert result is sentinel
        mock_validate.assert_called_once_with(
            {"symbol": "BTCUSD", "historical": [{"date": "2024-01-01"}]}
        )

    @pytest.mark.asyncio
    async def test_get_crypto_historical_passes_dict_response(
        self, mock_client, monkeypatch
    ):
        """Test crypto historical dict responses pass through."""
        from fmp_data.alternative.async_client import AsyncAlternativeMarketsClient
        from fmp_data.alternative.models import CryptoHistoricalData

        sentinel = MagicMock()
        mock_validate = MagicMock(return_value=sentinel)
        monkeypatch.setattr(CryptoHistoricalData, "model_validate", mock_validate)

        response = {"symbol": "BTCUSD", "historical": [{"date": "2024-01-01"}]}
        mock_client.request_async.return_value = response

        async_client = AsyncAlternativeMarketsClient(mock_client)
        result = await async_client.get_crypto_historical("BTCUSD")

        assert result is sentinel
        mock_validate.assert_called_once_with(response)

    @pytest.mark.asyncio
    async def test_get_forex_historical_formats_dates(self, mock_client):
        """Test forex historical formats date parameters."""
        from fmp_data.alternative import endpoints as alternative_endpoints
        from fmp_data.alternative.async_client import AsyncAlternativeMarketsClient

        mock_client.request_async.return_value = {"symbol": "EURUSD", "historical": []}

        async_client = AsyncAlternativeMarketsClient(mock_client)
        result = await async_client.get_forex_historical(
            "EURUSD", start_date=dt_date(2024, 1, 1), end_date=dt_date(2024, 1, 31)
        )

        assert result.symbol == "EURUSD"
        mock_client.request_async.assert_called_once_with(
            alternative_endpoints.FOREX_HISTORICAL,
            symbol="EURUSD",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

    @pytest.mark.asyncio
    async def test_get_commodity_historical_formats_dates(self, mock_client):
        """Test commodity historical formats date parameters."""
        from fmp_data.alternative import endpoints as alternative_endpoints
        from fmp_data.alternative.async_client import AsyncAlternativeMarketsClient

        mock_client.request_async.return_value = {"symbol": "CL", "historical": []}

        async_client = AsyncAlternativeMarketsClient(mock_client)
        result = await async_client.get_commodity_historical(
            "CL", start_date=dt_date(2024, 2, 1), end_date=dt_date(2024, 2, 15)
        )

        assert result.symbol == "CL"
        mock_client.request_async.assert_called_once_with(
            alternative_endpoints.COMMODITY_HISTORICAL,
            symbol="CL",
            start_date="2024-02-01",
            end_date="2024-02-15",
        )


class TestAsyncEconomicsClient:
    """Tests for AsyncEconomicsClient."""

    @pytest.mark.asyncio
    async def test_get_treasury_rates(self, mock_client):
        """Test async get_treasury_rates method."""
        from fmp_data.economics.async_client import AsyncEconomicsClient

        mock_client.request_async.return_value = [
            TreasuryRate(
                date="2024-01-01",
                month1=5.0,
                month2=5.1,
                month3=5.2,
                month6=5.3,
                year1=5.0,
                year2=4.8,
                year3=4.6,
                year5=4.5,
                year7=4.4,
                year10=4.3,
                year20=4.5,
                year30=4.6,
            )
        ]

        async_client = AsyncEconomicsClient(mock_client)
        result = await async_client.get_treasury_rates()

        assert len(result) == 1
        assert isinstance(result[0], TreasuryRate)

    @pytest.mark.asyncio
    async def test_get_economic_calendar_formats_dates(self, mock_client):
        """Test economic calendar date formatting."""
        from fmp_data.economics import endpoints as economics_endpoints
        from fmp_data.economics.async_client import AsyncEconomicsClient

        mock_client.request_async.return_value = []
        async_client = AsyncEconomicsClient(mock_client)

        result = await async_client.get_economic_calendar(
            start_date=dt_date(2024, 1, 1),
            end_date=dt_date(2024, 1, 31),
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            economics_endpoints.ECONOMIC_CALENDAR,
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

    @pytest.mark.asyncio
    async def test_get_commitment_of_traders_report_formats_dates(self, mock_client):
        """Test COT report date formatting."""
        from fmp_data.economics import endpoints as economics_endpoints
        from fmp_data.economics.async_client import AsyncEconomicsClient

        mock_client.request_async.return_value = []
        async_client = AsyncEconomicsClient(mock_client)

        result = await async_client.get_commitment_of_traders_report(
            "CL", start_date=dt_date(2024, 1, 1), end_date=dt_date(2024, 1, 31)
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            economics_endpoints.COMMITMENT_OF_TRADERS_REPORT,
            symbol="CL",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )


class TestAsyncBatchClient:
    """Tests for AsyncBatchClient."""

    @pytest.mark.asyncio
    async def test_get_quotes(self, mock_client):
        """Test async get_quotes method."""
        from fmp_data.batch.async_client import AsyncBatchClient

        mock_client.request_async.return_value = [
            BatchQuote(
                symbol="AAPL",
                name="Apple Inc.",
                price=150.0,
                changesPercentage=1.5,
                change=2.25,
                dayLow=148.0,
                dayHigh=152.0,
                yearHigh=180.0,
                yearLow=120.0,
                priceAvg50=155.0,
                priceAvg200=160.0,
                volume=50000000,
                avgVolume=45000000,
                exchange="NASDAQ",
                open=149.0,
                previousClose=147.75,
            ),
            BatchQuote(
                symbol="MSFT",
                name="Microsoft Corporation",
                price=380.0,
                changesPercentage=0.8,
                change=3.0,
                dayLow=375.0,
                dayHigh=385.0,
                yearHigh=400.0,
                yearLow=300.0,
                priceAvg50=370.0,
                priceAvg200=350.0,
                volume=30000000,
                avgVolume=25000000,
                exchange="NASDAQ",
                open=378.0,
                previousClose=377.0,
            ),
        ]

        async_client = AsyncBatchClient(mock_client)
        result = await async_client.get_quotes(["AAPL", "MSFT"])

        assert len(result) == 2
        assert isinstance(result[0], BatchQuote)
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "MSFT"

    @pytest.mark.asyncio
    async def test_get_quotes_short(self, mock_client):
        """Test async get_quotes_short method."""
        from fmp_data.batch.async_client import AsyncBatchClient

        mock_client.request_async.return_value = [
            BatchQuoteShort(symbol="AAPL", price=150.0, volume=50000000),
            BatchQuoteShort(symbol="MSFT", price=380.0, volume=30000000),
        ]

        async_client = AsyncBatchClient(mock_client)
        result = await async_client.get_quotes_short(["AAPL", "MSFT"])

        assert len(result) == 2
        assert isinstance(result[0], BatchQuoteShort)

    def test_parse_csv_rows_empty(self):
        """Test parsing empty CSV data returns no rows."""

        assert parse_csv_rows(b"") == []

    def test_parse_csv_rows_skips_blank_rows(self):
        """Test CSV parsing skips blank rows and strips whitespace."""

        raw = b"symbol,name\nAAPL, Apple Inc. \n, \n"
        rows = parse_csv_rows(raw)

        assert rows == [{"symbol": "AAPL", "name": "Apple Inc."}]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method_name,kwargs,endpoint",
        [
            (
                "get_exchange_quotes",
                {"exchange": "NASDAQ", "short": True},
                "BATCH_EXCHANGE_QUOTE",
            ),
            ("get_mutualfund_quotes", {"short": True}, "BATCH_MUTUALFUND_QUOTES"),
            ("get_etf_quotes", {"short": True}, "BATCH_ETF_QUOTES"),
            ("get_commodity_quotes", {"short": True}, "BATCH_COMMODITY_QUOTES"),
            ("get_crypto_quotes", {"short": True}, "BATCH_CRYPTO_QUOTES"),
            ("get_forex_quotes", {"short": True}, "BATCH_FOREX_QUOTES"),
            ("get_index_quotes", {"short": True}, "BATCH_INDEX_QUOTES"),
        ],
    )
    async def test_batch_short_param(self, mock_client, method_name, kwargs, endpoint):
        """Test short param forwarding for async batch endpoints."""
        from fmp_data.batch import endpoints as batch_endpoints
        from fmp_data.batch.async_client import AsyncBatchClient

        mock_client.request_async.return_value = []
        async_client = AsyncBatchClient(mock_client)

        method = getattr(async_client, method_name)
        await method(**kwargs)

        expected_endpoint = getattr(batch_endpoints, endpoint)
        mock_client.request_async.assert_called_once_with(expected_endpoint, **kwargs)

    @pytest.mark.asyncio
    async def test_get_exchange_quotes_without_short(self, mock_client):
        """Test exchange quotes omit short param when None."""
        from fmp_data.batch import endpoints as batch_endpoints
        from fmp_data.batch.async_client import AsyncBatchClient

        mock_client.request_async.return_value = []
        async_client = AsyncBatchClient(mock_client)

        result = await async_client.get_exchange_quotes("NASDAQ")

        assert result == []
        mock_client.request_async.assert_called_once_with(
            batch_endpoints.BATCH_EXCHANGE_QUOTE, exchange="NASDAQ"
        )

    @pytest.mark.asyncio
    async def test_get_eod_bulk(self, mock_client):
        """Test async get_eod_bulk method."""
        from fmp_data.batch.async_client import AsyncBatchClient
        from fmp_data.batch.endpoints import EOD_BULK

        mock_client.request_async.return_value = (
            b"symbol,date,open,low,high,close,adjClose,volume\n"
            b"EGS745W1C011.CA,2024-10-22,2.67,2.7,2.9,2.93,2.93,920904\n"
        )

        async_client = AsyncBatchClient(mock_client)
        result = await async_client.get_eod_bulk(dt_date(2024, 10, 22))

        assert result[0].symbol == "EGS745W1C011.CA"
        assert result[0].adj_close == 2.93
        mock_client.request_async.assert_called_once_with(EOD_BULK, date="2024-10-22")


class TestAsyncTranscriptsClient:
    """Tests for AsyncTranscriptsClient."""

    @pytest.mark.asyncio
    async def test_get_transcript(self, mock_client):
        """Test async get_transcript method."""
        from fmp_data.transcripts.async_client import AsyncTranscriptsClient

        mock_client.request_async.return_value = [
            EarningsTranscript(
                symbol="AAPL",
                quarter=1,
                year=2024,
                date="2024-01-01",
                content="This is a test transcript content.",
            )
        ]

        async_client = AsyncTranscriptsClient(mock_client)
        result = await async_client.get_transcript(
            "AAPL", year=2024, quarter=1, limit=1
        )

        assert len(result) == 1
        assert isinstance(result[0], EarningsTranscript)
        assert result[0].symbol == "AAPL"
        mock_client.request_async.assert_called_once_with(
            EARNINGS_TRANSCRIPT,
            symbol="AAPL",
            year=2024,
            quarter=1,
            limit=1,
        )


class TestAsyncSECClient:
    """Tests for AsyncSECClient."""

    @pytest.mark.asyncio
    async def test_get_latest_8k(self, mock_client):
        """Test async get_latest_8k method."""
        from fmp_data.sec.async_client import AsyncSECClient

        mock_client.request_async.return_value = [
            SECFiling8K(
                symbol="AAPL",
                cik="0000320193",
                acceptedDate="2024-01-01T12:00:00",
                formType="8-K",
                link="https://www.sec.gov/...",
                finalLink="https://www.sec.gov/...",
            )
        ]

        async_client = AsyncSECClient(mock_client)
        result = await async_client.get_latest_8k(page=0)

        assert len(result) == 1
        assert isinstance(result[0], SECFiling8K)

    @pytest.mark.asyncio
    async def test_get_latest_8k_with_dates(self, mock_client):
        """Test get_latest_8k formats date filters."""
        from fmp_data.sec import endpoints as sec_endpoints
        from fmp_data.sec.async_client import AsyncSECClient

        mock_client.request_async.return_value = []
        async_client = AsyncSECClient(mock_client)

        result = await async_client.get_latest_8k(
            page=1,
            limit=50,
            from_date=dt_date(2024, 1, 1),
            to_date=dt_date(2024, 1, 31),
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            sec_endpoints.SEC_FILINGS_8K,
            page=1,
            limit=50,
            **{"from": "2024-01-01", "to": "2024-01-31"},
        )

    @pytest.mark.asyncio
    async def test_get_profile_handles_validation_errors(self, mock_client):
        """Test get_profile returns None on validation errors."""
        from pydantic import ValidationError

        from fmp_data.sec.async_client import AsyncSECClient

        mock_client.logger = MagicMock()
        error = ValidationError.from_exception_data(
            "SECProfile",
            [
                {
                    "type": "missing",
                    "loc": ("symbol",),
                    "msg": "Field required",
                    "input": None,
                }
            ],
        )
        mock_client.request_async.side_effect = error

        async_client = AsyncSECClient(mock_client)
        result = await async_client.get_profile("AAPL")

        assert result is None
        mock_client.logger.warning.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_profile_empty_list_returns_none(self, mock_client):
        """Test get_profile returns None for empty list."""
        from fmp_data.sec.async_client import AsyncSECClient

        mock_client.request_async.return_value = []

        async_client = AsyncSECClient(mock_client)
        result = await async_client.get_profile("AAPL")

        assert result is None

    @pytest.mark.asyncio
    async def test_search_industry_classification_requires_params(self, mock_client):
        """Test search_industry_classification requires a filter."""
        from fmp_data.sec.async_client import AsyncSECClient

        async_client = AsyncSECClient(mock_client)
        with pytest.raises(ValueError, match="Provide at least one"):
            await async_client.search_industry_classification()

    @pytest.mark.asyncio
    async def test_search_industry_classification_builds_params(self, mock_client):
        """Test search_industry_classification builds optional params."""
        from fmp_data.sec import endpoints as sec_endpoints
        from fmp_data.sec.async_client import AsyncSECClient

        mock_client.request_async.return_value = []

        async_client = AsyncSECClient(mock_client)
        result = await async_client.search_industry_classification(
            symbol="AAPL",
            sic_code="3571",
        )

        assert result == []
        mock_client.request_async.assert_called_once_with(
            sec_endpoints.INDUSTRY_CLASSIFICATION_SEARCH,
            symbol="AAPL",
            sicCode="3571",
        )


class TestAsyncIndexClient:
    """Tests for AsyncIndexClient."""

    @pytest.mark.asyncio
    async def test_get_sp500_constituents(self, mock_client):
        """Test async get_sp500_constituents method."""
        from fmp_data.index.async_client import AsyncIndexClient

        mock_client.request_async.return_value = [
            IndexConstituent(
                symbol="AAPL",
                name="Apple Inc.",
                sector="Technology",
                subSector="Consumer Electronics",
                headQuarter="Cupertino, CA",
            )
        ]

        async_client = AsyncIndexClient(mock_client)
        result = await async_client.get_sp500_constituents()

        assert len(result) == 1
        assert isinstance(result[0], IndexConstituent)
        assert result[0].symbol == "AAPL"


class TestAsyncFMPDataClient:
    """Tests for AsyncFMPDataClient main class."""

    def test_async_fmp_data_client_requires_api_key(self):
        """Test async client requires an API key."""
        from fmp_data import AsyncFMPDataClient
        from fmp_data.exceptions import ConfigError

        with pytest.raises(ConfigError, match="API key is required"):
            AsyncFMPDataClient(api_key=None)

    @pytest.mark.asyncio
    async def test_async_fmp_data_client_initialization(self):
        """Test AsyncFMPDataClient can be initialized."""
        from fmp_data import AsyncFMPDataClient

        client = AsyncFMPDataClient(api_key="test_key")
        assert client._initialized

        await client.aclose()

    @pytest.mark.asyncio
    async def test_async_fmp_data_client_context_manager(self):
        """Test AsyncFMPDataClient works as async context manager."""
        from fmp_data import AsyncFMPDataClient

        async with AsyncFMPDataClient(api_key="test_key") as client:
            assert client._initialized
            # Access some endpoint groups to verify lazy initialization
            _ = client.company
            _ = client.market
            _ = client.fundamental

    @pytest.mark.asyncio
    async def test_async_fmp_data_client_all_properties(self):
        """Test all endpoint group properties are accessible."""
        from fmp_data import AsyncFMPDataClient
        from fmp_data.alternative.async_client import AsyncAlternativeMarketsClient
        from fmp_data.batch.async_client import AsyncBatchClient
        from fmp_data.company.async_client import AsyncCompanyClient
        from fmp_data.economics.async_client import AsyncEconomicsClient
        from fmp_data.fundamental.async_client import AsyncFundamentalClient
        from fmp_data.index.async_client import AsyncIndexClient
        from fmp_data.institutional.async_client import AsyncInstitutionalClient
        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient
        from fmp_data.investment.async_client import AsyncInvestmentClient
        from fmp_data.market.async_client import AsyncMarketClient
        from fmp_data.sec.async_client import AsyncSECClient
        from fmp_data.technical.async_client import AsyncTechnicalClient
        from fmp_data.transcripts.async_client import AsyncTranscriptsClient

        async with AsyncFMPDataClient(api_key="test_key") as client:
            assert isinstance(client.company, AsyncCompanyClient)
            assert isinstance(client.market, AsyncMarketClient)
            assert isinstance(client.fundamental, AsyncFundamentalClient)
            assert isinstance(client.technical, AsyncTechnicalClient)
            assert isinstance(client.intelligence, AsyncMarketIntelligenceClient)
            assert isinstance(client.institutional, AsyncInstitutionalClient)
            assert isinstance(client.investment, AsyncInvestmentClient)
            assert isinstance(client.alternative, AsyncAlternativeMarketsClient)
            assert isinstance(client.economics, AsyncEconomicsClient)
            assert isinstance(client.batch, AsyncBatchClient)
            assert isinstance(client.transcripts, AsyncTranscriptsClient)
            assert isinstance(client.sec, AsyncSECClient)
            assert isinstance(client.index, AsyncIndexClient)

    @pytest.mark.asyncio
    async def test_async_fmp_data_client_from_env(self, monkeypatch):
        """Test AsyncFMPDataClient.from_env method."""
        from fmp_data import AsyncFMPDataClient

        monkeypatch.setenv("FMP_API_KEY", "test_env_key")

        client = AsyncFMPDataClient.from_env()
        assert client._initialized

        await client.aclose()

    @pytest.mark.asyncio
    async def test_async_fmp_data_client_aenter_requires_initialized(self):
        """Test async context manager rejects uninitialized client."""
        from fmp_data import AsyncFMPDataClient

        client = AsyncFMPDataClient(api_key="test_key")
        client._initialized = False

        with pytest.raises(RuntimeError, match="Client not properly initialized"):
            await client.__aenter__()

        client._initialized = True
        await client.aclose()

    @pytest.mark.asyncio
    async def test_async_fmp_data_client_aexit_logs_error(self):
        """Test async context manager logs errors on exit."""
        from fmp_data import AsyncFMPDataClient

        client = AsyncFMPDataClient(api_key="test_key")
        client.client = MagicMock()
        client._logger = MagicMock()
        client.aclose = AsyncMock()

        await client.__aexit__(ValueError, ValueError("boom"), None)

        client._logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_fmp_data_client_aclose_closes_clients(self):
        """Test aclose closes async and sync clients."""
        from fmp_data import AsyncFMPDataClient

        client = AsyncFMPDataClient(api_key="test_key")
        async_client = AsyncMock()
        async_client.is_closed = False
        client._async_client = async_client
        client.client = MagicMock()
        client._logger = MagicMock()

        await client.aclose()

        async_client.aclose.assert_awaited_once()
        client.client.close.assert_called_once()
        client._logger.info.assert_called_once_with("Async FMP Data client closed")


class TestAsyncMarketIntelligenceClient:
    """Tests for AsyncMarketIntelligenceClient."""

    @pytest.mark.asyncio
    async def test_get_stock_news_sentiments_deprecation_warning(self, mock_client):
        """Test that get_stock_news_sentiments emits deprecation warning."""
        import warnings

        from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient

        async_client = AsyncMarketIntelligenceClient(mock_client)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = await async_client.get_stock_news_sentiments(page=0)

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "no longer supports this endpoint" in str(w[0].message)

        # Verify no API call was made
        mock_client.request_async.assert_not_called()

        # Verify empty result
        assert result == []
        assert isinstance(result, list)
