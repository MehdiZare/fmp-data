# tests/unit/test_batch.py
"""Tests for the batch module endpoints"""

from datetime import date
from unittest.mock import AsyncMock, Mock, patch

import pytest

from fmp_data.batch._csv_utils import get_url_fields, parse_csv_models, parse_csv_rows
from fmp_data.batch.models import (
    AftermarketQuote,
    AftermarketTrade,
    BatchMarketCap,
    BatchQuote,
    BatchQuoteShort,
    EarningsSurpriseBulk,
    EODBulk,
    PeersBulk,
)
from fmp_data.company.models import CompanyProfile


class TestBatchModels:
    """Tests for batch model validation"""

    @pytest.fixture
    def batch_quote_data(self):
        """Mock batch quote data"""
        return {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 150.25,
            "changesPercentage": 1.5,
            "change": 2.25,
            "dayLow": 148.0,
            "dayHigh": 152.0,
            "yearHigh": 180.0,
            "yearLow": 120.0,
            "marketCap": 2500000000000,
            "priceAvg50": 155.0,
            "priceAvg200": 145.0,
            "exchange": "NASDAQ",
            "volume": 50000000,
            "avgVolume": 80000000,
            "open": 149.0,
            "previousClose": 148.0,
            "eps": 6.05,
            "pe": 24.8,
            "earningsAnnouncement": "2024-02-01T16:30:00.000+0000",
            "sharesOutstanding": 16000000000,
            "timestamp": 1704067200,
        }

    @pytest.fixture
    def batch_quote_short_data(self):
        """Mock short batch quote data"""
        return {
            "symbol": "AAPL",
            "price": 150.25,
            "change": 2.25,
            "volume": 50000000,
        }

    @pytest.fixture
    def aftermarket_trade_data(self):
        """Mock aftermarket trade data"""
        return {
            "symbol": "AAPL",
            "price": 151.00,
            "size": 100,
            "timestamp": 1704067200,
        }

    @pytest.fixture
    def aftermarket_quote_data(self):
        """Mock aftermarket quote data"""
        return {
            "symbol": "AAPL",
            "ask": 151.50,
            "bid": 151.00,
            "asize": 500,
            "bsize": 400,
            "timestamp": 1704067200,
        }

    @pytest.fixture
    def batch_market_cap_data(self):
        """Mock batch market cap data"""
        return {
            "symbol": "AAPL",
            "date": "2024-01-01",
            "marketCap": 2500000000000,
        }

    def test_batch_quote_model(self, batch_quote_data):
        """Test BatchQuote model validation"""
        quote = BatchQuote.model_validate(batch_quote_data)
        assert quote.symbol == "AAPL"
        assert quote.name == "Apple Inc."
        assert quote.price == 150.25
        assert quote.changes_percentage == 1.5
        assert quote.change == 2.25
        assert quote.day_low == 148.0
        assert quote.day_high == 152.0
        assert quote.market_cap == 2500000000000
        assert quote.exchange == "NASDAQ"
        assert quote.volume == 50000000

    def test_batch_quote_model_minimal(self):
        """Test BatchQuote with only required field"""
        quote = BatchQuote.model_validate({"symbol": "TEST"})
        assert quote.symbol == "TEST"
        assert quote.name is None
        assert quote.price is None

    def test_batch_quote_short_model(self, batch_quote_short_data):
        """Test BatchQuoteShort model validation"""
        quote = BatchQuoteShort.model_validate(batch_quote_short_data)
        assert quote.symbol == "AAPL"
        assert quote.price == 150.25
        assert quote.change == 2.25
        assert quote.volume == 50000000

    def test_aftermarket_trade_model(self, aftermarket_trade_data):
        """Test AftermarketTrade model validation"""
        trade = AftermarketTrade.model_validate(aftermarket_trade_data)
        assert trade.symbol == "AAPL"
        assert trade.price == 151.00
        assert trade.size == 100
        assert trade.timestamp == 1704067200

    def test_aftermarket_quote_model(self, aftermarket_quote_data):
        """Test AftermarketQuote model validation"""
        quote = AftermarketQuote.model_validate(aftermarket_quote_data)
        assert quote.symbol == "AAPL"
        assert quote.ask == 151.50
        assert quote.bid == 151.00
        assert quote.ask_size == 500
        assert quote.bid_size == 400

    def test_batch_market_cap_model(self, batch_market_cap_data):
        """Test BatchMarketCap model validation"""
        cap = BatchMarketCap.model_validate(batch_market_cap_data)
        assert cap.symbol == "AAPL"
        assert cap.market_cap == 2500000000000

    def test_peers_bulk_model(self):
        """Test PeersBulk model validation"""
        peers = PeersBulk.model_validate(
            {"symbol": "000001.SZ", "peers": "600036.SS,600000.SS"}
        )
        assert peers.symbol == "000001.SZ"
        assert peers.peers_list == ["600036.SS", "600000.SS"]

    def test_earnings_surprise_bulk_model(self):
        """Test EarningsSurpriseBulk model validation"""
        surprise = EarningsSurpriseBulk.model_validate(
            {
                "symbol": "AMKYF",
                "date": "2025-07-09",
                "epsActual": "0.3631",
                "epsEstimated": "0.3615",
                "lastUpdated": "2025-07-09",
            }
        )
        assert surprise.symbol == "AMKYF"
        assert surprise.eps_actual == 0.3631
        assert surprise.eps_estimated == 0.3615

    def test_eod_bulk_model(self):
        """Test EODBulk model validation"""
        eod = EODBulk.model_validate(
            {
                "symbol": "EGS745W1C011.CA",
                "date": "2024-10-22",
                "open": "2.67",
                "low": "2.7",
                "high": "2.9",
                "close": "2.93",
                "adjClose": "2.93",
                "volume": "920904",
            }
        )
        assert eod.symbol == "EGS745W1C011.CA"
        assert eod.close == 2.93


