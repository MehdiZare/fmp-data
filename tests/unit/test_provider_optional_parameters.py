"""Provider-derived expectations plus pre-change signatures and HTTP requests.

The fixture was captured from FMP's documentation and dev at 02d2a90 on
2026-09-13, before changing the SDK. Do not regenerate it from endpoint metadata:
that would let a missing parameter disappear from both sides of the assertion.
"""

import ast
from datetime import date
import importlib
import inspect
import json
from pathlib import Path
from typing import Any, get_type_hints

import httpx
import pytest

from fmp_data import AsyncFMPDataClient, FMPDataClient
from fmp_data.tool_binding import resolve_method_param_name

CASES = json.loads(
    (
        Path(__file__).parents[1] / "fixtures/provider_optional_parameters.json"
    ).read_text()
)["cases"]
IDS = [f"{case['group']}.{case['method']}" for case in CASES]


def test_provider_fixture_retains_all_audited_findings():
    assert len(CASES) == len(set(IDS)) == 27
    assert sum(len(case["new_parameters"]) for case in CASES) == 74


def _sample(param):
    value = param["sample"]
    return date.fromisoformat(value) if param["type"] == "date" else value


def _transport(case, captured):
    def respond(request):
        captured.append(
            {
                "path": request.url.path,
                "query": {k: v for k, v in request.url.params.items() if k != "apikey"},
            }
        )
        payload = []
        if case["method"] == "get_market_hours":
            payload = [
                {
                    "exchange": "NYSE",
                    "name": "New York Stock Exchange",
                    "openingHour": "09:30",
                    "closingHour": "16:00",
                    "timezone": "America/New_York",
                    "isMarketOpen": True,
                }
            ]
        return httpx.Response(200, json=payload)

    return httpx.MockTransport(respond)


@pytest.mark.parametrize("case", CASES, ids=IDS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_additions_preserve_signature(case, asynchronous, client_config):
    cls = AsyncFMPDataClient if asynchronous else FMPDataClient
    client = cls(
        config=client_config.model_copy(
            update={"base_url": "https://test.financialmodelingprep.com"}
        )
    )
    try:
        method = getattr(getattr(client, case["group"]), case["method"])
        signature = inspect.signature(method)
        old = case["baseline_parameters"]
        assert list(signature.parameters) == [p["name"] for p in old] + [
            p["name"] for p in case["new_parameters"]
        ]
        for baseline in old:
            param = signature.parameters[baseline["name"]]
            assert param.kind.name == baseline["kind"]
            assert repr(param.default) == baseline["default"]
        for new in case["new_parameters"]:
            param = signature.parameters[new["name"]]
            assert param.kind is inspect.Parameter.KEYWORD_ONLY
            assert param.default is None
            python_type = {
                "date": date,
                "int": int,
                "float": float,
                "str": str,
                "bool": bool,
            }[new["type"]]
            assert get_type_hints(method)[new["name"]] == python_type | None
        source = inspect.getsourcefile(method)
        assert source is not None
        tree = ast.parse(Path(source).read_text())
        node = next(
            n
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name == case["method"]
        )
        # Async modules use future annotations but preserve the same public types.
        assert node.returns is not None
        assert ast.unparse(node.returns) == case["return_annotation"]
        assert {
            arg.arg: ast.unparse(arg.annotation) if arg.annotation else None
            for arg in node.args.args
            if arg.arg != "self"
        } == case["baseline_annotations"]
    finally:
        client.close()


@pytest.mark.parametrize("case", CASES, ids=IDS)
@pytest.mark.parametrize("mode", ["omitted", "positional", "none", "value"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.asyncio
async def test_actual_query_and_legacy_defaults(
    case, mode, asynchronous, client_config
):
    captured: list[dict[str, Any]] = []
    cls = AsyncFMPDataClient if asynchronous else FMPDataClient
    client = cls(
        config=client_config.model_copy(
            update={"base_url": "https://test.financialmodelingprep.com"}
        )
    )
    transport = _transport(case, captured)
    if asynchronous:
        client._async_client = httpx.AsyncClient(transport=transport)
    else:
        client.client.close()
        client.client = httpx.Client(transport=transport)
    kwargs = (
        {}
        if mode in {"omitted", "positional"}
        else {
            p["name"]: _sample(p) if mode == "value" else None
            for p in case["new_parameters"]
        }
    )
    try:
        method = getattr(getattr(client, case["group"]), case["method"])
        args = list(case["args"])
        if mode == "positional":
            args.extend(
                ast.literal_eval(p["default"])
                for p in case["baseline_parameters"][len(args) :]
            )
        result = method(*args, **kwargs)
        if asynchronous:
            await result
    finally:
        if asynchronous:
            await client.aclose()
        else:
            client.close()
    expected = dict(case["baseline_request"]["query"])
    if mode == "value":
        for param in case["new_parameters"]:
            value = param["sample"]
            expected[param["wire"]] = (
                str(value).lower() if isinstance(value, bool) else str(value)
            )
    assert captured == [{"path": case["baseline_request"]["path"], "query": expected}]


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_provider_parameters_reach_metadata_and_binding(case, fmp_client):
    module = importlib.import_module(f"fmp_data.{case['group']}.endpoints")
    endpoint = getattr(module, case["endpoint"])
    optional_by_wire = {p.alias or p.name: p for p in endpoint.optional_params}
    method = getattr(getattr(fmp_client, case["group"]), case["method"])
    for expected in case["new_parameters"]:
        param = optional_by_wire[expected["wire"]]
        assert not param.required
        assert param.description
        assert (
            param.param_type.value
            == {
                "date": "date",
                "int": "integer",
                "float": "float",
                "str": "string",
                "bool": "boolean",
            }[expected["type"]]
        )
        assert (
            resolve_method_param_name(
                param.name, set(inspect.signature(method).parameters)
            )
            == expected["name"]
        )


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.asyncio
async def test_exchange_variants_uses_symbol_without_renaming_query(
    asynchronous, client_config
):
    captured: list[dict[str, Any]] = []
    client = (AsyncFMPDataClient if asynchronous else FMPDataClient)(
        config=client_config
    )
    transport = _transport({"method": "search_exchange_variants"}, captured)
    if asynchronous:
        client._async_client = httpx.AsyncClient(transport=transport)
    else:
        client.client.close()
        client.client = httpx.Client(transport=transport)
    try:
        method = client.market.search_exchange_variants
        assert list(inspect.signature(method).parameters) == ["query"]
        result = method("MSFT")
        if asynchronous:
            assert inspect.isawaitable(result)
            await result
    finally:
        if asynchronous:
            await client.aclose()
        else:
            client.close()
    assert captured[0]["query"] == {"symbol": "MSFT"}
