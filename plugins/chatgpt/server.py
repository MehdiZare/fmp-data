"""Streamable HTTP MCP server for the fmp-data ChatGPT plugin."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
from typing import Annotated
from urllib.parse import urlsplit

from mcp.server import MCPServer
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import (
    AuthSettings,
    ClientRegistrationOptions,
    RevocationOptions,
)
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import StringConstraints
from starlette.applications import Starlette
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.routing import Route

from fmp_data.async_client import AsyncFMPDataClient
from fmp_data.company.models import CompanyProfile, Quote
from fmp_data.exceptions import (
    AuthenticationError,
    FMPError,
    FMPNotFound,
    RateLimitError,
)
from fmp_data.market.models import CompanySearchResult
from plugins.chatgpt.accounts import SCOPE, Accounts
from plugins.chatgpt.connect import BindLinkCookie, connect

Symbol = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=32)
]
CompanyName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]
read_market_data = ToolAnnotations(
    readOnlyHint=True, destructiveHint=False, openWorldHint=True, idempotentHint=True
)


@asynccontextmanager
async def market_client(ctx: Context) -> AsyncIterator[AsyncFMPDataClient]:
    try:
        request: Request = ctx.request_context.request
        token = get_access_token()
        key = request.app.state.accounts.key_for(token.token) if token else None
        if key is None:
            raise ToolError("Reconnect your FMP account in ChatGPT.")
        async with AsyncFMPDataClient(api_key=key) as client:
            yield client
    except AuthenticationError:
        raise ToolError("FMP rejected your key. Reconnect your FMP account.") from None
    except FMPNotFound:
        raise ToolError("FMP returned no matching record.") from None
    except RateLimitError:
        raise ToolError("FMP request limit reached. Try again later.") from None
    except FMPError:
        raise ToolError("The requested market data is unavailable from FMP.") from None


async def search_companies(
    company_name: CompanyName, ctx: Context
) -> list[CompanySearchResult]:
    """Find up to five ticker symbols, exchanges, and currencies by company name."""
    async with market_client(ctx) as client:
        return await client.market.search_company(query=company_name, limit=5)


async def get_stock_quote(symbol: Symbol, ctx: Context) -> Quote:
    """Get the latest available FMP price, change, and timestamp for one ticker."""
    async with market_client(ctx) as client:
        return await client.company.get_quote(symbol)


async def get_company_profile(symbol: Symbol, ctx: Context) -> CompanyProfile:
    """Look up a listed company's business description, industry, and exchange."""
    async with market_client(ctx) as client:
        return await client.company.get_profile(symbol)


def create_app() -> Starlette:
    accounts = Accounts()
    url = urlsplit(accounts.origin)
    # HTTPX logs full request URLs at INFO. FMP authenticates via a query parameter.
    for name in ("httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)
    server = MCPServer(
        "fmp-data",
        title="FMP Data",
        auth_server_provider=accounts,
        auth=AuthSettings(
            issuer_url=accounts.origin,
            resource_server_url=accounts.resource,
            validate_token_resource=True,
            required_scopes=[SCOPE],
            client_registration_options=ClientRegistrationOptions(
                valid_scopes=[SCOPE], default_scopes=[SCOPE]
            ),
            revocation_options=RevocationOptions(enabled=True),
        ),
    )
    for tool, title in (
        (search_companies, "Find company tickers"),
        (get_stock_quote, "Get a stock quote"),
        (get_company_profile, "Get a company profile"),
    ):
        server.add_tool(
            tool,
            title=title,
            annotations=read_market_data,
            meta={"securitySchemes": [{"type": "oauth2", "scopes": [SCOPE]}]},
        )
    app = server.streamable_http_app(
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(
            allowed_hosts=[url.netloc], allowed_origins=[accounts.origin]
        ),
    )
    app.state.accounts = accounts
    app.router.routes.insert(0, Route("/connect", connect, methods=["GET", "POST"]))
    app.add_middleware(BindLinkCookie)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[url.hostname])
    return app
