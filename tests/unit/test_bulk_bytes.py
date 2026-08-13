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
from unittest.mock import AsyncMock, Mock, patch

import pytest

from fmp_data.base import BaseClient, _unwrap_list_result
from fmp_data.batch import endpoints as batch_endpoints
from fmp_data.batch.async_client import AsyncBatchClient
from fmp_data.batch.client import BatchClient
from fmp_data.batch.endpoints import BATCH_QUOTE, PROFILE_BULK
from fmp_data.batch.models import BatchQuote
from fmp_data.config import ClientConfig
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

    def test_unwrap_list_refuses_bytes(self) -> None:
        """``isinstance(payload, bytes)`` is true; unwrap must not wrap a file."""
        raw = b"symbol,name\nAAPL,Apple\n"
        with pytest.raises(TypeError, match="not a list row type"):
            _unwrap_list_result(raw, bytes)

    def test_endpoint_group_unwrap_list_refuses_bytes(self) -> None:
        from fmp_data.base import EndpointGroup

        raw = b"PK\x03\x04xlsx"
        with pytest.raises(TypeError, match="not a list row type"):
            EndpointGroup._unwrap_list(raw, bytes)


def _base_client() -> BaseClient:
    return BaseClient(ClientConfig(api_key="test_key", base_url="https://api.test.com"))


def _overload_return_annotations(method_name: str) -> list[ast.expr]:
    source = (_REPO_ROOT / "fmp_data" / "base.py").read_text(encoding="utf-8")
    tree = ast.parse(source, filename="fmp_data/base.py")
    returns: list[ast.expr] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != "BaseClient":
            continue
        for item in node.body:
            if not isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            if item.name != method_name:
                continue
            if any(
                (isinstance(dec, ast.Name) and dec.id == "overload")
                or (isinstance(dec, ast.Attribute) and dec.attr == "overload")
                for dec in item.decorator_list
            ):
                if item.returns is not None:
                    returns.append(item.returns)
    return returns


def _annotation_names(expr: ast.expr) -> set[str]:
    return {node.id for node in ast.walk(expr) if isinstance(node, ast.Name)}


class TestRequestBytesOverloadAndListRefusal:
    """``request(Endpoint[bytes]) -> bytes``; ``request_list`` refuses bytes (#249)."""

    @pytest.mark.parametrize("method_name", ["request", "request_async"])
    def test_bytes_overload_returns_bytes(self, method_name: str) -> None:
        returns = _overload_return_annotations(method_name)
        assert returns, f"expected overloads on BaseClient.{method_name}"
        first = returns[0]
        assert isinstance(first, ast.Name) and first.id == "bytes", (
            f"first BaseClient.{method_name} overload must return bytes"
        )
        assert any("list" in _annotation_names(expr) for expr in returns[1:]), (
            f"expected the T | list[T] overload to remain on BaseClient.{method_name}"
        )

    @pytest.mark.parametrize("method_name", ["request_list", "request_async_list"])
    def test_list_helper_bytes_overload_is_noreturn(self, method_name: str) -> None:
        returns = _overload_return_annotations(method_name)
        assert returns, f"expected overloads on BaseClient.{method_name}"
        first = returns[0]
        assert isinstance(first, ast.Name) and first.id == "NoReturn", (
            f"first BaseClient.{method_name} overload must return NoReturn"
        )
        assert any("list" in _annotation_names(expr) for expr in returns[1:]), (
            f"expected the list[T] overload to remain on BaseClient.{method_name}"
        )

    def test_request_bytes_endpoint_returns_bytes_not_list(self) -> None:
        client = _base_client()
        response = Mock()
        response.status_code = 200
        response.content = _CSV_BYTES
        response.close = Mock()
        with patch.object(client.client, "request", return_value=response):
            result = client.request(PROFILE_BULK, part="0")
        assert type(result) is bytes
        assert result == _CSV_BYTES

    @pytest.mark.asyncio
    async def test_request_async_bytes_endpoint_returns_bytes_not_list(self) -> None:
        client = _base_client()
        response = Mock()
        response.status_code = 200
        response.content = _CSV_BYTES
        response.raise_for_status = Mock()
        response.aclose = AsyncMock()
        mock_http = Mock()
        mock_http.request = AsyncMock(return_value=response)
        with patch.object(client, "_setup_async_client", return_value=mock_http):
            result = await client.request_async(PROFILE_BULK, part="0")
        assert type(result) is bytes
        assert result == _CSV_BYTES

    def test_request_list_refuses_profile_bulk(self) -> None:
        client = _base_client()
        with (
            patch.object(client, "request") as request,
            pytest.raises(TypeError, match="profile_bulk"),
        ):
            client.request_list(PROFILE_BULK, part="0")
        request.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_async_list_refuses_profile_bulk(self) -> None:
        client = _base_client()
        with (
            patch.object(client, "request_async") as request_async,
            pytest.raises(TypeError, match="profile_bulk"),
        ):
            await client.request_async_list(PROFILE_BULK, part="0")
        request_async.assert_not_called()

    def test_request_list_still_unwraps_quote_lists(self) -> None:
        client = _base_client()
        quote = BatchQuote(symbol="AAPL")
        with patch.object(client, "request", return_value=quote) as request:
            result = client.request_list(BATCH_QUOTE, symbols=["AAPL"])
        assert result == [quote]
        request.assert_called_once_with(BATCH_QUOTE, symbols=["AAPL"])

    @pytest.mark.asyncio
    async def test_request_async_list_still_unwraps_quote_lists(self) -> None:
        client = _base_client()
        quote = BatchQuote(symbol="AAPL")
        with patch.object(
            client, "request_async", new=AsyncMock(return_value=quote)
        ) as request_async:
            result = await client.request_async_list(BATCH_QUOTE, symbols=["AAPL"])
        assert result == [quote]
        request_async.assert_awaited_once_with(BATCH_QUOTE, symbols=["AAPL"])


def test_request_signature_stays_union() -> None:
    from fmp_data.base import BaseClient

    assert _is_t_or_list_t(get_type_hints(BaseClient.request)["return"])
    assert _is_t_or_list_t(get_type_hints(BaseClient.request_async)["return"])
