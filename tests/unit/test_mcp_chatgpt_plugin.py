"""Exercise ChatGPT tool discovery and calls through the HTTP transport."""

from importlib import import_module
from unittest.mock import AsyncMock

import pytest

from fmp_data.async_client import AsyncFMPDataClient
from fmp_data.exceptions import FMPError

pytest.importorskip("mcp.server.mcpserver")


def test_chatgpt_plugin_over_http(monkeypatch):
    from starlette.testclient import TestClient

    app = import_module("plugins.chatgpt.server").app
    monkeypatch.setenv("FMP_API_KEY", "offline-test-key")
    provider = AsyncMock(return_value=[{"name": "Example Corp", "symbol": "EXMP"}])
    monkeypatch.setattr(AsyncFMPDataClient, "request_async", provider)
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:

        def rpc(method, params):
            response = client.post(
                "/mcp",
                headers={"Accept": "application/json, text/event-stream"},
                json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
            )
            response.raise_for_status()
            return response.json()["result"]

        result = rpc(
            "initialize",
            {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "plugin-test", "version": "1"},
            },
        )
        assert result["serverInfo"]["name"] == "fmp-data"
        tools = rpc("tools/list", {})["tools"]
        assert {tool["name"] for tool in tools} == {
            "search_companies",
            "get_stock_quote",
            "get_company_profile",
        }
        for tool in tools:
            assert tool["annotations"]["readOnlyHint"]
            assert "ctx" not in tool["inputSchema"]["properties"]

        def call(name, **arguments):
            return rpc("tools/call", {"name": name, "arguments": arguments})

        matched = call("search_companies", company_name="Example")
        assert not matched["isError"]
        assert "EXMP" in matched["content"][0]["text"]
        assert provider.await_args is not None
        assert provider.await_args.kwargs == {"query": "Example", "limit": 5}
        assert call("get_stock_quote", symbol=" ")["isError"]
        assert provider.await_count == 1

        provider.return_value = [
            {
                "symbol": "EXMP",
                "name": "Example Corp",
                "price": 10,
                "changePercentage": 0,
                "change": 0,
                "dayLow": 9,
                "dayHigh": 11,
                "exchange": "NASDAQ",
                "timestamp": 1700000000,
            }
        ]
        quote = call("get_stock_quote", symbol="EXMP")
        assert not quote["isError"]
        assert quote["structuredContent"]["price"] == 10
        assert quote["structuredContent"]["timestamp"]
        profile = call("get_company_profile", symbol="EXMP")
        assert not profile["isError"]
        assert profile["structuredContent"]["symbol"] == "EXMP"

        provider.side_effect = FMPError("private upstream diagnostic")
        for tool_name in ["get_stock_quote", "get_company_profile"]:
            result = call(tool_name, symbol="EXMP")
            assert result["isError"]
            assert "unavailable from FMP" in result["content"][0]["text"]
            assert "private upstream diagnostic" not in str(result)
