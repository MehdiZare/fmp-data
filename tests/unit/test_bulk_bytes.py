"""Bulk-bytes / CSV endpoints stay off ``_unwrap_list`` (#247).

Quote lists are row-typed and go through ``_unwrap_list`` (#246). Bulk
downloads are ``bytes`` and go through ``_request_csv`` only.
``FINANCIAL_REPORTS_XLSX`` is a company XLSX download, not a batch CSV.
"""

from __future__ import annotations

import ast
from pathlib import Path
from types import UnionType
from typing import Union, get_args, get_origin, get_type_hints
from unittest.mock import AsyncMock, Mock

import pytest

from fmp_data.base import _unwrap_list_result
from fmp_data.batch import endpoints as batch_endpoints
from fmp_data.batch.async_client import AsyncBatchClient
from fmp_data.batch.client import BatchClient
from fmp_data.batch.endpoints import BATCH_QUOTE, PROFILE_BULK
from fmp_data.batch.models import BatchQuote
from fmp_data.exceptions import InvalidResponseTypeError
from fmp_data.models import Endpoint

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BATCH_CLIENTS = (
    _REPO_ROOT / "fmp_data" / "batch" / "client.py",
    _REPO_ROOT / "fmp_data" / "batch" / "async_client.py",
)
_CSV_BYTES = b"symbol\nAAPL\n"
_REJECT_PAYLOADS = (
    [{"symbol": "AAPL"}],
    [b"symbol\nAAPL\n"],
    "csv",
)


def _bulk_endpoint_names() -> list[str]:
    names = [
        name
        for name, value in vars(batch_endpoints).items()
        if name.endswith("_BULK") and isinstance(value, Endpoint)
    ]
    assert names, "expected at least one *_BULK endpoint"
    return sorted(names)


