# tests/unit/test_async_clients.py
"""Tests for async endpoint group clients."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from fmp_data.alternative.models import CryptoQuote, ForexQuote
from fmp_data.batch.models import BatchQuote, BatchQuoteShort
from fmp_data.company.models import (
    AftermarketQuote,
    AftermarketTrade,
    CompanyProfile,
    IntradayPrice,
    Quote,
    StockPriceChange,
)
from fmp_data.economics.models import TreasuryRate
from fmp_data.fundamental.models import BalanceSheet, IncomeStatement, OwnerEarnings
from fmp_data.index.models import IndexConstituent
from fmp_data.institutional.models import InsiderTrade
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
            from_date="2025-02-01",
            to_date="2025-02-04",
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
