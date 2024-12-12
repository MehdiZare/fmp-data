from datetime import date, datetime
from unittest.mock import patch

import pytest

from fmp_data.institutional.models import (
    CIKCompanyMap,
    CIKMapping,
    FailToDeliver,
    Form13F,
    InsiderStatistic,
    InsiderTrade,
    InstitutionalHolder,
    InstitutionalHolding,
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
        """Test getting CIK mapping by symbol"""
        # Updated mock response to match expected structure
        mock_data = {"symbol": "AAPL", "companyCik": "0000320193"}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_data]
        )

        mappings = fmp_client.institutional.get_cik_by_symbol("AAPL")
        assert isinstance(mappings, list)
        assert len(mappings) == 1
        assert isinstance(mappings[0], CIKCompanyMap)  # Using correct model
        assert mappings[0].symbol == "AAPL"
        assert mappings[0].cik == "0000320193"  # Using aliased field name
