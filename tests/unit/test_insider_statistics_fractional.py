"""Regression coverage for provider fractional share totals (#395)."""

from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
from pydantic import ValidationError
import pytest

from fmp_data import AsyncFMPDataClient, FMPDataClient
from fmp_data.base import BaseClient
from fmp_data.config import ClientConfig
from fmp_data.institutional.endpoints import (
    INSIDER_STATISTICS,
    INSIDER_TRADING_STATISTICS_ENHANCED,
)
from fmp_data.institutional.models import InsiderStatistic, InsiderTradingStatistics
from fmp_data.models import Endpoint

# Public-field-only historical rows captured in #395; no credentials or URLs.
DISPOSED_ROW: dict[str, Any] = {
    "symbol": "NVDA",
    "cik": "0001045810",
    "year": 2020,
    "quarter": 2,
    "acquiredTransactions": 17,
    "disposedTransactions": 105,
    "acquiredDisposedRatio": 0.1619,
    "totalAcquired": 11350,
    "totalDisposed": 309729.1943,
    "averageAcquired": 667.6471,
    "averageDisposed": 2949.8019,
    "totalPurchases": 5,
    "totalSales": 99,
}
ACQUIRED_ROW: dict[str, Any] = {
    "symbol": "NVDA",
    "cik": "0001045810",
    "year": 2015,
    "quarter": 4,
    "acquiredTransactions": 5,
    "disposedTransactions": 14,
    "acquiredDisposedRatio": 0.3571,
    "totalAcquired": 165816.9858,
    "totalDisposed": 943835,
    "averageAcquired": 33163.3972,
    "averageDisposed": 67416.7857,
    "totalPurchases": 1,
    "totalSales": 9,
}
WHOLE_ROW = DISPOSED_ROW | {"year": 2026, "totalDisposed": 943835}
MODELS = (InsiderStatistic, InsiderTradingStatistics)
METHODS = (
    ("get_insider_statistics", InsiderStatistic),
    ("get_insider_trading_statistics_enhanced", InsiderTradingStatistics),
)


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize(
    "row,acquired,disposed",
    [
        (DISPOSED_ROW, 11350.0, 309729.1943),
        (ACQUIRED_ROW, 165816.9858, 943835.0),
        (WHOLE_ROW, 11350.0, 943835.0),
        (WHOLE_ROW | {"totalAcquired": 0, "totalDisposed": 0}, 0.0, 0.0),
        # Other independently observed disposed quantities in the issue.
        (
            WHOLE_ROW | {"symbol": "MSFT", "totalDisposed": 234618.27500000002},
            11350.0,
            234618.27500000002,
        ),
        (WHOLE_ROW | {"symbol": "AVGO", "totalDisposed": 176758.5}, 11350.0, 176758.5),
    ],
)
def test_share_totals_preserve_provider_values(
    model: type[InsiderStatistic] | type[InsiderTradingStatistics],
    row: dict[str, Any],
    acquired: float,
    disposed: float,
) -> None:
    stats = model.model_validate(row)
    assert stats.total_acquired == acquired
    assert stats.total_disposed == disposed
    assert isinstance(stats.total_acquired, float)
    assert isinstance(stats.total_disposed, float)
    dumped = stats.model_dump(mode="json", by_alias=True)
    assert dumped["totalAcquired"] == acquired
    assert dumped["totalDisposed"] == disposed
    for field in (
        "acquired_transactions",
        "disposed_transactions",
        "total_purchases",
        "total_sales",
    ):
        assert isinstance(getattr(stats, field), int)


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize(
    "field",
    ["acquiredTransactions", "disposedTransactions", "totalPurchases", "totalSales"],
)
def test_fractional_transaction_counts_remain_invalid(
    model: type[InsiderStatistic] | type[InsiderTradingStatistics], field: str
) -> None:
    with pytest.raises(ValidationError) as error:
        model.model_validate(WHOLE_ROW | {field: 1.5})
    assert error.value.errors()[0]["loc"] == (field,)
    assert error.value.errors()[0]["type"] == "int_from_float"


