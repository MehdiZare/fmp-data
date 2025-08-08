from datetime import date, datetime
from unittest.mock import patch

import pytest

from fmp_data.institutional.models import (
    CIKMapping,
    FailToDeliver,
    Form13F,
    HolderPerformanceSummary,
    InsiderStatistic,
    InsiderTrade,
    InsiderTradingByName,
    InsiderTradingLatest,
    InsiderTradingSearch,
    InsiderTradingStatistics,
    InstitutionalHolder,
    InstitutionalHolding,
    InstitutionalOwnershipDates,
    InstitutionalOwnershipExtract,
    InstitutionalOwnershipLatest,
    SymbolPositionsSummary,
)


@pytest.fixture
def mock_13f_filing():
    """Mock 13F filing data"""
    return {
        "date": "2023-09-30",
        "fillingDate": "2023-11-16",
        "acceptedDate": "2023-11-16",
        "cik": "0001067983",
        "cusip": "G6683N103",
        "tickercusip": "NU",
        "nameOfIssuer": "NU HLDGS LTD",
        "shares": 107118784,
        "titleOfClass": "ORD SHS CL A",
        "value": 776611184.0,
        "link": "https://www.sec.gov/Archives/edgar/data/1067983/000095012323011029/0000950123-23-011029-index.htm",
        "linkFinal": "https://www.sec.gov/Archives/edgar/data/1067983/000095012323011029/28498.xml",
    }


@pytest.fixture
def mock_insider_trade():
    """Mock insider trade data"""
    return {
        "symbol": "AAPL",
        "filingDate": "2024-01-07T00:00:00",
        "transactionDate": "2024-01-05",
        "reportingCik": "0001214128",
        "transactionType": "S-SALE",
        "securitiesOwned": 150000.0,
        "companyCik": "0000320193",
        "reportingName": "Cook Timothy",
        "typeOfOwner": "CEO",
        "acquistionOrDisposition": "D",
        "formType": "4",
        "securitiesTransacted": 50000.0,
        "price": 150.25,
        "securityName": "Common Stock",
        "link": "https://www.sec.gov/Archives/edgar/data/...",
    }


@pytest.fixture
def mock_institutional_holder():
    """Mock institutional holder data"""
    return {"cik": "0001905393", "name": "PCG WEALTH ADVISORS, LLC"}


@pytest.fixture
def mock_institutional_holding():
    """Mock institutional holding data"""
    return {
        "symbol": "AAPL",
        "cik": "0000320193",
        "date": "2024-06-30",
        "investorsHolding": 5181,
        "lastInvestorsHolding": 5164,
        "investorsHoldingChange": 17,
        "numberOf13Fshares": 9315793861,
        "lastNumberOf13Fshares": 9133859544,
        "numberOf13FsharesChange": 181934317,
        "totalInvested": 1988382372981.0,
        "lastTotalInvested": 1593047802343.0,
        "totalInvestedChange": 395334570638.0,
        "ownershipPercent": 60.4692,
        "lastOwnershipPercent": 59.2882,
        "ownershipPercentChange": 1.0199,
    }


@pytest.fixture
def mock_insider_statistic():
    """Mock insider statistics data"""
    return {
        "symbol": "AAPL",
        "cik": "0000320193",
        "year": 2024,
        "quarter": 1,
        "purchases": 5,
        "sales": 10,
        "buySellRatio": 0.5,
        "totalBought": 25000,
        "totalSold": 75000,
        "averageBought": 5000.0,
        "averageSold": 7500.0,
        "pPurchases": 3,
        "sSales": 7,
    }


@pytest.fixture
def mock_fail_to_deliver():
    """Mock fail to deliver data"""
    return {
        "symbol": "AAPL",
        "date": "2024-11-14",
        "price": 225.12,
        "quantity": 444,
        "cusip": "037833100",
        "name": "APPLE INC;COM NPV",
    }


@pytest.fixture
def mock_cik_mapping():
    """Mock CIK mapping data"""
    return {"reportingCik": "0001758386", "reportingName": "Young Bradford Addison"}


