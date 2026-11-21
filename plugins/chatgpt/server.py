"""Streamable HTTP MCP server for the fmp-data ChatGPT plugin."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import StringConstraints
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount

from fmp_data.async_client import AsyncFMPDataClient
from fmp_data.company.models import CompanyProfile, Quote
from fmp_data.exceptions import FMPError, FMPNotFound, RateLimitError
from fmp_data.market.models import CompanySearchResult

Symbol = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=32)
]
CompanyName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]
server = MCPServer("fmp-data", title="FMP Data")
read_market_data = ToolAnnotations(
    readOnlyHint=True, destructiveHint=False, openWorldHint=True, idempotentHint=True
)


@asynccontextmanager
async def market_client(ctx: Context) -> AsyncIterator[AsyncFMPDataClient]:
    try:
        request: Request = ctx.request_context.request
        yield request.app.state.fmp_client
    except FMPNotFound:
        raise ToolError("FMP returned no matching record.") from None
    except RateLimitError:
        raise ToolError("FMP request limit reached. Try again later.") from None
    except FMPError:
        raise ToolError("The requested market data is unavailable from FMP.") from None


@server.tool(title="Find company tickers", annotations=read_market_data)
async def search_companies(
    company_name: CompanyName, ctx: Context
) -> list[CompanySearchResult]:
    """Find up to five ticker symbols, exchanges, and currencies by company name."""
    async with market_client(ctx) as client:
        return await client.market.search_company(query=company_name, limit=5)


@server.tool(title="Get a stock quote", annotations=read_market_data)
async def get_stock_quote(symbol: Symbol, ctx: Context) -> Quote:
    """Get the latest available FMP price, change, and timestamp for one ticker."""
    async with market_client(ctx) as client:
        return await client.company.get_quote(symbol)


@server.tool(title="Get a company profile", annotations=read_market_data)
async def get_company_profile(symbol: Symbol, ctx: Context) -> CompanyProfile:
    """Look up a listed company's business description, industry, and exchange."""
    async with market_client(ctx) as client:
        return await client.company.get_profile(symbol)


transport = server.streamable_http_app(stateless_http=True, json_response=True)


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    async with AsyncFMPDataClient.from_env() as client:
        transport.state.fmp_client = client
        async with transport.router.lifespan_context(transport):
            yield


app = Starlette(routes=[Mount("/", app=transport)], lifespan=lifespan)