class TestBatchClient:
    """Tests for BatchClient methods"""

    @staticmethod
    def _mock_csv_response(csv_text: str) -> Mock:
        response = Mock()
        response.status_code = 200
        response.content = csv_text.encode("utf-8")
        response.raise_for_status = Mock()
        return response

    @pytest.fixture
    def batch_quote_data(self):
        """Mock batch quote data"""
        return {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 150.25,
            "changesPercentage": 1.5,
            "volume": 50000000,
        }

    def test_parse_csv_models_skips_invalid_url(self):
        """Invalid URL fields should be coerced to None."""
        csv_text = (
            '"symbol","website","image"\n'
            '"APPX","ttps://www.tradretfs.com[","https://example.com/logo.png"\n'
        )

        results = parse_csv_models(
            csv_text.encode("utf-8"),
            CompanyProfile,
        )

        assert len(results) == 1
        assert results[0].symbol == "APPX"
        assert results[0].website is None

    def test_parse_csv_rows_empty(self):
        """Empty CSV input returns no rows."""
        assert parse_csv_rows(b"") == []

    def test_parse_csv_rows_skips_blank_rows(self):
        """Blank CSV rows should be skipped."""
        csv_text = "symbol,name\nAAPL, Apple Inc. \n, \n"
        rows = parse_csv_rows(csv_text.encode("utf-8"))

        assert rows == [{"symbol": "AAPL", "name": "Apple Inc."}]

    def test_get_url_fields_detects_urls(self):
        """URL fields should be detected for URL-typed annotations."""

        from pydantic import AnyHttpUrl, BaseModel

        class URLRow(BaseModel):
            website: AnyHttpUrl | None = None
            images: list[AnyHttpUrl] | None = None
            name: str | None = None

        assert get_url_fields(URLRow) == {"website", "images"}

    def test_parse_csv_models_skips_invalid_rows_without_url_fields(self, caplog):
        """Invalid rows without URL fields should be skipped."""
        import logging

        from pydantic import BaseModel

        class SimpleRow(BaseModel):
            symbol: str
            value: int

        csv_text = "symbol,value\nAAPL,not-a-number\n"

        with caplog.at_level(logging.WARNING, logger="fmp_data.batch._csv_utils"):
            results = parse_csv_models(
                csv_text.encode("utf-8"),
                SimpleRow,
            )

        assert results == []
        assert "Skipping invalid SimpleRow row" in caplog.text

    @patch("httpx.Client.request")
    def test_get_quotes(
        self, mock_request, fmp_client, mock_response, batch_quote_data
    ):
        """Test fetching batch quotes"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[batch_quote_data]
        )
        result = fmp_client.batch.get_quotes(["AAPL"])
        assert len(result) == 1
        assert isinstance(result[0], BatchQuote)
        assert result[0].symbol == "AAPL"

    @patch("httpx.Client.request")
    def test_get_quotes_multiple_symbols(
        self, mock_request, fmp_client, mock_response, batch_quote_data
    ):
        """Test fetching batch quotes for multiple symbols"""
        msft_data = {**batch_quote_data, "symbol": "MSFT", "name": "Microsoft"}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[batch_quote_data, msft_data]
        )
        result = fmp_client.batch.get_quotes(["AAPL", "MSFT"])
        assert len(result) == 2
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "MSFT"

    @patch("httpx.Client.request")
    def test_get_quotes_short(self, mock_request, fmp_client, mock_response):
        """Test fetching short batch quotes"""
        short_data = {
            "symbol": "AAPL",
            "price": 150.25,
            "change": 2.25,
            "volume": 50000000,
        }
        mock_request.return_value = mock_response(
            status_code=200, json_data=[short_data]
        )
        result = fmp_client.batch.get_quotes_short(["AAPL"])
        assert len(result) == 1
        assert isinstance(result[0], BatchQuoteShort)
        assert result[0].price == 150.25
        assert result[0].change == 2.25

    @patch("httpx.Client.request")
    def test_get_price_target_summary_bulk(self, mock_request, fmp_client):
        """Test fetching price target summary bulk data"""
        csv_text = (
            "symbol,lastMonthCount,lastMonthAvgPriceTarget,"
            "lastQuarterCount,lastQuarterAvgPriceTarget,"
            "lastYearCount,lastYearAvgPriceTarget,"
            "allTimeCount,allTimeAvgPriceTarget,publishers\n"
            "A,0,0,1,116,6,142.17,18,146.61,"
            '"[\\"TheFly\\"]"\n'
        )
        mock_request.return_value = self._mock_csv_response(csv_text)
        results = fmp_client.batch.get_price_target_summary_bulk()
        assert results[0].symbol == "A"
        assert results[0].all_time_avg_price_target == 146.61

    @patch("httpx.Client.request")
    def test_get_etf_holder_bulk(self, mock_request, fmp_client):
        """Test fetching ETF holder bulk data"""
        csv_text = (
            "symbol,asset,name,isin,securityCusip,sharesNumber,weightPercentage,"
            "marketValue,updatedAt\n"
            "SPY,AAPL,APPLE INC,US0378331005,037833100,188106081,7.137,"
            "44744793487.47,2025-01-16 05:01:09\n"
        )
        mock_request.return_value = self._mock_csv_response(csv_text)
        results = fmp_client.batch.get_etf_holder_bulk("1")
        assert results[0].symbol == "SPY"
        assert results[0].asset == "AAPL"

    @patch("httpx.Client.request")
    def test_get_upgrades_downgrades_consensus_bulk(self, mock_request, fmp_client):
        """Test fetching upgrades/downgrades consensus bulk data"""
        csv_text = (
            "symbol,strongBuy,buy,hold,sell,strongSell,consensus\n"
            ",0,1,1,0,0,Buy\n"
            "AAPL,1,29,11,4,0,Buy\n"
        )
        mock_request.return_value = self._mock_csv_response(csv_text)
        results = fmp_client.batch.get_upgrades_downgrades_consensus_bulk()
        assert len(results) == 1
        assert results[0].symbol == "AAPL"

    @patch("httpx.Client.request")
    def test_get_key_metrics_ttm_bulk(self, mock_request, fmp_client):
        """Test fetching key metrics TTM bulk data"""
        csv_text = "date,revenuePerShare\n2025-07-09,7.38\n"
        mock_request.return_value = self._mock_csv_response(csv_text)
        results = fmp_client.batch.get_key_metrics_ttm_bulk()
        assert results[0].revenue_per_share == 7.38

    @patch("httpx.Client.request")
    def test_get_peers_bulk(self, mock_request, fmp_client):
        """Test fetching peers bulk data"""
        csv_text = 'symbol,peers\n000001.SZ,"600036.SS,600000.SS"\n'
        mock_request.return_value = self._mock_csv_response(csv_text)
        results = fmp_client.batch.get_peers_bulk()
        assert results[0].symbol == "000001.SZ"
        assert results[0].peers_list == ["600036.SS", "600000.SS"]

    @patch("httpx.Client.request")
    def test_get_earnings_surprises_bulk(self, mock_request, fmp_client):
        """Test fetching earnings surprises bulk data"""
        csv_text = (
            "symbol,date,epsActual,epsEstimated,lastUpdated\n"
            "AMKYF,2025-07-09,0.3631,0.3615,2025-07-09\n"
        )
        mock_request.return_value = self._mock_csv_response(csv_text)
        results = fmp_client.batch.get_earnings_surprises_bulk(2025)
        assert results[0].symbol == "AMKYF"
        assert results[0].eps_actual == 0.3631

    @patch("httpx.Client.request")
    def test_get_income_statement_bulk(self, mock_request, fmp_client):
        """Test fetching income statement bulk data"""
        csv_text = (
            "date,symbol,reportedCurrency,cik,filingDate,acceptedDate,fiscalYear,"
            "period,revenue\n"
            "2025-03-31,000001.SZ,CNY,0000000000,2025-03-31,"
            "2025-03-31 00:00:00,2025,Q1,33644000000\n"
        )
        mock_request.return_value = self._mock_csv_response(csv_text)
        results = fmp_client.batch.get_income_statement_bulk(2025, "Q1")
        assert results[0].symbol == "000001.SZ"
        assert results[0].revenue == 33644000000

    @patch("httpx.Client.request")
    def test_get_income_statement_growth_bulk(self, mock_request, fmp_client):
        """Test fetching income statement growth bulk data"""
        csv_text = (
            "symbol,date,fiscalYear,period,reportedCurrency,growthRevenue\n"
            "000001.SZ,2025-03-31,2025,Q1,CNY,0.04159\n"
        )
        mock_request.return_value = self._mock_csv_response(csv_text)
        results = fmp_client.batch.get_income_statement_growth_bulk(2025, "Q1")
        assert results[0].model_extra["growthRevenue"] == "0.04159"

    @patch("httpx.Client.request")
    def test_get_balance_sheet_bulk(self, mock_request, fmp_client):
        """Test fetching balance sheet bulk data"""
        csv_text = (
            "date,symbol,reportedCurrency,cik,filingDate,acceptedDate,fiscalYear,"
            "period,cashAndShortTermInvestments,netReceivables,inventory,"
            "totalCurrentAssets,propertyPlantEquipmentNet,totalNonCurrentAssets,"
            "totalAssets,accountPayables,shortTermDebt,totalCurrentLiabilities,"
            "longTermDebt,totalNonCurrentLiabilities,totalLiabilities,commonStock,"
            "retainedEarnings,totalStockholdersEquity,totalEquity,"
            "totalLiabilitiesAndTotalEquity,totalInvestments,totalDebt,netDebt\n"
            "2025-03-31,000001.SZ,CNY,0000000000,2025-05-31,"
            "2025-03-31 07:00:00,2025,Q1,1985000,9666577000,4520000,"
            "9700830000,194000,238171027000,247871857000,3861497000,"
            "4842848000,8851455000,178923999000,232235780000,244087635000,"
            "5550277000,-5066509000,6784622000,6784622000,247871857000,"
            "237373355000,183766847000,183764862000\n"
        )
        mock_request.return_value = self._mock_csv_response(csv_text)
        results = fmp_client.batch.get_balance_sheet_bulk(2025, "Q1")
        assert results[0].total_assets == 247871857000
        assert results[0].net_debt == 183764862000

    @patch("httpx.Client.request")
    def test_get_balance_sheet_growth_bulk(self, mock_request, fmp_client):
        """Test fetching balance sheet growth bulk data"""
        csv_text = (
            "symbol,date,fiscalYear,period,reportedCurrency,"
            "growthCashAndCashEquivalents\n"
            "000001.SZ,2025-03-31,2025,Q1,CNY,0.09574482\n"
        )
        mock_request.return_value = self._mock_csv_response(csv_text)
        results = fmp_client.batch.get_balance_sheet_growth_bulk(2025, "Q1")
        assert results[0].model_extra["growthCashAndCashEquivalents"] == "0.09574482"

    @patch("httpx.Client.request")
    def test_get_cash_flow_bulk(self, mock_request, fmp_client):
        """Test fetching cash flow bulk data"""
        csv_text = (
            "date,symbol,reportedCurrency,cik,filingDate,acceptedDate,fiscalYear,"
            "period,netIncome\n"
            "2025-03-31,000001.SZ,CNY,0000000000,2025-03-31,"
            "2025-03-31 00:00:00,2025,Q1,0\n"
        )
        mock_request.return_value = self._mock_csv_response(csv_text)
        results = fmp_client.batch.get_cash_flow_bulk(2025, "Q1")
        assert results[0].symbol == "000001.SZ"

    @patch("httpx.Client.request")
    def test_get_cash_flow_growth_bulk(self, mock_request, fmp_client):
        """Test fetching cash flow growth bulk data"""
        csv_text = (
            "symbol,date,fiscalYear,period,reportedCurrency,growthOperatingCashFlow\n"
            "000001.SZ,2025-03-31,2025,Q1,CNY,3.20728\n"
        )
        mock_request.return_value = self._mock_csv_response(csv_text)
        results = fmp_client.batch.get_cash_flow_growth_bulk(2025, "Q1")
        assert results[0].model_extra["growthOperatingCashFlow"] == "3.20728"

    @patch("httpx.Client.request")
    def test_get_eod_bulk(self, mock_request, fmp_client):
        """Test fetching EOD bulk data"""
        csv_text = (
            "symbol,date,open,low,high,close,adjClose,volume\n"
            "EGS745W1C011.CA,2024-10-22,2.67,2.7,2.9,2.93,2.93,920904\n"
        )
        mock_request.return_value = self._mock_csv_response(csv_text)
        results = fmp_client.batch.get_eod_bulk(date(2024, 10, 22))
        assert results[0].symbol == "EGS745W1C011.CA"
        assert results[0].adj_close == 2.93
        params = mock_request.call_args.kwargs["params"]
        assert params["date"] == "2024-10-22"

    @patch("httpx.Client.request")
    def test_get_aftermarket_trades(self, mock_request, fmp_client, mock_response):
        """Test fetching aftermarket trades"""
        trade_data = {"symbol": "AAPL", "price": 151.00, "size": 100, "timestamp": 123}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[trade_data]
        )
        result = fmp_client.batch.get_aftermarket_trades(["AAPL"])
        assert len(result) == 1
        assert isinstance(result[0], AftermarketTrade)
        assert result[0].price == 151.00

    @patch("httpx.Client.request")
    def test_get_aftermarket_quotes(self, mock_request, fmp_client, mock_response):
        """Test fetching aftermarket quotes"""
        quote_data = {
            "symbol": "AAPL",
            "ask": 151.50,
            "bid": 151.00,
            "asize": 500,
            "bsize": 400,
        }
        mock_request.return_value = mock_response(
            status_code=200, json_data=[quote_data]
        )
        result = fmp_client.batch.get_aftermarket_quotes(["AAPL"])
        assert len(result) == 1
        assert isinstance(result[0], AftermarketQuote)
        assert result[0].ask == 151.50

    @patch("httpx.Client.request")
    def test_get_exchange_quotes(
        self, mock_request, fmp_client, mock_response, batch_quote_data
    ):
        """Test fetching exchange quotes"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[batch_quote_data]
        )
        result = fmp_client.batch.get_exchange_quotes("NASDAQ")
        assert len(result) == 1
        assert isinstance(result[0], BatchQuote)

    @pytest.mark.parametrize(
        "method_name,kwargs,expected_params",
        [
            (
                "get_exchange_quotes",
                {"exchange": "NASDAQ", "short": True},
                {"exchange": "NASDAQ", "short": True},
            ),
            ("get_mutualfund_quotes", {"short": True}, {"short": True}),
            ("get_etf_quotes", {"short": True}, {"short": True}),
            ("get_commodity_quotes", {"short": True}, {"short": True}),
            ("get_crypto_quotes", {"short": True}, {"short": True}),
            ("get_forex_quotes", {"short": True}, {"short": True}),
            ("get_index_quotes", {"short": True}, {"short": True}),
        ],
    )
    @patch("httpx.Client.request")
    def test_batch_short_param(
        self,
        mock_request,
        fmp_client,
        mock_response,
        method_name,
        kwargs,
        expected_params,
    ):
        """Test short param forwarding for batch quote endpoints"""
        short_data = {"symbol": "AAPL", "price": 150.25, "change": 2.25, "volume": 10}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[short_data]
        )

        method = getattr(fmp_client.batch, method_name)
        method(**kwargs)

        params = mock_request.call_args.kwargs["params"]
        for key, value in expected_params.items():
            assert params[key] == value

    @patch("httpx.Client.request")
    def test_get_market_caps(self, mock_request, fmp_client, mock_response):
        """Test fetching batch market caps"""
        cap_data = {"symbol": "AAPL", "date": "2024-01-01", "marketCap": 2500000000000}
        mock_request.return_value = mock_response(status_code=200, json_data=[cap_data])
        result = fmp_client.batch.get_market_caps(["AAPL"])
        assert len(result) == 1
        assert isinstance(result[0], BatchMarketCap)
        assert result[0].market_cap == 2500000000000


class TestAsyncBatchClient:
    """Tests for async batch client validation error handling"""

    @pytest.mark.asyncio
    async def test_upgrades_downgrades_consensus_bulk_with_invalid_rows(self):
        """Test async upgrades/downgrades consensus handles validation errors"""
        from fmp_data.batch.async_client import AsyncBatchClient

        # Create mock client
        mock_client = Mock()
        mock_client.logger = Mock()

        # Mock CSV response with one invalid row (invalid number format)
        csv_text = (
            "symbol,strongBuy,buy,hold,sell,strongSell,consensus\n"
            "INVALID,NOT_A_NUMBER,1,1,0,0,Buy\n"  # Invalid: strongBuy should be int
            "AAPL,1,29,11,4,0,Buy\n"
        )
        # Async client expects bytes
        mock_client.request_async = AsyncMock(return_value=csv_text.encode("utf-8"))

        async_batch = AsyncBatchClient(mock_client)
        results = await async_batch.get_upgrades_downgrades_consensus_bulk()

        # Should skip invalid row and return only valid one
        assert len(results) == 1
        assert results[0].symbol == "AAPL"
        # Should have logged a warning about the invalid row
        mock_client.logger.warning.assert_called()