class TestInstitutionalModels:
    def test_form_13f_model(self, mock_13f_filing):
        """Test Form13F model validation"""
        filing = Form13F.model_validate(mock_13f_filing)
        assert filing.cik == "0001067983"
        assert isinstance(filing.form_date, date)
        assert filing.cusip == "G6683N103"
        assert filing.ticker == "NU"
        assert isinstance(filing.value, float)
        assert filing.shares == 107118784
        assert filing.class_title == "ORD SHS CL A"
        assert filing.link_final is not None

    def test_insider_trade_model(self, mock_insider_trade):
        """Test InsiderTrade model validation"""
        trade = InsiderTrade.model_validate(mock_insider_trade)
        assert trade.symbol == "AAPL"
        assert isinstance(trade.filing_date, datetime)
        assert isinstance(trade.transaction_date, date)
        assert trade.reporting_name == "Cook Timothy"
        assert trade.type_of_owner == "CEO"
        assert isinstance(trade.price, float)
        assert trade.securities_transacted == 50000.0

    def test_institutional_holder_model(self, mock_institutional_holder):
        """Test InstitutionalHolder model validation"""
        holder = InstitutionalHolder.model_validate(mock_institutional_holder)
        assert holder.cik == "0001905393"
        assert holder.name == "PCG WEALTH ADVISORS, LLC"

    def test_institutional_holding_model(self, mock_institutional_holding):
        """Test InstitutionalHolding model validation"""
        holding = InstitutionalHolding.model_validate(mock_institutional_holding)
        assert holding.symbol == "AAPL"
        assert isinstance(holding.report_date, date)
        assert isinstance(holding.ownership_percent, float)
        assert holding.investors_holding == 5181
        assert holding.number_of_13f_shares == 9315793861
        assert isinstance(holding.total_invested, float)

    def test_insider_statistic_model(self, mock_insider_statistic):
        """Test InsiderStatistic model validation"""
        stats = InsiderStatistic.model_validate(mock_insider_statistic)
        assert stats.symbol == "AAPL"
        assert stats.year == 2024
        assert stats.quarter == 1
        assert isinstance(stats.buy_sell_ratio, float)
        assert stats.total_bought == 25000
        assert stats.total_sold == 75000
        assert isinstance(stats.average_bought, float)

    def test_fail_to_deliver_model(self, mock_fail_to_deliver):
        """Test FailToDeliver model validation"""
        ftd = FailToDeliver.model_validate(mock_fail_to_deliver)
        assert ftd.symbol == "AAPL"
        assert isinstance(ftd.fail_date, date)  # Changed from date to fail_date
        assert ftd.price == 225.12
        assert ftd.quantity == 444
        assert ftd.cusip == "037833100"
        assert ftd.name == "APPLE INC;COM NPV"

    def test_cik_mapping_model(self, mock_cik_mapping):
        """Test CIKMapping model validation with actual API response structure"""
        mapping = CIKMapping.model_validate(mock_cik_mapping)
        assert mapping.reporting_cik == "0001758386"
        assert mapping.reporting_name == "Young Bradford Addison"


