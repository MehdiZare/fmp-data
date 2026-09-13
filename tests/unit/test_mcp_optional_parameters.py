"""Native MCP schema generation and invocation retain new optional filters."""

import importlib
import inspect
from typing import Any

import httpx
import pytest

pytest.importorskip("mcp", reason="MCP extra not installed")

from fmp_data.mcp._compat import import_mcp_server_class
from fmp_data.mcp.tool_loader import register_from_manifest
from tests.unit.test_provider_optional_parameters import CASES, IDS, _transport


@pytest.mark.parametrize("case", CASES, ids=IDS)
@pytest.mark.parametrize("mode", ["omitted", "none", "value"])
@pytest.mark.asyncio
async def test_native_mcp_schema_and_query(case, mode, fmp_client):
    captured: list[dict[str, Any]] = []
    fmp_client.client.close()
    fmp_client.client = httpx.Client(transport=_transport(case, captured))
    server = import_mcp_server_class()("parameter-coverage")
    method = getattr(getattr(fmp_client, case["group"]), case["method"])
    module = importlib.import_module(f"fmp_data.{case['group']}.mapping")
    table = getattr(module, f"{case['group'].upper()}_ENDPOINTS_SEMANTICS")
    keys = [key for key, sem in table.items() if sem.method_name == case["method"]]
    if keys:
        register_from_manifest(server, fmp_client, [f"{case['group']}.{keys[0]}"])
    else:
        # Existing SDK-only methods can be explicitly wrapped by applications.
        server.add_tool(method)
    tools = await server.list_tools()
    assert len(tools) == 1
    schema = tools[0].model_dump(by_alias=True)["inputSchema"]
    params = dict(zip(inspect.signature(method).parameters, case["args"], strict=False))
    expected = dict(case["baseline_request"]["query"])
    for new in case["new_parameters"]:
        assert new["name"] in schema["properties"]
        assert new["name"] not in schema.get("required", [])
        assert schema["properties"][new["name"]]["default"] is None
        if mode != "omitted":
            params[new["name"]] = new["sample"] if mode == "value" else None
        if mode == "value":
            value = new["sample"]
            expected[new["wire"]] = (
                str(value).lower() if isinstance(value, bool) else str(value)
            )
    await server.call_tool(tools[0].name, params)
    assert len(captured) == 1
    assert captured[0]["query"] == expected
