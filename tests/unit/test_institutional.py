from datetime import date, datetime
from unittest.mock import Mock, patch
import warnings

import pytest

from fmp_data.exceptions import FMPError
from fmp_data.institutional.models import (
    CIKMapping,
    FailToDeliver,
    Form13F,
    HolderIndustryBreakdown,
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
        "filingDate": "2023-11-16",
        "acceptedDate": "2023-11-16",
        "cik": "0001067983",
        "securityCusip": "G6683N103",
        "symbol": "NU",
        "nameOfIssuer": "NU HLDGS LTD",
        "shares": 107118784,
        "titleOfClass": "ORD SHS CL A",
        "value": 776611184.0,
        "link": "https://www.sec.gov/Archives/edgar/data/1067983/000095012323011029/0000950123-23-011029-index.htm",
        "finalLink": "https://www.sec.gov/Archives/edgar/data/1067983/000095012323011029/28498.xml",
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
        "acquiredTransactions": 5,
        "disposedTransactions": 10,
        "acquiredDisposedRatio": 0.5,
        "totalAcquired": 25000,
        "totalDisposed": 75000,
        "averageAcquired": 5000.0,
        "averageDisposed": 7500.0,
        "totalPurchases": 3,
        "totalSales": 7,
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
        assert filing.symbol == "NU"
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
        assert isinstance(stats.acquired_disposed_ratio, float)
        assert stats.total_acquired == 25000
        assert stats.total_disposed == 75000
        assert isinstance(stats.average_acquired, float)

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

                def close(self):
                    pass

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
            "0001067983", report_date=date(2024, 1, 5)
        )
        assert isinstance(filing, list)
        assert isinstance(filing[0], Form13F)
        assert filing[0].cik == "0001067983"
        assert filing[0].value == 776611184.0

    def test_get_form_13f_returns_empty_on_error(self, fmp_client):
        """Test get_form_13f returns empty list when request fails."""
        fmp_client._logger = Mock()
        with patch.object(fmp_client, "request", side_effect=FMPError("API error")):
            result = fmp_client.institutional.get_form_13f(
                "0001067983", report_date=date(2024, 1, 5)
            )

        assert result == []
        fmp_client._logger.warning.assert_called_once()
        assert "0001067983" in fmp_client._logger.warning.call_args[0][0]

    @patch("httpx.Client.request")
    def test_get_form_13f_by_quarter(
        self, mock_request, fmp_client, mock_response, mock_13f_filing
    ):
        """The wire-shaped method takes year/quarter, as the API does (#188)."""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_13f_filing]
        )

        filing = fmp_client.institutional.get_form_13f_by_quarter(
            "0001067983", year=2023, quarter=3
        )
        assert isinstance(filing, list)
        assert isinstance(filing[0], Form13F)
        assert filing[0].cik == "0001067983"

        sent = mock_request.call_args.kwargs["params"]
        assert sent["year"] == 2023
        assert sent["quarter"] == 3
        assert "date" not in sent
        assert "report_date" not in sent

    def test_get_form_13f_delegates_to_by_quarter(self, fmp_client):
        """``report_date`` is a convenience over the wire shape, not a param."""
        with patch.object(
            fmp_client.institutional, "get_form_13f_by_quarter", return_value=[]
        ) as by_quarter:
            result = fmp_client.institutional.get_form_13f(
                "0001067983", report_date=date(2023, 8, 15)
            )

        assert result == []
        # Any date inside the period resolves to that calendar quarter.
        by_quarter.assert_called_once_with("0001067983", 2023, 3)

    def test_get_form_13f_by_quarter_returns_empty_on_error(self, fmp_client):
        """Error swallowing lives on the method the tools actually call."""
        fmp_client._logger = Mock()
        with patch.object(fmp_client, "request", side_effect=FMPError("API error")):
            result = fmp_client.institutional.get_form_13f_by_quarter(
                "0001067983", 2023, 3
            )

        assert result == []
        fmp_client._logger.warning.assert_called_once()
        assert "0001067983" in fmp_client._logger.warning.call_args[0][0]

    def test_get_form_13f_dates_returns_empty_on_error(self, fmp_client):
        """Test get_form_13f_dates returns empty list when request fails."""
        fmp_client._logger = Mock()
        with patch.object(fmp_client, "request", side_effect=FMPError("API error")):
            result = fmp_client.institutional.get_form_13f_dates("0001067983")

        assert result == []
        fmp_client._logger.warning.assert_called_once()
        assert "0001067983" in fmp_client._logger.warning.call_args[0][0]

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

        holdings = fmp_client.institutional.get_institutional_holdings(
            "AAPL", report_date=date(2024, 6, 30)
        )
        assert isinstance(holdings, list)
        assert len(holdings) == 1
        assert isinstance(holdings[0], InstitutionalHolding)
        assert holdings[0].symbol == "AAPL"
        assert holdings[0].investors_holding == 5181
        assert holdings[0].total_invested == 1988382372981.0

    @patch("httpx.Client.request")
    def test_get_institutional_holdings_by_quarter(
        self, mock_request, fmp_client, mock_response, mock_institutional_holding
    ):
        """The wire-shaped holdings method takes year/quarter (#188)."""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_institutional_holding]
        )

        holdings = fmp_client.institutional.get_institutional_holdings_by_quarter(
            "AAPL", year=2024, quarter=2
        )
        assert isinstance(holdings, list)
        assert holdings[0].symbol == "AAPL"

        sent = mock_request.call_args.kwargs["params"]
        assert sent["year"] == 2024
        assert sent["quarter"] == 2
        assert "date" not in sent

    def test_get_institutional_holdings_delegates_to_by_quarter(self, fmp_client):
        """An explicit year/quarter still wins over the derived pair."""
        with patch.object(
            fmp_client.institutional,
            "get_institutional_holdings_by_quarter",
            return_value=[],
        ) as by_quarter:
            fmp_client.institutional.get_institutional_holdings(
                "AAPL", report_date=date(2024, 6, 30)
            )
            by_quarter.assert_called_once_with("AAPL", 2024, 2)

            by_quarter.reset_mock()
            fmp_client.institutional.get_institutional_holdings(
                "AAPL", report_date=date(2024, 6, 30), year=2023, quarter=4
            )
            by_quarter.assert_called_once_with("AAPL", 2023, 4)

    def test_search_cik_by_name_filters_results(self, fmp_client):
        """Test search_cik_by_name filters results case-insensitively."""
        mapping_match = CIKMapping(
            reporting_cik="0001758386",
            reporting_name="Acme Capital Partners",
        )
        mapping_other = CIKMapping(
            reporting_cik="0000000001",
            reporting_name="Other Holdings",
        )

        with patch.object(
            fmp_client, "request", return_value=[mapping_match, mapping_other]
        ):
            results = fmp_client.institutional.search_cik_by_name("acme")

        assert results == [mapping_match]

    def test_search_cik_by_name_wraps_single_result(self, fmp_client):
        """Test search_cik_by_name handles non-list responses."""
        mapping = CIKMapping(
            reporting_cik="0001758386",
            reporting_name="Acme Capital Partners",
        )

        with patch.object(fmp_client, "request", return_value=mapping):
            results = fmp_client.institutional.search_cik_by_name("ACME")

        assert results == [mapping]


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

        trades = fmp_client.institutional.get_insider_trading_latest(
            page=0, limit=50, trade_date=date(2024, 1, 5)
        )
        assert isinstance(trades, list)
        assert len(trades) == 1
        assert isinstance(trades[0], InsiderTradingLatest)
        assert trades[0].symbol == "AAPL"
        _, kwargs = mock_request.call_args
        assert kwargs["params"]["page"] == 0
        assert kwargs["params"]["limit"] == 50
        assert kwargs["params"]["date"] == date(2024, 1, 5)

    @patch("httpx.Client.request")
    def test_search_insider_trading(
        self, mock_request, fmp_client, mock_response, mock_insider_trade
    ):
        """Test searching insider trading with filters"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_insider_trade]
        )

        trades = fmp_client.institutional.search_insider_trading(
            symbol="AAPL",
            reporting_cik="0001214128",
            company_cik="0000320193",
            transaction_type="S-Sale",
        )
        assert isinstance(trades, list)
        assert len(trades) == 1
        assert isinstance(trades[0], InsiderTradingSearch)
        assert trades[0].symbol == "AAPL"
        _, kwargs = mock_request.call_args
        assert kwargs["params"]["symbol"] == "AAPL"
        assert kwargs["params"]["reportingCik"] == "0001214128"
        assert kwargs["params"]["companyCik"] == "0000320193"
        assert kwargs["params"]["transactionType"] == "S-Sale"

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
            "acquiredTransactions": 15,
            "disposedTransactions": 25,
            "acquiredDisposedRatio": 0.6,
            "totalAcquired": 50000,
            "totalDisposed": 75000,
            "averageAcquired": 3333.33,
            "averageDisposed": 3000.0,
            "totalPurchases": 10,
            "totalSales": 20,
        }
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_stats]
        )

        stats = fmp_client.institutional.get_insider_trading_statistics_enhanced("AAPL")
        assert isinstance(stats, InsiderTradingStatistics)
        assert stats.symbol == "AAPL"
        assert stats.acquired_transactions == 15

    @patch("httpx.Client.request")
    def test_get_institutional_ownership_latest(
        self, mock_request, fmp_client, mock_response
    ):
        """Test getting latest institutional ownership filings"""
        mock_ownership = {
            "cik": "0001067983",
            "name": "Berkshire Hathaway Inc",
            "date": "2023-09-30",
            "filingDate": "2023-11-15T00:00:00",
            "acceptedDate": "2023-11-15T10:30:00",
            "formType": "13F-HR",
            "link": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001067983",
            "finalLink": "https://www.sec.gov/Archives/edgar/data/1067983/000095012323011029/28498.xml",
        }
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_ownership]
        )

        ownership = fmp_client.institutional.get_institutional_ownership_latest()
        assert isinstance(ownership, list)
        assert len(ownership) == 1
        assert isinstance(ownership[0], InstitutionalOwnershipLatest)
        assert ownership[0].cik == "0001067983"
        assert ownership[0].report_date.strftime("%Y-%m-%d") == "2023-09-30"
        _, kwargs = mock_request.call_args
        assert kwargs["params"]["page"] == 0
        assert kwargs["params"]["limit"] == 100

    @patch("httpx.Client.request")
    def test_get_institutional_ownership_extract(
        self, mock_request, fmp_client, mock_response
    ):
        """Test getting filings extract data"""
        mock_extract = {
            "cik": "0001067983",
            "date": "2023-09-30",
            "filingDate": "2023-11-15",
            "acceptedDate": "2023-11-15",
            "securityCusip": "037833100",
            "symbol": "AAPL",
            "nameOfIssuer": "Apple Inc",
            "titleOfClass": "COM",
            "shares": 1000000,
            "sharesType": "SH",
            "putCallShare": None,
            "value": 175000000.0,
            "link": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001067983",
            "finalLink": "https://www.sec.gov/Archives/edgar/data/1067983/000095012323011029/28498.xml",
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
    def test_get_institutional_ownership_extract_by_quarter(
        self, mock_request, fmp_client, mock_response
    ):
        """Wire-shaped extract method takes year/quarter (#192)."""
        mock_extract = {
            "cik": "0001067983",
            "date": "2023-09-30",
            "filingDate": "2023-11-15",
            "acceptedDate": "2023-11-15",
            "securityCusip": "037833100",
            "symbol": "AAPL",
            "nameOfIssuer": "Apple Inc",
            "titleOfClass": "COM",
            "shares": 1000000,
            "sharesType": "SH",
            "putCallShare": None,
            "value": 175000000.0,
            "link": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001067983",
            "finalLink": "https://www.sec.gov/Archives/edgar/data/1067983/000095012323011029/28498.xml",
        }
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_extract]
        )

        extract = (
            fmp_client.institutional.get_institutional_ownership_extract_by_quarter(
                "0001067983", year=2023, quarter=3
            )
        )
        assert isinstance(extract, list)
        assert extract[0].cik == "0001067983"

        sent = mock_request.call_args.kwargs["params"]
        assert sent["year"] == 2023
        assert sent["quarter"] == 3
        assert "date" not in sent
        assert "report_date" not in sent

    def test_get_institutional_ownership_extract_delegates_to_by_quarter(
        self, fmp_client
    ):
        """report_date convenience derives year/quarter and delegates (#192)."""
        with patch.object(
            fmp_client.institutional,
            "get_institutional_ownership_extract_by_quarter",
            return_value=[],
        ) as by_quarter:
            result = fmp_client.institutional.get_institutional_ownership_extract(
                "0001067983", report_date=date(2023, 8, 15)
            )

        assert result == []
        by_quarter.assert_called_once_with("0001067983", 2023, 3)

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
            "date": "2023-09-30",
            "cik": "0001067983",
            "investorName": "Berkshire Hathaway Inc",
            "portfolioSize": 50,
            "securitiesAdded": 5,
            "securitiesRemoved": 3,
            "marketValue": 7500000000.0,
            "previousMarketValue": 7250000000.0,
            "changeInMarketValue": 250000000.0,
            "changeInMarketValuePercentage": 3.45,
            "averageHoldingPeriod": 12,
            "averageHoldingPeriodTop10": 15,
            "averageHoldingPeriodTop20": 14,
            "turnover": 0.05,
            "turnoverAlternateSell": 0.03,
            "turnoverAlternateBuy": 0.02,
            "performance": 500000000.0,
            "performancePercentage": 7.14,
            "lastPerformance": 450000000.0,
            "changeInPerformance": 50000000.0,
            "performance1year": 800000000.0,
            "performancePercentage1year": 12.0,
            "performance3year": 2000000000.0,
            "performancePercentage3year": 35.0,
            "performance5year": 3500000000.0,
            "performancePercentage5year": 60.0,
            "performanceSinceInception": 5000000000.0,
            "performanceSinceInceptionPercentage": 100.0,
            "performanceRelativeToSP500Percentage": 2.5,
            "performance1yearRelativeToSP500Percentage": 3.0,
            "performance3yearRelativeToSP500Percentage": 5.0,
            "performance5yearRelativeToSP500Percentage": 8.0,
            "performanceSinceInceptionRelativeToSP500Percentage": 15.0,
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
        assert performance[0].investor_name == "Berkshire Hathaway Inc"
        _, kwargs = mock_request.call_args
        assert kwargs["params"]["page"] == 0
        assert "year" not in kwargs["params"]
        assert "quarter" not in kwargs["params"]

    @patch("httpx.Client.request")
    def test_get_holder_performance_summary_by_quarter(
        self, mock_request, fmp_client, mock_response
    ):
        """Wire-shaped holder performance takes year/quarter (#192)."""
        mock_request.return_value = mock_response(status_code=200, json_data=[])

        fmp_client.institutional.get_holder_performance_summary_by_quarter(
            "0001067983", year=2023, quarter=3, page=1
        )

        sent = mock_request.call_args.kwargs["params"]
        assert sent["cik"] == "0001067983"
        assert sent["year"] == 2023
        assert sent["quarter"] == 3
        assert sent["page"] == 1
        assert "date" not in sent
        assert "report_date" not in sent

    @patch("httpx.Client.request")
    def test_get_holder_performance_summary_sends_derived_quarter(
        self, mock_request, fmp_client, mock_response
    ):
        """When report_date is set, the derived year/quarter reach the wire (#192).

        Asserted at the request rather than by patching the ``_by_quarter``
        sibling: the two public methods deliberately do **not** call each
        other, so that the inert-filter warning fires once and points at the
        caller's line on either route. A test that pins the internal call
        would forbid that arrangement while proving nothing about the request.
        """
        mock_request.return_value = mock_response(status_code=200, json_data=[])

        with pytest.warns(UserWarning, match="ignores year/quarter"):
            result = fmp_client.institutional.get_holder_performance_summary(
                "0001067983", report_date=date(2023, 9, 30), page=2
            )

        assert result == []
        sent = mock_request.call_args.kwargs["params"]
        assert sent["cik"] == "0001067983"
        assert sent["year"] == 2023
        assert sent["quarter"] == 3
        assert sent["page"] == 2

    def test_get_holder_performance_summary_without_date_skips_by_quarter(
        self, fmp_client
    ):
        """Without report_date, request is made without year/quarter (#192)."""
        with patch.object(fmp_client, "request", return_value=[]) as request:
            with patch.object(
                fmp_client.institutional,
                "get_holder_performance_summary_by_quarter",
            ) as by_quarter:
                result = fmp_client.institutional.get_holder_performance_summary(
                    "0001067983", page=0
                )

        assert result == []
        by_quarter.assert_not_called()
        # request is called with endpoint + kwargs; just ensure year/quarter absent
        call_kwargs = request.call_args.kwargs
        assert "year" not in call_kwargs
        assert "quarter" not in call_kwargs
        assert call_kwargs.get("cik") == "0001067983" or (
            request.call_args.args and True
        )
        # More precise: params passed as kwargs to request
        assert request.call_args.kwargs["cik"] == "0001067983"
        assert request.call_args.kwargs["page"] == 0

    @patch("httpx.Client.request")
    def test_get_institutional_ownership_analytics_by_quarter(
        self, mock_request, fmp_client, mock_response
    ):
        """Wire-shaped analytics method takes year/quarter (#192)."""
        mock_request.return_value = mock_response(status_code=200, json_data=[])

        fmp_client.institutional.get_institutional_ownership_analytics_by_quarter(
            "AAPL", year=2024, quarter=1, page=2, limit=50
        )

        sent = mock_request.call_args.kwargs["params"]
        assert sent["symbol"] == "AAPL"
        assert sent["year"] == 2024
        assert sent["quarter"] == 1
        assert sent["page"] == 2
        assert sent["limit"] == 50
        assert "date" not in sent
        assert "report_date" not in sent

    def test_get_institutional_ownership_analytics_delegates_to_by_quarter(
        self, fmp_client
    ):
        """report_date convenience derives year/quarter and delegates (#192)."""
        with patch.object(
            fmp_client.institutional,
            "get_institutional_ownership_analytics_by_quarter",
            return_value=[],
        ) as by_quarter:
            result = fmp_client.institutional.get_institutional_ownership_analytics(
                "AAPL", report_date=date(2024, 3, 31), page=2, limit=50
            )

        assert result == []
        by_quarter.assert_called_once_with("AAPL", 2024, 1, page=2, limit=50)

    @patch("httpx.Client.request")
    def test_get_holder_industry_breakdown_by_quarter(
        self, mock_request, fmp_client, mock_response
    ):
        """Wire-shaped industry breakdown takes year/quarter (#192)."""
        mock_request.return_value = mock_response(status_code=200, json_data=[])

        fmp_client.institutional.get_holder_industry_breakdown_by_quarter(
            "0001067983", year=2023, quarter=4
        )

        sent = mock_request.call_args.kwargs["params"]
        assert sent["cik"] == "0001067983"
        assert sent["year"] == 2023
        assert sent["quarter"] == 4
        assert "date" not in sent

    def test_get_holder_industry_breakdown_delegates_to_by_quarter(self, fmp_client):
        """report_date convenience derives year/quarter and delegates (#192)."""
        with patch.object(
            fmp_client.institutional,
            "get_holder_industry_breakdown_by_quarter",
            return_value=[],
        ) as by_quarter:
            result = fmp_client.institutional.get_holder_industry_breakdown(
                "0001067983", report_date=date(2023, 12, 15)
            )

        assert result == []
        by_quarter.assert_called_once_with("0001067983", 2023, 4)

    @patch("httpx.Client.request")
    def test_get_symbol_positions_summary(
        self, mock_request, fmp_client, mock_response
    ):
        """Test getting positions summary by symbol"""
        mock_positions = {
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
            "newPositions": 50,
            "lastNewPositions": 45,
            "newPositionsChange": 5,
            "increasedPositions": 200,
            "lastIncreasedPositions": 180,
            "increasedPositionsChange": 20,
            "closedPositions": 30,
            "lastClosedPositions": 25,
            "closedPositionsChange": 5,
            "reducedPositions": 100,
            "lastReducedPositions": 90,
            "reducedPositionsChange": 10,
        }
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_positions]
        )

        positions = fmp_client.institutional.get_symbol_positions_summary(
            "AAPL", report_date=date(2024, 6, 30)
        )
        assert isinstance(positions, list)
        assert len(positions) == 1
        assert isinstance(positions[0], SymbolPositionsSummary)
        assert positions[0].symbol == "AAPL"

    @patch("httpx.Client.request")
    def test_get_symbol_positions_summary_by_quarter(
        self, mock_request, fmp_client, mock_response
    ):
        """Wire-shaped positions summary takes year/quarter (#192)."""
        mock_request.return_value = mock_response(status_code=200, json_data=[])

        fmp_client.institutional.get_symbol_positions_summary_by_quarter(
            "AAPL", year=2024, quarter=2
        )

        sent = mock_request.call_args.kwargs["params"]
        assert sent["symbol"] == "AAPL"
        assert sent["year"] == 2024
        assert sent["quarter"] == 2
        assert "date" not in sent

    def test_get_symbol_positions_summary_delegates_to_by_quarter(self, fmp_client):
        """report_date convenience derives year/quarter and delegates (#192)."""
        with patch.object(
            fmp_client.institutional,
            "get_symbol_positions_summary_by_quarter",
            return_value=[],
        ) as by_quarter:
            result = fmp_client.institutional.get_symbol_positions_summary(
                "AAPL", report_date=date(2024, 6, 30)
            )

        assert result == []
        by_quarter.assert_called_once_with("AAPL", 2024, 2)

    @patch("httpx.Client.request")
    def test_get_industry_performance_summary_by_quarter(
        self, mock_request, fmp_client, mock_response
    ):
        """Wire-shaped industry performance takes year/quarter (#192)."""
        mock_request.return_value = mock_response(status_code=200, json_data=[])

        fmp_client.institutional.get_industry_performance_summary_by_quarter(
            year=2024, quarter=1
        )

        sent = mock_request.call_args.kwargs["params"]
        assert sent["year"] == 2024
        assert sent["quarter"] == 1
        assert "date" not in sent

    def test_get_industry_performance_summary_delegates_to_by_quarter(self, fmp_client):
        """report_date convenience derives year/quarter and delegates (#192)."""
        with patch.object(
            fmp_client.institutional,
            "get_industry_performance_summary_by_quarter",
            return_value=[],
        ) as by_quarter:
            result = fmp_client.institutional.get_industry_performance_summary(
                report_date=date(2024, 3, 31)
            )

        assert result == []
        by_quarter.assert_called_once_with(2024, 1)