class TestInstitutionalClient:
    @pytest.fixture
    def mock_response(self):
        """Create mock response helper"""

        def create_response(status_code=200, json_data=None):
            class MockResponse:
                def __init__(self, status_code, json_data):
                    self.status_code = status_code
                    self._json_data = json_data

                def json(self):
                    return self._json_data

                def raise_for_status(self):
                    if self.status_code >= 400:
                        raise Exception(f"HTTP {self.status_code}")

            return MockResponse(status_code, json_data)

        return create_response

    @patch("httpx.Client.request")
    def test_get_form_13f(
        self, mock_request, fmp_client, mock_response, mock_13f_filing
    ):
        """Test getting Form 13F filing"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_13f_filing]
        )

        filing = fmp_client.institutional.get_form_13f(
            "0001067983", filing_date=date(2024, 1, 5)
        )
        assert isinstance(filing, list)
        assert isinstance(filing[0], Form13F)
        assert filing[0].cik == "0001067983"
        assert filing[0].value == 776611184.0

    @patch("httpx.Client.request")
    def test_get_insider_trades(
        self, mock_request, fmp_client, mock_response, mock_insider_trade
    ):
        """Test getting insider trades"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_insider_trade]
        )

        trades = fmp_client.institutional.get_insider_trades("AAPL")
        assert isinstance(trades, list)
        assert len(trades) == 1
        assert isinstance(trades[0], InsiderTrade)
        assert trades[0].securities_transacted == 50000.0
        assert trades[0].type_of_owner == "CEO"

    @patch("httpx.Client.request")
    def test_get_institutional_holders(
        self, mock_request, fmp_client, mock_response, mock_institutional_holder
    ):
        """Test getting institutional holders"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_institutional_holder]
        )

        holders = fmp_client.institutional.get_institutional_holders()
        assert isinstance(holders, list)
        assert len(holders) == 1
        assert isinstance(holders[0], InstitutionalHolder)
        assert holders[0].cik == "0001905393"

    @patch("httpx.Client.request")
    def test_get_institutional_holdings(
        self, mock_request, fmp_client, mock_response, mock_institutional_holding
    ):
        """Test getting institutional holdings"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_institutional_holding]
        )

        holdings = fmp_client.institutional.get_institutional_holdings("AAPL")
        assert isinstance(holdings, list)
        assert len(holdings) == 1
        assert isinstance(holdings[0], InstitutionalHolding)
        assert holdings[0].symbol == "AAPL"
        assert holdings[0].investors_holding == 5181
        assert holdings[0].total_invested == 1988382372981.0

    @patch("httpx.Client.request")
    def test_get_cik_by_symbol(self, mock_request, fmp_client, mock_response):
        """Test getting CIK mapping by symbol - method removed"""
        pytest.skip("Method get_cik_by_symbol was removed from client")