@pytest.mark.parametrize(
    "endpoint", [INSIDER_STATISTICS, INSIDER_TRADING_STATISTICS_ENHANCED]
)
def test_response_processing_retains_fractional_historical_rows(
    endpoint: Endpoint[Any],
) -> None:
    rows = BaseClient._process_response(
        endpoint, [WHOLE_ROW, DISPOSED_ROW, ACQUIRED_ROW]
    )
    assert isinstance(rows, list)
    assert len(rows) == 3
    assert [row.year for row in rows] == [2026, 2020, 2015]
    assert rows[1].total_disposed == 309729.1943
    assert rows[2].total_acquired == 165816.9858


def response(rows: list[dict[str, Any]]) -> httpx.Response:
    return httpx.Response(
        200,
        json=rows,
        request=httpx.Request(
            "GET",
            "https://test.financialmodelingprep.com/stable/insider-trading/statistics?symbol=NVDA",
        ),
    )


@pytest.mark.parametrize("method,model", METHODS)
@pytest.mark.parametrize("first", [WHOLE_ROW, DISPOSED_ROW, ACQUIRED_ROW])
def test_sync_statistics_parse_fractional_history(
    fmp_client: FMPDataClient,
    method: str,
    model: type[InsiderStatistic] | type[InsiderTradingStatistics],
    first: dict[str, Any],
) -> None:
    with patch(
        "httpx.Client.request",
        return_value=response([first, DISPOSED_ROW, ACQUIRED_ROW]),
    ):
        stats = getattr(fmp_client.institutional, method)("NVDA")
    assert isinstance(stats, model)
    assert stats.year == first["year"]
    assert stats.total_acquired == first["totalAcquired"]
    assert stats.total_disposed == first["totalDisposed"]


@pytest.mark.asyncio
@pytest.mark.parametrize("method,model", METHODS)
@pytest.mark.parametrize("first", [WHOLE_ROW, DISPOSED_ROW, ACQUIRED_ROW])
async def test_async_statistics_parse_fractional_history(
    client_config: ClientConfig,
    method: str,
    model: type[InsiderStatistic] | type[InsiderTradingStatistics],
    first: dict[str, Any],
) -> None:
    with patch(
        "httpx.AsyncClient.request",
        new_callable=AsyncMock,
        return_value=response([first, DISPOSED_ROW, ACQUIRED_ROW]),
    ):
        async with AsyncFMPDataClient(config=client_config) as client:
            stats = await getattr(client.institutional, method)("NVDA")
    assert isinstance(stats, model)
    assert stats.year == first["year"]
    assert stats.total_acquired == first["totalAcquired"]
    assert stats.total_disposed == first["totalDisposed"]


@pytest.mark.parametrize("method,model", METHODS)
def test_sync_statistics_reject_invalid_history(
    fmp_client: FMPDataClient,
    method: str,
    model: type[InsiderStatistic] | type[InsiderTradingStatistics],
) -> None:
    with patch(
        "httpx.Client.request",
        return_value=response([WHOLE_ROW, WHOLE_ROW | {"totalDisposed": "invalid"}]),
    ):
        with pytest.raises(ValidationError, match="totalDisposed"):
            getattr(fmp_client.institutional, method)("NVDA")


@pytest.mark.asyncio
@pytest.mark.parametrize("method,model", METHODS)
async def test_async_statistics_reject_invalid_history(
    client_config: ClientConfig,
    method: str,
    model: type[InsiderStatistic] | type[InsiderTradingStatistics],
) -> None:
    with patch(
        "httpx.AsyncClient.request",
        new_callable=AsyncMock,
        return_value=response([WHOLE_ROW, WHOLE_ROW | {"totalDisposed": "invalid"}]),
    ):
        async with AsyncFMPDataClient(config=client_config) as client:
            with pytest.raises(ValidationError, match="totalDisposed"):
                await getattr(client.institutional, method)("NVDA")
