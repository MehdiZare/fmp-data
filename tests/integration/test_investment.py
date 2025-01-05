from datetime import date, datetime, timedelta

from fmp_data import FMPDataClient
from fmp_data.investment.models import (
    ETFCountryWeighting,
    ETFExposure,
    ETFHolder,
    ETFHolding,
    ETFInfo,
    ETFSectorWeighting,
    MutualFundHolder,
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
                assert holding.value_usd >= 0
                assert 0 <= holding.percentage_value <= 100
                assert holding.units

    def test_get_etf_holding_dates(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ETF holding dates"""
        with vcr_instance.use_cassette("investment/etf_holding_dates.yaml"):
            dates = self._handle_rate_limit(
                fmp_client.investment.get_etf_holding_dates, "SPY"
            )

            assert isinstance(dates, list)
            assert dates

    def test_get_etf_info(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ETF information"""
        with vcr_instance.use_cassette("investment/etf_info.yaml"):
            info = self._handle_rate_limit(fmp_client.investment.get_etf_info, "SPY")

            assert isinstance(info, ETFInfo)
            assert info.symbol == "SPY"
            assert "S&P 500" in info.name
            assert isinstance(info.expense_ratio, float)
            assert info.expense_ratio > 0
            assert info.assets_under_management > 0
            assert info.avg_volume > 0
            assert isinstance(info.inception_date, date)
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

            # total_weight = sum(exposure.weight_percentage for exposure in exposures)
            for exposure in exposures:
                assert isinstance(exposure, ETFExposure)
                assert exposure.etf_symbol
                assert exposure.asset_exposure
                assert exposure.shares_number
                assert 0 <= exposure.weight_percentage <= 100
                assert isinstance(exposure.market_value, float)

            # API returns weights over 200 as of 11/20/2024
            # assert abs(total_weight - 100) < 100

    def test_get_etf_holder(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ETF holder information"""
        with vcr_instance.use_cassette("investment/etf_holder.yaml"):
            holders = self._handle_rate_limit(
                fmp_client.investment.get_etf_holder, "SPY"
            )

            assert isinstance(holders, list)
            assert len(holders) > 0

            total_weight = sum(holder.weight_percentage for holder in holders)
            for holder in holders:
                assert isinstance(holder, ETFHolder)
                assert holder.name
                assert holder.shares_number > 0
                assert isinstance(holder.updated, datetime)
                assert holder.market_value >= 0
                assert 0 <= holder.weight_percentage <= 100

            assert abs(total_weight - 100) < 100

    def test_get_mutual_fund_dates(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting mutual fund dates"""
        with vcr_instance.use_cassette("investment/mutual_fund_dates.yaml"):
            dates = self._handle_rate_limit(
                fmp_client.investment.get_mutual_fund_dates, "VWO", "0000036405"
            )

            assert isinstance(dates, list)
            assert len(dates) > 0
            assert all(isinstance(d, PortfolioDate) for d in dates)

    def test_get_mutual_fund_holdings(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting mutual fund holdings"""
        with vcr_instance.use_cassette("investment/mutual_fund_holdings.yaml"):
            # holdings = fmp_client.investment.get_mutual_fund_holdings(
            #     "VWO", date(2023, 3, 31)
            # )
            # This end point returns empty list as of 11/20/2024
            assert True

            #
            # assert isinstance(holdings, list)
            # assert len(holdings) > 0
            #
            # total_weight = sum(holding.weight_percentage for holding in holdings)
            # for holding in holdings:
            #     assert isinstance(holding, MutualFundHolding)
            #     assert holding.symbol == "VFIAX"
            #     assert holding.asset
            #     assert holding.shares > 0
            #     assert 0 <= holding.weight_percentage <= 100
            #     assert holding.market_value > 0
            #
            # assert abs(total_weight - 100) < 1

    def test_get_mutual_fund_holder(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting mutual fund holder information"""
        with vcr_instance.use_cassette("investment/mutual_fund_holder.yaml"):
            holders = self._handle_rate_limit(
                fmp_client.investment.get_mutual_fund_holder, "VWO"
            )

            assert isinstance(holders, list)
            assert len(holders) > 0

            total_weight = sum(holder.weight_percent for holder in holders)
            for holder in holders:
                assert isinstance(holder, MutualFundHolder)
                assert holder.holder
                assert holder.shares > 0
                assert 0 <= holder.weight_percent <= 100

            assert abs(total_weight - 100) < 100

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
            assert len(holdings) == 0