def _bulk_methods(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    methods: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for node in ast.walk(tree):
        if isinstance(
            node, ast.FunctionDef | ast.AsyncFunctionDef
        ) and node.name.endswith("_bulk"):
            methods.append(node)
    return methods


def _called_names(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            names.add(func.id)
        elif isinstance(func, ast.Attribute):
            names.add(func.attr)
    return names


def _sync_client(payload: object) -> tuple[BatchClient, Mock]:
    mock_client = Mock()
    mock_client.config.validation_mode = "warn"
    mock_client.request.return_value = payload
    return BatchClient(mock_client), mock_client


def _async_client(payload: object) -> tuple[AsyncBatchClient, Mock]:
    mock_client = Mock()
    mock_client.config.validation_mode = "warn"
    mock_client.request_async = AsyncMock(return_value=payload)
    return AsyncBatchClient(mock_client), mock_client


def _is_t_or_list_t(annotation: object) -> bool:
    if get_origin(annotation) not in {UnionType, Union}:
        return False
    return any(get_origin(arg) is list for arg in get_args(annotation))


class TestBulkEndpointBindings:
    @pytest.mark.parametrize("name", _bulk_endpoint_names())
    def test_bulk_endpoints_bind_bytes_not_a_row_type(self, name: str) -> None:
        endpoint = getattr(batch_endpoints, name)
        assert endpoint.response_model is bytes

    @pytest.mark.parametrize("name", _bulk_endpoint_names())
    def test_bulk_endpoints_are_annotated_endpoint_bytes(self, name: str) -> None:
        hints = get_type_hints(batch_endpoints)
        assert hints[name] == Endpoint[bytes]

    def test_quote_lists_stay_row_typed(self) -> None:
        hints = get_type_hints(batch_endpoints)
        assert hints["BATCH_QUOTE"] == Endpoint[BatchQuote]
        assert BATCH_QUOTE.response_model is BatchQuote


class TestRequestCsvIsTheBytesHelper:
    @pytest.mark.parametrize(
        "method",
        [BatchClient._request_csv, AsyncBatchClient._request_csv],
    )
    def test_request_csv_is_annotated_endpoint_bytes(self, method: object) -> None:
        hints = get_type_hints(method)
        assert hints["endpoint"] == Endpoint[bytes]
        assert hints["return"] is bytes

    @pytest.mark.parametrize("path", _BATCH_CLIENTS)
    def test_bulk_methods_call_request_csv_not_unwrap_list(self, path: Path) -> None:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        methods = _bulk_methods(tree)
        assert methods, f"expected *_bulk methods in {path.name}"
        for method in methods:
            called = _called_names(method)
            assert "_request_csv" in called, method.name
            assert "_unwrap_list" not in called, method.name

    @pytest.mark.parametrize("payload", _REJECT_PAYLOADS)
    def test_request_csv_rejects_non_bytes_payload(self, payload: object) -> None:
        client, _ = _sync_client(payload)
        with pytest.raises(InvalidResponseTypeError, match="expected bytes"):
            client._request_csv(PROFILE_BULK, part="0")

    def test_request_csv_accepts_bytes(self) -> None:
        client, _ = _sync_client(_CSV_BYTES)
        result = client._request_csv(PROFILE_BULK, part="0")
        assert result == _CSV_BYTES
        assert type(result) is bytes

    def test_request_csv_accepts_bytearray(self) -> None:
        client, _ = _sync_client(bytearray(_CSV_BYTES))
        result = client._request_csv(PROFILE_BULK, part="0")
        assert result == _CSV_BYTES
        assert type(result) is bytes

    @pytest.mark.asyncio
    @pytest.mark.parametrize("payload", _REJECT_PAYLOADS)
    async def test_async_request_csv_rejects_non_bytes_payload(
        self, payload: object
    ) -> None:
        client, _ = _async_client(payload)
        with pytest.raises(InvalidResponseTypeError, match="expected bytes"):
            await client._request_csv(PROFILE_BULK, part="0")

    @pytest.mark.asyncio
    async def test_async_request_csv_accepts_bytes(self) -> None:
        client, _ = _async_client(_CSV_BYTES)
        result = await client._request_csv(PROFILE_BULK, part="0")
        assert result == _CSV_BYTES
        assert type(result) is bytes

    @pytest.mark.asyncio
    async def test_async_request_csv_accepts_bytearray(self) -> None:
        client, _ = _async_client(bytearray(_CSV_BYTES))
        result = await client._request_csv(PROFILE_BULK, part="0")
        assert result == _CSV_BYTES
        assert type(result) is bytes

    def test_get_profile_bulk_parses_bytes_not_a_wrapped_file(self) -> None:
        client, mock_client = _sync_client(_CSV_BYTES)
        rows = client.get_profile_bulk("0")

        assert [row.symbol for row in rows] == ["AAPL"]
        assert all(not isinstance(row, bytes) for row in rows)
        mock_client.request.assert_called_once_with(PROFILE_BULK, part="0")

    @pytest.mark.asyncio
    async def test_async_get_profile_bulk_parses_bytes_not_a_wrapped_file(self) -> None:
        client, mock_client = _async_client(_CSV_BYTES)
        rows = await client.get_profile_bulk("0")

        assert [row.symbol for row in rows] == ["AAPL"]
        assert all(not isinstance(row, bytes) for row in rows)
        mock_client.request_async.assert_awaited_once_with(PROFILE_BULK, part="0")

    def test_unwrap_list_would_wrap_bytes_as_a_single_row(self) -> None:
        """``isinstance(payload, bytes)`` is true, so unwrap is the wrong helper."""
        raw = b"symbol,name\nAAPL,Apple\n"
        assert _unwrap_list_result(raw, bytes) == [raw]


def test_request_signature_stays_union() -> None:
    from fmp_data.base import BaseClient

    assert _is_t_or_list_t(get_type_hints(BaseClient.request)["return"])
    assert _is_t_or_list_t(get_type_hints(BaseClient.request_async)["return"])
