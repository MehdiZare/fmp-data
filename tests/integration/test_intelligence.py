from datetime import date, datetime, timedelta
from decimal import Decimal

from fmp_data import FMPDataClient
from fmp_data.intelligence.models import (
    AnalystEstimate,
    AnalystRecommendation,
    DividendEvent,
    EarningConfirmed,
    EarningEvent,
    EarningSurprise,
    IPOEvent,
    PriceTarget,
    PriceTargetConsensus,
    PriceTargetSummary,
    StockSplitEvent,
    UpgradeDowngrade,
    UpgradeDowngradeConsensus,
)


class TestIntelligenceEndpoints:
    """Test market intelligence endpoints"""

    def test_get_price_target(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting price targets"""
        with vcr_instance.use_cassette("intelligence/price_target.yaml"):
            targets = fmp_client.intelligence.get_price_target("AAPL")

            assert isinstance(targets, list)
            assert len(targets) > 0

            for target in targets:
                assert isinstance(target, PriceTarget)
                assert isinstance(target.published_date, datetime)
                assert isinstance(target.price_target, float)
                assert target.symbol == "AAPL"
                assert isinstance(target.adj_price_target, float)
                assert isinstance(target.price_when_posted, float)

    def test_get_price_target_summary(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting price target summary"""
        with vcr_instance.use_cassette("intelligence/price_target_summary.yaml"):
            summary = fmp_client.intelligence.get_price_target_summary("AAPL")

            assert isinstance(summary, PriceTargetSummary)
            assert summary.symbol == "AAPL"
            assert isinstance(summary.last_month, int)
            assert isinstance(summary.last_month_avg_price_target, float)
            assert isinstance(summary.last_quarter_avg_price_target, float)
            assert isinstance(summary.last_year, int)
            assert isinstance(summary.all_time_avg_price_target, float)

    def test_get_price_target_consensus(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting price target consensus"""
        with vcr_instance.use_cassette("intelligence/price_target_consensus.yaml"):
            consensus = fmp_client.intelligence.get_price_target_consensus("AAPL")

            assert isinstance(consensus, PriceTargetConsensus)
            assert consensus.symbol == "AAPL"
            assert isinstance(consensus.target_consensus, float)
            assert isinstance(consensus.target_high, float)
            assert isinstance(consensus.target_low, float)

    def test_get_analyst_estimates(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting analyst estimates"""
        with vcr_instance.use_cassette("intelligence/analyst_estimates.yaml"):
            estimates = fmp_client.intelligence.get_analyst_estimates("AAPL")

            assert isinstance(estimates, list)
            assert len(estimates) > 0

            for estimate in estimates:
                assert isinstance(estimate, AnalystEstimate)
                assert isinstance(estimate.date, datetime)
                assert isinstance(estimate.estimated_revenue_high, float)
                assert estimate.symbol == "AAPL"
                assert isinstance(estimate.estimated_ebitda_avg, float)
                assert isinstance(estimate.number_analyst_estimated_revenue, int)

    def test_get_analyst_recommendations(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting analyst recommendations"""
        with vcr_instance.use_cassette("intelligence/analyst_recommendations.yaml"):
            recommendations = fmp_client.intelligence.get_analyst_recommendations(
                "AAPL"
            )

            assert isinstance(recommendations, list)
            assert len(recommendations) > 0

            for rec in recommendations:
                assert isinstance(rec, AnalystRecommendation)
                assert isinstance(rec.date, datetime)
                assert rec.symbol == "AAPL"
                assert isinstance(rec.analyst_ratings_buy, int)
                assert isinstance(rec.analyst_ratings_strong_sell, int)

    def test_get_upgrades_downgrades(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting upgrades and downgrades"""
        with vcr_instance.use_cassette("intelligence/upgrades_downgrades.yaml"):
            changes = fmp_client.intelligence.get_upgrades_downgrades("AAPL")

            assert isinstance(changes, list)
            assert len(changes) > 0

            for change in changes:
                assert isinstance(change, UpgradeDowngrade)
                assert isinstance(change.published_date, datetime)
                assert change.symbol == "AAPL"
                assert isinstance(change.action, str)
                assert (
                    isinstance(change.previous_grade, str)
                    if change.previous_grade is not None
                    else True
                )
                assert isinstance(change.new_grade, str)

    def test_get_upgrades_downgrades_consensus(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting upgrades/downgrades consensus"""
        with vcr_instance.use_cassette(
            "intelligence/upgrades_downgrades_consensus.yaml"
        ):
            consensus = fmp_client.intelligence.get_upgrades_downgrades_consensus(
                "AAPL"
            )

            assert isinstance(consensus, UpgradeDowngradeConsensus)
            assert consensus.symbol == "AAPL"
            assert isinstance(consensus.strong_buy, int)
            assert isinstance(consensus.buy, int)
            assert isinstance(consensus.hold, int)
            assert isinstance(consensus.sell, int)
            assert isinstance(consensus.strong_sell, int)

    def test_get_earnings_calendar(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting earnings calendar"""
        with vcr_instance.use_cassette("intelligence/earnings_calendar.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = fmp_client.intelligence.get_earnings_calendar(
                start_date=start_date, end_date=end_date
            )

            assert isinstance(events, list)
            assert len(events) > 0

            for event in events:
                assert isinstance(event, EarningEvent)
                assert isinstance(event.event_date, date)
                assert isinstance(event.symbol, str)
                assert isinstance(event.fiscal_date_ending, date)
                assert isinstance(event.updated_from_date, date)
                if event.eps_estimated is not None:
                    assert isinstance(event.eps_estimated, float)

    def test_get_earnings_confirmed(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting confirmed earnings"""
        with vcr_instance.use_cassette("intelligence/earnings_confirmed.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = fmp_client.intelligence.get_earnings_confirmed(
                start_date=start_date, end_date=end_date
            )

            assert isinstance(events, list)
            if len(events) > 0:
                for event in events:
                    assert isinstance(event, EarningConfirmed)
                    assert isinstance(event.time, str)
                    if event.event_date is not None:
                        assert isinstance(event.event_date, datetime)

    def test_get_historical_earnings(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical earnings"""
        with vcr_instance.use_cassette("intelligence/historical_earnings.yaml"):
            events = fmp_client.intelligence.get_historical_earnings("AAPL")

            assert isinstance(events, list)
            assert len(events) > 0

            for event in events:
                assert isinstance(event, EarningEvent)
                assert event.symbol == "AAPL"
                assert isinstance(event.event_date, date)
                assert isinstance(event.time, str)

    def test_get_earnings_surprises(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting earnings surprises"""
        with vcr_instance.use_cassette("intelligence/earnings_surprises.yaml"):
            surprises = fmp_client.intelligence.get_earnings_surprises("AAPL")

            assert isinstance(surprises, list)
            assert len(surprises) > 0

            for surprise in surprises:
                assert isinstance(surprise, EarningSurprise)
                assert surprise.symbol == "AAPL"
                assert isinstance(surprise.surprise_date, date)
                assert isinstance(surprise.actual_earning_result, float)
                assert isinstance(surprise.estimated_earning, float)

    def test_get_dividends_calendar(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting dividends calendar"""
        with vcr_instance.use_cassette("intelligence/dividends_calendar.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = fmp_client.intelligence.get_dividends_calendar(
                start_date=start_date, end_date=end_date
            )

            assert isinstance(events, list)
            assert len(events) > 0

            for event in events:
                assert isinstance(event, DividendEvent)
                assert isinstance(event.symbol, str)
                assert isinstance(event.dividend, float)
                assert (
                    isinstance(event.record_date, date) if event.record_date else True
                )
                assert (
                    isinstance(event.payment_date, date) if event.payment_date else True
                )
                assert isinstance(event.ex_dividend_date, date)

    def test_get_stock_splits_calendar(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting stock splits calendar"""
        with vcr_instance.use_cassette("intelligence/stock_splits_calendar.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = fmp_client.intelligence.get_stock_splits_calendar(
                start_date=start_date, end_date=end_date
            )

            assert isinstance(events, list)
            if len(events) > 0:
                for event in events:
                    assert isinstance(event, StockSplitEvent)
                    assert isinstance(event.symbol, str)
                    assert isinstance(event.split_event_date, date)
                    assert isinstance(event.label, str)
                    assert isinstance(event.numerator, int)
                    assert isinstance(event.denominator, int)

    def test_get_ipo_calendar(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting IPO calendar"""
        with vcr_instance.use_cassette("intelligence/ipo_calendar.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = fmp_client.intelligence.get_ipo_calendar(
                start_date=start_date, end_date=end_date
            )

            assert isinstance(events, list)
            if len(events) > 0:
                for event in events:
                    assert isinstance(event, IPOEvent)
                    assert isinstance(event.symbol, str)
                    assert isinstance(event.company, str)
                    assert isinstance(event.ipo_event_date, date)
                    assert isinstance(event.exchange, str)
                    if event.shares is not None:
                        assert isinstance(event.shares, int)
                    if event.market_cap is not None:
                        assert isinstance(event.market_cap, Decimal)
