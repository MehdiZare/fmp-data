from datetime import date, datetime
import logging

import pytest

from fmp_data import FMPDataClient
from fmp_data.institutional.models import (
    AssetAllocation,
    BeneficialOwnership,
    CIKMapping,
    FailToDeliver,
    Form13F,
    Form13FDate,
    HolderIndustryBreakdown,
    HolderPerformanceSummary,
    IndustryPerformanceSummary,
    InsiderRoster,
    InsiderStatistic,
    InsiderTrade,
    InsiderTradingByName,
    InsiderTradingLatest,
    InsiderTradingSearch,
    InsiderTradingStatistics,
    InsiderTransactionType,
    InstitutionalHolder,
    InstitutionalHolding,
    InstitutionalOwnershipAnalytics,
    InstitutionalOwnershipDates,
    InstitutionalOwnershipExtract,
    InstitutionalOwnershipLatest,
    SymbolPositionsSummary,
)

from .base import BaseTestCase

logger = logging.getLogger(__name__)


class Test13FEndpoints(BaseTestCase):
    """Test Form 13F related endpoints"""

    def test_get_form_13f(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Form 13F filing data"""
        with vcr_instance.use_cassette("institutional/form_13f.yaml"):
            # Using Berkshire Hathaway's CIK as test data
            results = self._handle_rate_limit(
                fmp_client.institutional.get_form_13f,
                "0001067983",
                datetime.fromisoformat("2023-09-30"),
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


class TestInstitutionalOwnershipEndpoints(BaseTestCase):
    """Test institutional ownership endpoints"""

    REPORT_DATE = date(2023, 9, 30)

    def test_get_institutional_holders(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting list of institutional holders"""
        with vcr_instance.use_cassette("institutional/holders.yaml"):
            holders = self._handle_rate_limit(
                fmp_client.institutional.get_institutional_holders
            )

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
            holdings = self._handle_rate_limit(
                fmp_client.institutional.get_institutional_holdings,
                "AAPL",
                self.REPORT_DATE,
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


class TestInsiderTradingEndpoints(BaseTestCase):
    """Test insider trading related endpoints"""

    def test_get_insider_trades(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting insider trades"""
        with vcr_instance.use_cassette("institutional/insider_trades.yaml"):
            trades = self._handle_rate_limit(
                fmp_client.institutional.get_insider_trades,
                "AAPL",
            )

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
            roster = self._handle_rate_limit(
                fmp_client.institutional.get_insider_roster,
                "AAPL",
            )

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
            stats = self._handle_rate_limit(
                fmp_client.institutional.get_insider_statistics,
                "AAPL",
            )

            # Verify statistics structure
            assert isinstance(stats, InsiderStatistic)
            assert stats.symbol == "AAPL"
            assert isinstance(stats.year, int)
            assert isinstance(stats.quarter, int)
            assert isinstance(stats.acquired_transactions, int)
            assert isinstance(stats.disposed_transactions, int)
            assert isinstance(stats.acquired_disposed_ratio, float)
            assert isinstance(stats.total_acquired, int)
            assert isinstance(stats.total_disposed, int)

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
            trades = self._handle_rate_limit(
                fmp_client.institutional.get_insider_trades,
                test_symbol,
            )

            assert isinstance(trades, list)
            if len(trades) > 0:  # Some symbols might not have recent trades
                assert all(isinstance(t, InsiderTrade) for t in trades)
                assert all(t.symbol == test_symbol for t in trades)
                assert all(t.price >= 0 for t in trades)


# Add these test classes to test_institutional.py


class TestCIKMappingEndpoints(BaseTestCase):
    """Test CIK mapping related endpoints"""

    def test_get_cik_mappings(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting CIK mappings"""
        with vcr_instance.use_cassette("institutional/cik_mappings.yaml"):
            mappings = self._handle_rate_limit(
                fmp_client.institutional.get_cik_mappings,
                page=0,
            )

            assert isinstance(mappings, list)
            assert len(mappings) > 0
            assert all(isinstance(m, CIKMapping) for m in mappings)

            # Verify sample mapping data
            sample_mapping = mappings[0]
            assert isinstance(sample_mapping.reporting_cik, str)
            assert isinstance(sample_mapping.reporting_name, str)
            assert len(sample_mapping.reporting_cik) == 10  # CIK numbers are 10 digits

    def test_search_cik_by_name(self, fmp_client: FMPDataClient, vcr_instance):
        """Test searching CIK mappings by name"""
        with vcr_instance.use_cassette("institutional/cik_search_name.yaml"):
            # Using "Berkshire" as test search term
            mappings = self._handle_rate_limit(
                fmp_client.institutional.search_cik_by_name,
                "Berkshire",
                page=0,
            )

            assert isinstance(mappings, list)
            assert len(mappings) > 0
            assert all(isinstance(m, CIKMapping) for m in mappings)

            # Verify search results contain term
            sample_mapping = mappings[0]
            assert "BERKSHIRE" in sample_mapping.reporting_name.upper()


class TestBeneficialOwnershipEndpoints(BaseTestCase):
    """Test beneficial ownership endpoints"""

    def test_get_beneficial_ownership(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting beneficial ownership data"""
        with vcr_instance.use_cassette("institutional/beneficial_ownership.yaml"):
            ownership = self._handle_rate_limit(
                fmp_client.institutional.get_beneficial_ownership,
                "AAPL",
            )

            assert isinstance(ownership, list)
            if len(ownership) > 0:  # Not all symbols have beneficial ownership data
                assert all(isinstance(o, BeneficialOwnership) for o in ownership)

                # Verify sample ownership data
                sample_ownership = ownership[0]
                assert sample_ownership.symbol == "AAPL"
                assert isinstance(sample_ownership.filing_date, datetime)
                assert isinstance(sample_ownership.accepted_date, datetime)
                assert isinstance(sample_ownership.citizenship_place_org, str)
                assert isinstance(sample_ownership.type_of_reporting_person, str)
                assert isinstance(sample_ownership.shared_voting_power, float)
                assert isinstance(sample_ownership.url, str)

    @pytest.mark.parametrize(
        "test_symbol",
        [
            "AAPL",  # High volume stock
            "MSFT",  # Another high volume option
        ],
    )
    def test_beneficial_ownership_multiple_symbols(
        self, fmp_client: FMPDataClient, vcr_instance, test_symbol
    ):
        """Test beneficial ownership with different symbols"""
        with vcr_instance.use_cassette(
            f"institutional/beneficial_ownership_{test_symbol}.yaml"
        ):
            ownership = self._handle_rate_limit(
                fmp_client.institutional.get_beneficial_ownership,
                test_symbol,
            )

            assert isinstance(ownership, list)
            if len(ownership) > 0:
                assert all(isinstance(o, BeneficialOwnership) for o in ownership)
                assert all(o.symbol == test_symbol for o in ownership)
                assert all(o.amount_beneficially_owned >= 0 for o in ownership)


class TestFailToDeliverEndpoints(BaseTestCase):
    """Test fail to deliver endpoints"""

    def test_get_fail_to_deliver(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting fail to deliver data"""
        with vcr_instance.use_cassette("institutional/fail_to_deliver.yaml"):
            ftd_data = self._handle_rate_limit(
                fmp_client.institutional.get_fail_to_deliver,
                "AAPL",
                page=0,
            )

            assert isinstance(ftd_data, list)
            if len(ftd_data) > 0:  # Not all symbols have FTD data
                assert all(isinstance(f, FailToDeliver) for f in ftd_data)

                # Verify sample FTD data
                sample_ftd = ftd_data[0]
                assert sample_ftd.symbol == "AAPL"
                assert isinstance(sample_ftd.fail_date, date)
                assert isinstance(sample_ftd.quantity, int)
                assert isinstance(sample_ftd.price, float)
                assert isinstance(sample_ftd.name, str)

                # Verify reasonable value ranges
                assert sample_ftd.quantity >= 0
                assert sample_ftd.price > 0

    @pytest.mark.parametrize(
        "test_symbol",
        [
            "AAPL",  # High volume stock
            "MSFT",  # Another high volume option
        ],
    )
    def test_fail_to_deliver_multiple_symbols(
        self, fmp_client: FMPDataClient, vcr_instance, test_symbol
    ):
        """Test fail to deliver with different symbols"""
        with vcr_instance.use_cassette(
            f"institutional/fail_to_deliver_{test_symbol}.yaml"
        ):
            ftd_data = self._handle_rate_limit(
                fmp_client.institutional.get_fail_to_deliver,
                test_symbol,
                page=0,
            )

            assert isinstance(ftd_data, list)
            if len(ftd_data) > 0:
                assert all(isinstance(f, FailToDeliver) for f in ftd_data)
                assert all(f.symbol == test_symbol for f in ftd_data)
                assert all(f.quantity >= 0 for f in ftd_data)
                assert all(f.price > 0 for f in ftd_data)


class TestInstitutionalAdditionalEndpoints(BaseTestCase):
    """Test additional institutional endpoints"""

    CIK = "0001067983"
    REPORT_DATE = date(2023, 9, 30)

    def test_get_form_13f_dates(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting Form 13F filing dates"""
        with vcr_instance.use_cassette("institutional/form_13f_dates.yaml"):
            results = self._handle_rate_limit(
                fmp_client.institutional.get_form_13f_dates, self.CIK
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], Form13FDate)

    def test_get_asset_allocation(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting asset allocation data"""
        with vcr_instance.use_cassette("institutional/asset_allocation.yaml"):
            results = self._handle_rate_limit(
                fmp_client.institutional.get_asset_allocation, self.REPORT_DATE
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], AssetAllocation)

    def test_get_transaction_types(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting insider transaction types"""
        with vcr_instance.use_cassette("institutional/transaction_types.yaml"):
            results = self._handle_rate_limit(
                fmp_client.institutional.get_transaction_types
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], InsiderTransactionType)

    def test_get_insider_trading_latest(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting latest insider trading activity"""
        with vcr_instance.use_cassette("institutional/insider_trading_latest.yaml"):
            results = self._handle_rate_limit(
                fmp_client.institutional.get_insider_trading_latest, page=0, limit=5
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], InsiderTradingLatest)

    def test_search_insider_trading(self, fmp_client: FMPDataClient, vcr_instance):
        """Test searching insider trading"""
        with vcr_instance.use_cassette("institutional/insider_trading_search.yaml"):
            results = self._handle_rate_limit(
                fmp_client.institutional.search_insider_trading,
                symbol="AAPL",
                page=0,
                limit=5,
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], InsiderTradingSearch)

    def test_get_insider_trading_by_name(self, fmp_client: FMPDataClient, vcr_instance):
        """Test searching insider trading by name"""
        with vcr_instance.use_cassette("institutional/insider_trading_by_name.yaml"):
            results = self._handle_rate_limit(
                fmp_client.institutional.get_insider_trading_by_name,
                reporting_name="COOK",
                page=0,
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], InsiderTradingByName)
                assert results[0].reporting_cik
                assert results[0].reporting_name

    def test_get_insider_trading_statistics_enhanced(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting enhanced insider trading statistics"""
        with vcr_instance.use_cassette(
            "institutional/insider_trading_statistics_enhanced.yaml"
        ):
            stats = self._handle_rate_limit(
                fmp_client.institutional.get_insider_trading_statistics_enhanced,
                "AAPL",
            )
            assert isinstance(stats, InsiderTradingStatistics)

    def test_get_institutional_ownership_latest(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting latest institutional ownership filings"""
        with vcr_instance.use_cassette("institutional/ownership_latest.yaml"):
            results = self._handle_rate_limit(
                fmp_client.institutional.get_institutional_ownership_latest,
                cik=self.CIK,
                page=0,
                limit=100,
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], InstitutionalOwnershipLatest)

    def test_get_institutional_ownership_extract(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting institutional ownership extract"""
        with vcr_instance.use_cassette("institutional/ownership_extract.yaml"):
            results = self._handle_rate_limit(
                fmp_client.institutional.get_institutional_ownership_extract,
                self.CIK,
                self.REPORT_DATE,
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], InstitutionalOwnershipExtract)

    def test_get_institutional_ownership_dates(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting institutional ownership dates"""
        with vcr_instance.use_cassette("institutional/ownership_dates.yaml"):
            results = self._handle_rate_limit(
                fmp_client.institutional.get_institutional_ownership_dates, self.CIK
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], InstitutionalOwnershipDates)
                assert isinstance(results[0].report_date, date)
                assert isinstance(results[0].year, int)
                assert isinstance(results[0].quarter, int)

    def test_get_institutional_ownership_analytics(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting institutional ownership analytics"""
        with vcr_instance.use_cassette("institutional/ownership_analytics.yaml"):
            results = self._handle_rate_limit(
                fmp_client.institutional.get_institutional_ownership_analytics,
                "AAPL",
                self.REPORT_DATE,
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], InstitutionalOwnershipAnalytics)

    def test_get_holder_performance_summary(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting holder performance summary"""
        with vcr_instance.use_cassette("institutional/holder_performance_summary.yaml"):
            results = self._handle_rate_limit(
                fmp_client.institutional.get_holder_performance_summary,
                self.CIK,
                self.REPORT_DATE,
                page=0,
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], HolderPerformanceSummary)

    def test_get_holder_industry_breakdown(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting holder industry breakdown"""
        with vcr_instance.use_cassette("institutional/holder_industry_breakdown.yaml"):
            results = self._handle_rate_limit(
                fmp_client.institutional.get_holder_industry_breakdown,
                self.CIK,
                self.REPORT_DATE,
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], HolderIndustryBreakdown)

    def test_get_symbol_positions_summary(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting symbol positions summary"""
        with vcr_instance.use_cassette("institutional/symbol_positions_summary.yaml"):
            results = self._handle_rate_limit(
                fmp_client.institutional.get_symbol_positions_summary,
                "AAPL",
                self.REPORT_DATE,
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], SymbolPositionsSummary)

    def test_get_industry_performance_summary(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting industry performance summary"""
        with vcr_instance.use_cassette(
            "institutional/industry_performance_summary.yaml"
        ):
            results = self._handle_rate_limit(
                fmp_client.institutional.get_industry_performance_summary,
                self.REPORT_DATE,
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], IndustryPerformanceSummary)
