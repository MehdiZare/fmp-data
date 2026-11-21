"""Exercise ChatGPT tool discovery and calls through the HTTP transport."""

from base64 import urlsafe_b64encode
from hashlib import sha256
from importlib import import_module
import secrets
from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlsplit

import pytest

from fmp_data.async_client import AsyncFMPDataClient
from fmp_data.exceptions import FMPError

pytest.importorskip("mcp.server.mcpserver")


ORIGIN = "https://fmp.test"
CALLBACK = "https://chatgpt.test/callback"


@pytest.fixture
def session(monkeypatch, tmp_path):
    from starlette.testclient import TestClient

    secret = secrets.token_urlsafe(32)
    db = tmp_path / "connections.db"
    for name, value in {
        "FMP_PLUGIN_DATABASE": str(db),
        "FMP_PLUGIN_ORIGIN": ORIGIN,
        "FMP_PLUGIN_REDIRECT_URI": CALLBACK,
        "FMP_PLUGIN_CLIENT_SECRET": secret,
        "FMP_PLUGIN_ENCRYPTION_KEY": urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode(),
        "FMP_API_KEY": secrets.token_urlsafe(32),
    }.items():
        monkeypatch.setenv(name, value)
    app = import_module("plugins.chatgpt.server").create_app()
    with TestClient(app, base_url=ORIGIN, follow_redirects=False) as client:
        yield client, {"client_id": "fmp-data-chatgpt", "client_secret": secret}, db


def begin_connection(client, registration):
    verifier = secrets.token_urlsafe(48)
    challenge = (
        urlsafe_b64encode(sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    )
    params = {
        "client_id": registration["client_id"],
        "redirect_uri": CALLBACK,
        "response_type": "code",
        "scope": "market:read",
        "state": "original-state",
        "code_challenge_method": "S256",
        "code_challenge": challenge,
        "resource": ORIGIN + "/mcp",
    }
    start = client.get("/authorize", params=params)
    assert start.status_code == 302, start.text
    assert start.headers["location"] == "/connect"
    assert client.get("/connect").status_code == 200
    return verifier


def link_account(client, registration, key):
    verifier = begin_connection(client, registration)
    assert client.post("/connect", data={"api_key": key}).status_code == 403
    approval = client.post(
        "/connect", headers={"Origin": ORIGIN}, data={"api_key": key}
    )
    assert approval.status_code == 303, approval.text
    location = urlsplit(approval.headers["location"])
    assert location.netloc == "chatgpt.test"
    query = parse_qs(location.query)
    assert query["state"] == ["original-state"]
    exchange = {
        **registration,
        "grant_type": "authorization_code",
        "code": query["code"][0],
        "redirect_uri": CALLBACK,
        "code_verifier": verifier,
        "resource": ORIGIN + "/mcp",
    }
    assert (
        client.post(
            "/token", data={**exchange, "code_verifier": "incorrect"}
        ).status_code
        == 400
    )
    result = client.post("/token", data=exchange)
    assert result.is_success, result.text
    assert key not in result.text
    assert client.post("/token", data=exchange).status_code == 400
    return result.json()


def test_chatgpt_plugin_over_http(monkeypatch, session):
    client, registration, _ = session
    provider = AsyncMock(return_value=[{"name": "Example Corp", "symbol": "EXMP"}])
    monkeypatch.setattr(AsyncFMPDataClient, "request_async", provider)
    monkeypatch.setattr(
        "fmp_data.company.async_client.AsyncCompanyClient.get_simple_quote", AsyncMock()
    )
    assert client.post("/mcp").status_code == 401
    discovery = client.get("/.well-known/oauth-protected-resource/mcp")
    assert discovery.json()["resource"] == ORIGIN + "/mcp"
    token = link_account(client, registration, "offline-user-one")["access_token"]
    client.headers["Authorization"] = "Bearer " + token

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


def test_connections_use_distinct_keys_and_refresh_and_revoke(monkeypatch, session):
    client, registration, db = session
    keys_seen = []

    async def provider(self, *args, **kwargs):
        keys_seen.append(self.config.api_key.get_secret_value())
        return [{"symbol": "EXMP", "name": "Example", "price": 10}]

    monkeypatch.setattr(AsyncFMPDataClient, "request_async", provider)
    a = link_account(client, registration, "first-user-key")
    b = link_account(client, registration, "second-user-key")
    assert keys_seen == ["first-user-key", "second-user-key"]
    keys_seen.clear()

    def search(token):
        return client.post(
            "/mcp",
            headers={
                "Authorization": "Bearer " + token,
                "Accept": "application/json, text/event-stream",
            },
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "search_companies",
                    "arguments": {"company_name": "Example"},
                },
            },
        )

    def refresh(token):
        return client.post(
            "/token",
            data={
                **registration,
                "grant_type": "refresh_token",
                "refresh_token": token,
            },
        )

    assert search(b["access_token"]).json()["result"]["isError"] is False
    assert search(a["access_token"]).json()["result"]["isError"] is False
    assert keys_seen == ["second-user-key", "first-user-key"]
    rotated = refresh(a["refresh_token"]).json()
    assert refresh(a["refresh_token"]).status_code == 400
    assert search(a["access_token"]).status_code == 401
    assert search(rotated["access_token"]).status_code == 200
    assert client.post(
        "/revoke", data={**registration, "token": rotated["refresh_token"]}
    ).is_success
    assert search(rotated["access_token"]).status_code == 401
    assert search(b["access_token"]).status_code == 200
    assert keys_seen[-2:] == ["first-user-key", "second-user-key"]
    raw = db.read_bytes()
    for value in (
        "first-user-key",
        "second-user-key",
        b["access_token"],
        b["refresh_token"],
    ):
        assert value.encode() not in raw


def test_invalid_fmp_key_creates_no_connection(monkeypatch, session):
    from fmp_data.exceptions import AuthenticationError

    client, registration, _ = session
    begin_connection(client, registration)
    key = "unverified-user-key"
    monkeypatch.setattr(
        "fmp_data.company.async_client.AsyncCompanyClient.get_simple_quote",
        AsyncMock(side_effect=AuthenticationError("FMP rejected this credential")),
    )
    result = client.post("/connect", headers={"Origin": ORIGIN}, data={"api_key": key})
    assert result.status_code == 400
    assert key not in result.text
    assert "location" not in result.headers
    with client.app.state.accounts.database() as database:
        assert database.execute("SELECT COUNT(*) FROM grants").fetchone()[0] == 0