class TestInstitutionalClientEnhanced:
    """Test enhanced institutional client methods"""

    @patch("httpx.Client.request")
    def test_get_insider_trading_latest(
        self, mock_request, fmp_client, mock_response, mock_insider_trade
    ):
        """Test getting latest insider trading activity"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_insider_trade]
        )

        trades = fmp_client.institutional.get_insider_trading_latest()
        assert isinstance(trades, list)
        assert len(trades) == 1
        assert isinstance(trades[0], InsiderTradingLatest)
        assert trades[0].symbol == "AAPL"

    @patch("httpx.Client.request")
    def test_search_insider_trading(
        self, mock_request, fmp_client, mock_response, mock_insider_trade
    ):
        """Test searching insider trading with filters"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_insider_trade]
        )

        trades = fmp_client.institutional.search_insider_trading(symbol="AAPL")
        assert isinstance(trades, list)
        assert len(trades) == 1
        assert isinstance(trades[0], InsiderTradingSearch)
        assert trades[0].symbol == "AAPL"

    @patch("httpx.Client.request")
    def test_get_insider_trading_by_name(
        self, mock_request, fmp_client, mock_response, mock_insider_trade
    ):
        """Test getting insider trading by reporting name"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_insider_trade]
        )

        trades = fmp_client.institutional.get_insider_trading_by_name("Cook Timothy")
        assert isinstance(trades, list)
        assert len(trades) == 1
        assert isinstance(trades[0], InsiderTradingByName)
        assert trades[0].reporting_name == "Cook Timothy"

    @patch("httpx.Client.request")
    def test_get_insider_trading_statistics_enhanced(
        self, mock_request, fmp_client, mock_response
    ):
        """Test getting enhanced insider trading statistics"""
        mock_stats = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "year": 2023,
            "quarter": 4,
            "purchases": 15,
            "sales": 25,
            "buySellRatio": 0.6,
            "totalBought": 50000,
            "totalSold": 75000,
            "averageBought": 3333.33,
            "averageSold": 3000.0,
            "pPurchases": 10,
            "sSales": 20,
        }
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_stats]
        )

        stats = fmp_client.institutional.get_insider_trading_statistics_enhanced("AAPL")
        assert isinstance(stats, InsiderTradingStatistics)
        assert stats.symbol == "AAPL"
        assert stats.purchases == 15

    @patch("httpx.Client.request")
    def test_get_institutional_ownership_latest(
        self, mock_request, fmp_client, mock_response
    ):
        """Test getting latest institutional ownership filings"""
        mock_ownership = {
            "cik": "0001067983",
            "date": "2023-09-30",
            "symbol": "AAPL",
            "companyName": "Apple Inc",
            "shares": 1000000,
            "value": 175000000.0,
            "weight": 2.5,
            "change": 50000,
            "changePercent": 5.0,
        }
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_ownership]
        )

        ownership = fmp_client.institutional.get_institutional_ownership_latest()
        assert isinstance(ownership, list)
        assert len(ownership) == 1
        assert isinstance(ownership[0], InstitutionalOwnershipLatest)
        assert ownership[0].symbol == "AAPL"
        assert ownership[0].filing_date.strftime("%Y-%m-%d") == "2023-09-30"

    @patch("httpx.Client.request")
    def test_get_institutional_ownership_extract(
        self, mock_request, fmp_client, mock_response
    ):
        """Test getting filings extract data"""
        mock_extract = {
            "cik": "0001067983",
            "date": "2023-09-30",
            "nameOfIssuer": "Apple Inc",
            "titleOfClass": "COM",
            "cusip": "037833100",
            "value": 175000000.0,
            "sharesPrnAmt": 1000000,
            "sharesPrnType": "SH",
            "putCall": None,
            "investmentDiscretion": "SOLE",
            "otherManager": None,
            "votingAuthoritySole": 1000000,
            "votingAuthorityShared": 0,
            "votingAuthorityNone": 0,
        }
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_extract]
        )

        extract = fmp_client.institutional.get_institutional_ownership_extract(
            "0001067983", date(2023, 9, 30)
        )
        assert isinstance(extract, list)
        assert len(extract) == 1
        assert isinstance(extract[0], InstitutionalOwnershipExtract)
        assert extract[0].cik == "0001067983"

    @patch("httpx.Client.request")
    def test_get_institutional_ownership_dates(
        self, mock_request, fmp_client, mock_response
    ):
        """Test getting Form 13F filing dates"""
        mock_dates = {"cik": "0001067983", "date": "2023-09-30"}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_dates]
        )

        dates = fmp_client.institutional.get_institutional_ownership_dates("0001067983")
        assert isinstance(dates, list)
        assert len(dates) == 1
        assert isinstance(dates[0], InstitutionalOwnershipDates)
        assert dates[0].cik == "0001067983"

    @patch("httpx.Client.request")
    def test_get_holder_performance_summary(
        self, mock_request, fmp_client, mock_response
    ):
        """Test getting holder performance summary"""
        mock_performance = {
            "cik": "0001067983",
            "name": "Berkshire Hathaway Inc",
            "totalValue": 7500000000.0,
            "entries": 50,
            "change": 250000000.0,
            "changePercent": 3.45,
        }
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_performance]
        )

        performance = fmp_client.institutional.get_holder_performance_summary(
            "0001067983"
        )
        assert isinstance(performance, list)
        assert len(performance) == 1
        assert isinstance(performance[0], HolderPerformanceSummary)
        assert performance[0].name == "Berkshire Hathaway Inc"

    @patch("httpx.Client.request")
    def test_get_symbol_positions_summary(
        self, mock_request, fmp_client, mock_response
    ):
        """Test getting positions summary by symbol"""
        mock_positions = {
            "symbol": "AAPL",
            "totalPositions": 3500,
            "totalShares": 15000000000,
            "totalValue": 2625000000000.0,
            "avgWeight": 4.2,
            "change": 500000000,
            "changePercent": 3.45,
        }
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_positions]
        )

        positions = fmp_client.institutional.get_symbol_positions_summary("AAPL")
        assert isinstance(positions, list)
        assert len(positions) == 1
        assert isinstance(positions[0], SymbolPositionsSummary)
        assert positions[0].symbol == "AAPL"
