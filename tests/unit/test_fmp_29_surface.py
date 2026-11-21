"""Provider fields and TipRanks query shape added in 2.9.0."""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import pytest

from fmp_data.exceptions import ValidationError
from fmp_data.index.models import HistoricalIndexConstituent
from fmp_data.intelligence.client import MarketIntelligenceClient
from fmp_data.intelligence.endpoints import TIPRANKS_SEARCH
from fmp_data.intelligence.models import ESGBenchmark, IPOEvent, TipRanksRating


def test_historical_constituent_accepts_change_type() -> None:
    row = HistoricalIndexConstituent.model_validate(
        {
            "date": "2026-10-06",
            "symbol": "AAPL",
            "changeType": "addition",
            "addedTicker": "AAPL",
        }
    )
    assert row.change_type == "addition"
    assert row.added_ticker == "AAPL"


def test_ipo_event_accepts_deal_size_and_null_market_cap() -> None:
    row = IPOEvent.model_validate(
        {
            "symbol": "NEW",
            "company": "New Co",
            "date": "2026-10-05",
            "exchange": "NYSE",
            "actions": "Expected",
            "shares": None,
            "priceRange": None,
            "dealSize": "150000000",
            "marketCap": None,
        }
    )
    assert row.deal_size == Decimal("150000000")
    assert row.market_cap is None


def test_esg_benchmark_accepts_period() -> None:
    row = ESGBenchmark.model_validate({"sector": "Technology", "period": "FY"})
    assert row.period == "FY"


def test_tipranks_rating_keeps_nullable_price_target() -> None:
    row = TipRanksRating.model_validate(
        {
            "symbol": "AAPL",
            "firmName": "Morgan Stanley",
            "expertUID": "abc",
            "priceTarget": None,
            "priceTargetCurrency": None,
        }
    )
    assert row.firm_name == "Morgan Stanley"
    assert row.price_target is None


def _client() -> tuple[MarketIntelligenceClient, Mock]:
    transport = Mock()
    transport.request.return_value = []
    client = MarketIntelligenceClient.__new__(MarketIntelligenceClient)
    client._client = transport
    return client, transport


def test_tipranks_search_omits_unset_filters_and_sends_firm_name() -> None:
    client, transport = _client()
    client.search_tipranks_ratings(
        "AAPL",
        firm_name="Morgan Stanley",
        nonadjusted=False,
        start_date=date(2026, 1, 1),
    )

    endpoint = transport.request.call_args.args[0]
    kwargs = transport.request.call_args.kwargs
    assert endpoint is TIPRANKS_SEARCH
    assert kwargs == {
        "symbol": "AAPL",
        "firm_name": "Morgan Stanley",
        "nonadjusted": False,
        "start_date": "2026-01-01",
    }


def test_tipranks_search_omits_firm_name_when_unset() -> None:
    client, transport = _client()
    client.search_tipranks_ratings()
    assert transport.request.call_args.kwargs == {}


def test_tipranks_pit_analyst_requires_an_identity() -> None:
    client, transport = _client()
    with pytest.raises(ValidationError, match="expert_uid or analyst_name"):
        client.get_tipranks_pit_by_analyst()
    transport.request.assert_not_called()
