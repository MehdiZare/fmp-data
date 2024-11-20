import logging
from datetime import date, datetime

import pytest

from fmp_data import FMPDataClient
from fmp_data.institutional.models import (
    Form13F,
    InsiderRoster,
    InsiderStatistic,
    InsiderTrade,
    InstitutionalHolder,
    InstitutionalHolding,
)

logger = logging.getLogger(__name__)


class Test13FEndpoints:
    """Test Form 13F related endpoints"""

    def test_get_form_13f(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Form 13F filing data"""
        with vcr_instance.use_cassette("institutional/form_13f.yaml"):
            # Using Berkshire Hathaway's CIK as test data
            results = fmp_client.institutional.get_form_13f(
                "0001067983", datetime.fromisoformat("2023-09-30")
            )

            assert isinstance(results, list)
            assert len(results) > 0
            assert all(isinstance(h, Form13F) for h in results)

            # Verify sample holding data
            sample_holding = results[0]
            assert isinstance(sample_holding.filing_date, date)
            assert isinstance(sample_holding.shares, int)
            assert isinstance(sample_holding.value, float)
            assert isinstance(sample_holding.cusip, str)
            assert isinstance(sample_holding.company_name, str)
            assert sample_holding.cik == "0001067983"  # Verify CIK matches request

            # Verify reasonable value ranges
            assert sample_holding.shares > 0
            assert sample_holding.value > 0
            assert len(sample_holding.cusip) > 0


class TestInstitutionalOwnershipEndpoints:
    """Test institutional ownership endpoints"""

    def test_get_institutional_holders(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting list of institutional holders"""
        with vcr_instance.use_cassette("institutional/holders.yaml"):
            holders = fmp_client.institutional.get_institutional_holders()

            assert isinstance(holders, list)
            assert len(holders) > 0
            assert all(isinstance(h, InstitutionalHolder) for h in holders)

            # Verify required fields
            sample_holder = holders[0]
            assert isinstance(sample_holder.cik, str)
            assert isinstance(sample_holder.name, str)

    def test_get_institutional_holdings(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting institutional holdings by symbol"""
        with vcr_instance.use_cassette("institutional/holdings.yaml"):
            holdings = fmp_client.institutional.get_institutional_holdings(
                "AAPL", False
            )

            assert isinstance(holdings, list)
            assert len(holdings) > 0
            assert all(isinstance(h, InstitutionalHolding) for h in holdings)

            # Verify sample holding data
            sample_holding = holdings[0]
            assert sample_holding.symbol == "AAPL"
            assert isinstance(sample_holding.cik, str)
            assert isinstance(sample_holding.report_date, date)
            assert isinstance(sample_holding.total_invested, float)
            assert isinstance(sample_holding.ownership_percent, float)


class TestInsiderTradingEndpoints:
    """Test insider trading related endpoints"""

    def test_get_insider_trades(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting insider trades"""
        with vcr_instance.use_cassette("institutional/insider_trades.yaml"):
            trades = fmp_client.institutional.get_insider_trades("AAPL")

            assert isinstance(trades, list)
            assert len(trades) > 0
            assert all(isinstance(t, InsiderTrade) for t in trades)

            # Verify sample trade data
            sample_trade = trades[0]
            assert sample_trade.symbol == "AAPL"
            assert isinstance(sample_trade.filing_date, datetime)
            assert isinstance(sample_trade.transaction_date, date)
            assert isinstance(sample_trade.securities_transacted, float)
            assert isinstance(sample_trade.price, float)

    def test_get_insider_roster(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting insider roster"""
        with vcr_instance.use_cassette("institutional/insider_roster.yaml"):
            roster = fmp_client.institutional.get_insider_roster("AAPL")

            assert isinstance(roster, list)
            assert len(roster) > 0
            assert all(isinstance(r, InsiderRoster) for r in roster)

            # Verify roster entry structure
            sample_entry = roster[0]
            assert isinstance(sample_entry.owner, str)
            assert isinstance(sample_entry.transaction_date, date)
            assert isinstance(sample_entry.type_of_owner, str)

    def test_get_insider_statistics(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting insider trading statistics"""
        with vcr_instance.use_cassette("institutional/insider_statistics.yaml"):
            stats = fmp_client.institutional.get_insider_statistics("AAPL")

            # Verify statistics structure
            assert isinstance(stats, InsiderStatistic)
            assert stats.symbol == "AAPL"
            assert isinstance(stats.year, int)
            assert isinstance(stats.quarter, int)
            assert isinstance(stats.purchases, int)
            assert isinstance(stats.sales, int)
            assert isinstance(stats.buy_sell_ratio, float)
            assert isinstance(stats.total_bought, int)
            assert isinstance(stats.total_sold, int)

    @pytest.mark.parametrize(
        "test_symbol",
        [
            "AAPL",  # High volume stock
            "MSFT",  # Another high volume option
        ],
    )
    def test_insider_trades_multiple_symbols(
        self, fmp_client: FMPDataClient, vcr_instance, test_symbol
    ):
        """Test insider trades with different symbols"""
        with vcr_instance.use_cassette(
            f"institutional/insider_trades_{test_symbol}.yaml"
        ):
            trades = fmp_client.institutional.get_insider_trades(test_symbol)

            assert isinstance(trades, list)
            if len(trades) > 0:  # Some symbols might not have recent trades
                assert all(isinstance(t, InsiderTrade) for t in trades)
                assert all(t.symbol == test_symbol for t in trades)
                assert all(t.price >= 0 for t in trades)
