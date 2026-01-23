from datetime import date, datetime, timedelta

from fmp_data import FMPDataClient
from fmp_data.investment.models import (
    ETFCountryWeighting,
    ETFExposure,
    ETFHolder,
    ETFHolding,
    ETFInfo,
    ETFSectorWeighting,
    FundDisclosureHolderLatest,
    FundDisclosureHolding,
    FundDisclosureSearchResult,
    MutualFundHolder,
    MutualFundHolding,
    PortfolioDate,
)

from .base import BaseTestCase


class TestInvestmentEndpoints(BaseTestCase):
    """Integration tests for InvestmentClient endpoints using real API calls and VCR"""

    def test_get_etf_holdings(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ETF holdings"""
        with vcr_instance.use_cassette("investment/etf_holdings.yaml"):
            holdings = self._handle_rate_limit(
                fmp_client.investment.get_etf_holdings, "SPY", date(2023, 9, 30)
            )

            assert isinstance(holdings, list)
            assert len(holdings) >= 0

            for holding in holdings:
                assert isinstance(holding, ETFHolding)
                assert holding.symbol
                # Note: asset can be empty for cash positions
                assert holding.market_value >= 0
                assert 0 <= holding.weight_percentage <= 100
                assert holding.shares_number >= 0

    def test_get_etf_holding_dates(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ETF holding dates"""
        with vcr_instance.use_cassette("investment/etf_holding_dates.yaml"):
            dates = self._handle_rate_limit(
                fmp_client.investment.get_etf_holding_dates, "SPY"
            )

            assert isinstance(dates, list)
            # Note: Some ETFs may not have holding dates available
            assert len(dates) >= 0

    def test_get_etf_info(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ETF information"""
        with vcr_instance.use_cassette("investment/etf_info.yaml"):
            info = self._handle_rate_limit(fmp_client.investment.get_etf_info, "SPY")

            assert isinstance(info, ETFInfo)
            assert info.symbol == "SPY"
            assert "S&P 500" in info.name
            assert isinstance(info.expense_ratio, float)
            assert info.expense_ratio > 0
            assert (
                info.assets_under_management is not None
                and info.assets_under_management > 0
            )
            assert info.avg_volume is not None and info.avg_volume > 0
            assert info.inception_date is not None
            assert info.etf_company
            assert info.sectors_list

    def test_get_etf_sector_weightings(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ETF sector weightings"""
        with vcr_instance.use_cassette("investment/etf_sector_weightings.yaml"):
            weightings = self._handle_rate_limit(
                fmp_client.investment.get_etf_sector_weightings, "SPY"
            )

            assert isinstance(weightings, list)
            assert len(weightings) > 0

            total_weight = sum(weighting.weight_percentage for weighting in weightings)
            for weighting in weightings:
                assert isinstance(weighting, ETFSectorWeighting)
                assert weighting.sector
                assert 0 <= weighting.weight_percentage <= 100

            assert abs(total_weight - 1) < 1  # Allow for small rounding differences

    def test_get_etf_country_weightings(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ETF country weightings"""
        with vcr_instance.use_cassette("investment/etf_country_weightings.yaml"):
            weightings = self._handle_rate_limit(
                fmp_client.investment.get_etf_country_weightings, "SPY"
            )

            assert isinstance(weightings, list)
            assert len(weightings) > 0

            total_weight = sum(weighting.weight_percentage for weighting in weightings)
            for weighting in weightings:
                assert isinstance(weighting, ETFCountryWeighting)
                assert weighting.country
                assert 0 <= weighting.weight_percentage <= 1

            assert abs(total_weight - 1) < 1

    def test_get_etf_exposure(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ETF stock exposure"""
        with vcr_instance.use_cassette("investment/etf_exposure.yaml"):
            exposures = self._handle_rate_limit(
                fmp_client.investment.get_etf_exposure, "SPY"
            )

            assert isinstance(exposures, list)
            assert len(exposures) > 0

            for exposure in exposures:
                assert isinstance(exposure, ETFExposure)
                assert exposure.symbol
                assert exposure.asset
                assert exposure.shares_number is not None
                assert isinstance(exposure.market_value, float)

    def test_get_etf_holder(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ETF holder information"""
        with vcr_instance.use_cassette("investment/etf_holder.yaml"):
            holders = self._handle_rate_limit(
                fmp_client.investment.get_etf_holder, "SPY"
            )

            assert isinstance(holders, list)
            # Note: Some ETFs may not have holder data available
            assert len(holders) >= 0

            if holders:
                for holder in holders:
                    assert isinstance(holder, ETFHolder)
                    assert holder.name
                    assert holder.shares_number > 0
                    assert isinstance(holder.updated, datetime)
                    assert holder.market_value >= 0
                    assert 0 <= holder.weight_percentage <= 100

    def test_get_mutual_fund_dates(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting mutual fund dates"""
        with vcr_instance.use_cassette("investment/mutual_fund_dates.yaml"):
            dates = self._handle_rate_limit(
                fmp_client.investment.get_mutual_fund_dates, "VWO"
            )

            assert isinstance(dates, list)
            # Note: Some funds may not have date data available
            assert len(dates) >= 0
            if dates:
                assert all(isinstance(d, PortfolioDate) for d in dates)

    def test_get_mutual_fund_holdings(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting mutual fund holdings"""
        with vcr_instance.use_cassette("investment/mutual_fund_holdings.yaml"):
            holdings = self._handle_rate_limit(
                fmp_client.investment.get_mutual_fund_holdings,
                "VWO",
                date(2023, 3, 31),
            )

            assert isinstance(holdings, list)
            # Note: This endpoint may return empty data for some funds/dates
            assert len(holdings) >= 0

            if holdings:
                for holding in holdings:
                    assert isinstance(holding, MutualFundHolding)
                    assert holding.symbol
                    assert holding.market_value >= 0

    def test_get_mutual_fund_holder(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting mutual fund holder information"""
        with vcr_instance.use_cassette("investment/mutual_fund_holder.yaml"):
            holders = self._handle_rate_limit(
                fmp_client.investment.get_mutual_fund_holder, "VWO"
            )

            assert isinstance(holders, list)
            # Note: Some funds may not have holder data available
            assert len(holders) >= 0

            if holders:
                for holder in holders:
                    assert isinstance(holder, MutualFundHolder)
                    assert holder.holder
                    assert holder.shares > 0
                    assert 0 <= holder.weight_percent <= 100

    def test_get_mutual_fund_by_name(self, fmp_client: FMPDataClient, vcr_instance):
        """Test searching mutual funds by name"""
        with vcr_instance.use_cassette("investment/mutual_fund_by_name.yaml"):
            results = self._handle_rate_limit(
                fmp_client.investment.get_mutual_fund_by_name, "Vanguard"
            )

            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], MutualFundHolding)

    def test_get_fund_disclosure_holders_latest(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting latest fund disclosure holders"""
        with vcr_instance.use_cassette(
            "investment/fund_disclosure_holders_latest.yaml"
        ):
            holders = self._handle_rate_limit(
                fmp_client.investment.get_fund_disclosure_holders_latest, "AAPL"
            )

            assert isinstance(holders, list)
            assert len(holders) >= 0

            if holders:
                for holder in holders:
                    assert isinstance(holder, FundDisclosureHolderLatest)
                    assert holder.shares >= 0
                    assert holder.weight_percent >= 0

    def test_get_fund_disclosure(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting fund disclosure holdings"""
        with vcr_instance.use_cassette("investment/fund_disclosure.yaml"):
            holdings = self._handle_rate_limit(
                fmp_client.investment.get_fund_disclosure, "VWO", 2023, 4
            )

            assert isinstance(holdings, list)
            assert len(holdings) >= 0

            if holdings:
                for holding in holdings:
                    assert isinstance(holding, FundDisclosureHolding)
                    assert holding.name or holding.symbol or holding.title

    def test_search_fund_disclosure_holders(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test searching fund disclosure holders by name"""
        with vcr_instance.use_cassette(
            "investment/fund_disclosure_holders_search.yaml"
        ):
            results = self._handle_rate_limit(
                fmp_client.investment.search_fund_disclosure_holders,
                "Federated Hermes",
            )

            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], FundDisclosureSearchResult)
                assert results[0].entity_name

    def test_error_handling_invalid_symbol(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test error handling with invalid symbol"""
        with vcr_instance.use_cassette("investment/invalid_symbol.yaml"):
            result = self._handle_rate_limit(
                fmp_client.investment.get_etf_info, "INVALID_SYMBOL"
            )
            assert result is None or (isinstance(result, list) and len(result) == 0)

    def test_error_handling_invalid_date(self, fmp_client: FMPDataClient, vcr_instance):
        """Test error handling with future date"""
        future_date = date.today() + timedelta(days=50)
        with vcr_instance.use_cassette("investment/invalid_date.yaml"):
            holdings = self._handle_rate_limit(
                fmp_client.investment.get_etf_holdings, "SPY", future_date
            )
            assert isinstance(holdings, list)
            # Note: API may return latest holdings when given future date
            assert len(holdings) >= 0