class TestHolderPerformanceSummaryInertQuarterFilter:
    """`holder-performance-summary` accepts year/quarter and ignores them (#192).

    Probed against the live API while cutting 2.6.0, and re-probed before
    these tests were written: for ``cik=0001067983`` the endpoint returns a
    byte-identical 52-row payload spanning 2013-06-30 to 2026-03-31 with no
    filter, with ``year=2023&quarter=3``, and with ``year=2019&quarter=1``.

    That makes `get_holder_performance_summary_by_quarter` a method whose
    *name* promises something the API does not do — a silent wrong answer,
    and a more convincing one than the date-shaped form, which is why it
    warns. The five sibling ``*_by_quarter`` methods were probed the same way
    and do filter correctly; this is the only exception.

    These tests exist because the warning has been lost once already: it was
    added in #196, and #198 reworked the change without it.
    """

    def test_by_quarter_warns_that_the_quarter_is_ignored(self, fmp_client):
        with patch.object(fmp_client, "request", return_value=[]):
            with pytest.warns(UserWarning, match="ignores year/quarter"):
                fmp_client.institutional.get_holder_performance_summary_by_quarter(
                    "0001067983", 2023, 3
                )

    def test_report_date_warns_too(self, fmp_client):
        """The date-shaped route reaches the same dead filter."""
        with patch.object(fmp_client, "request", return_value=[]):
            with pytest.warns(UserWarning, match="ignores year/quarter"):
                fmp_client.institutional.get_holder_performance_summary(
                    "0001067983", report_date=date(2023, 9, 30)
                )

    def test_the_correct_usage_stays_silent(self, fmp_client):
        """Omitting the date is what the endpoint supports; it must not warn.

        A warning here would train users to filter the whole category out,
        taking the two real ones with it.
        """
        with patch.object(fmp_client, "request", return_value=[]):
            with warnings.catch_warnings():
                warnings.simplefilter("error", UserWarning)
                fmp_client.institutional.get_holder_performance_summary("0001067983")

    def test_warning_is_attributed_to_the_caller_not_the_library(self, fmp_client):
        """Both routes must blame the user's line, or the warning is unusable.

        This is why the two public methods do not delegate to each other: a
        delegating call would report `client.py` as the offender on the
        date-shaped route (the #177 failure mode).
        """
        for call in (
            lambda: fmp_client.institutional.get_holder_performance_summary_by_quarter(
                "0001067983", 2023, 3
            ),
            lambda: fmp_client.institutional.get_holder_performance_summary(
                "0001067983", report_date=date(2023, 9, 30)
            ),
        ):
            with patch.object(fmp_client, "request", return_value=[]):
                with pytest.warns(UserWarning) as record:
                    call()
            assert record[0].filename == __file__, (
                f"warning blamed {record[0].filename}, not the caller"
            )

    def test_fires_once_per_call_not_twice(self, fmp_client):
        """Delegation would double it; the shared request helper must not warn."""
        with patch.object(fmp_client, "request", return_value=[]):
            with pytest.warns(UserWarning) as record:
                fmp_client.institutional.get_holder_performance_summary(
                    "0001067983", report_date=date(2023, 9, 30)
                )
        inert = [r for r in record if "ignores year/quarter" in str(r.message)]
        assert len(inert) == 1, f"expected 1 warning, got {len(inert)}"

    def test_parameters_are_still_sent(self, fmp_client):
        """Kept in the request in case FMP starts honouring them."""
        with patch.object(fmp_client, "request", return_value=[]) as request:
            with pytest.warns(UserWarning):
                fmp_client.institutional.get_holder_performance_summary_by_quarter(
                    "0001067983", 2023, 3, page=1
                )
        assert request.call_args.kwargs == {
            "cik": "0001067983",
            "page": 1,
            "year": 2023,
            "quarter": 3,
        }


def test_holder_industry_breakdown_allows_null_title() -> None:
    """FMP sends industryTitle: null on some holder rows (live 2026-08-14)."""
    item = HolderIndustryBreakdown.model_validate(
        {
            "date": "2024-09-30",
            "cik": "0001067983",
            "investorName": "BERKSHIRE HATHAWAY INC",
            "industryTitle": None,
            "weight": 0.1,
        }
    )
    assert item.industry_title is None
