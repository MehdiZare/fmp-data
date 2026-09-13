"""Exercise actual LangChain schemas and dispatch for provider filters."""

import importlib
from pathlib import Path
from typing import Any

import httpx
from langchain_core.embeddings import FakeEmbeddings
from langchain_core.tools import StructuredTool
from pydantic import BaseModel
import pytest

from fmp_data import FMPDataClient
from fmp_data.lc.models import EndpointInfo
from fmp_data.lc.registry import EndpointRegistry
from fmp_data.lc.vector_store import EndpointVectorStore
from fmp_data.tool_binding import resolve_method_param_name
from tests.unit.test_provider_optional_parameters import CASES, IDS, _transport

# These methods were never in the tool catalog. Keep the inventory stable;
# their SDK signatures and HTTP queries are covered in the core regression suite.
SDK_ONLY = {
    ("market", "get_company_screener"),
    ("market", "get_available_exchanges"),
    ("company", "get_earnings"),
}


@pytest.mark.parametrize("case", CASES, ids=IDS)
@pytest.mark.parametrize("mode", ["omitted", "none", "value"])
def test_native_langchain_tool_preserves_filters(
    case: dict[str, Any],
    mode: str,
    fmp_client: FMPDataClient,
    tmp_path: Path,
) -> None:
    module = importlib.import_module(f"fmp_data.{case['group']}.mapping")
    table = getattr(module, f"{case['group'].upper()}_ENDPOINTS_SEMANTICS")
    matches = [s for s in table.values() if s.method_name == case["method"]]
    if (case["group"], case["method"]) in SDK_ONLY:
        assert matches == []
        return
    assert matches
    endpoint = getattr(
        importlib.import_module(f"fmp_data.{case['group']}.endpoints"), case["endpoint"]
    )
    optional_by_wire = {p.alias or p.name: p for p in endpoint.optional_params}
    captured: list[dict[str, Any]] = []
    fmp_client.client.close()
    fmp_client.client = httpx.Client(transport=_transport(case, captured))
    store = EndpointVectorStore(
        client=fmp_client,
        registry=EndpointRegistry(),
        embeddings=FakeEmbeddings(size=8),
        cache_dir=str(tmp_path),
    )
    for semantics in matches:
        tool = store.create_tool(EndpointInfo(endpoint=endpoint, semantics=semantics))
        assert isinstance(tool, StructuredTool)
        model = tool.get_input_schema()
        assert issubclass(model, BaseModel)
        schema = model.model_json_schema()
        required_args = dict(
            zip(
                [p["name"] for p in case["baseline_parameters"]],
                case["args"],
                strict=False,
            )
        )
        params = {}
        for param in endpoint.mandatory_params:
            name = resolve_method_param_name(param.name, set(required_args))
            if name is not None:
                params[param.name] = required_args[name]
        expected = dict(case["baseline_request"]["query"])
        for new in case["new_parameters"]:
            param = optional_by_wire[new["wire"]]
            assert param.name in schema["properties"]
            assert param.name not in schema.get("required", [])
            assert param.name in semantics.parameter_hints
            if mode != "omitted":
                params[param.name] = new["sample"] if mode == "value" else None
            if mode == "value":
                value = new["sample"]
                expected[new["wire"]] = (
                    str(value).lower() if isinstance(value, bool) else str(value)
                )
        result = tool.invoke(params)
        assert result["status"] == "success", result
        assert captured[-1]["query"] == expected
