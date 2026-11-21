"""Browser-only account linking for the pre-registered ChatGPT client."""

from urllib.parse import parse_qs, urlsplit

from cryptography.fernet import InvalidToken
from mcp.server.auth.provider import AuthorizationParams, construct_redirect_uri
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import (
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)

from fmp_data.async_client import AsyncFMPDataClient
from fmp_data.exceptions import AuthenticationError, FMPError
from plugins.chatgpt.accounts import Accounts


def cookie_name(origin: str) -> str:
    return "__Host-fmp-link" if origin.startswith("https://") else "fmp-link"


HEADERS = {
    "Cache-Control": "no-store",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": (
        "default-src 'none'; form-action 'self'; "
        "frame-ancestors 'none'; base-uri 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
}
FORM = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Connect your FMP account</title><main><h1>Connect your FMP account</h1>
<p>Allow ChatGPT to look up quotes, company profiles, and tickers using your
Financial Modeling Prep subscription. Requests count against your account quota.
The plugin stores your key encrypted and checks it with one AAPL lookup.</p>
<form method="post" action="/connect">
<label>FMP API key <input name="api_key" type="password" maxlength="256"
autocomplete="off" required></label>
<button type="submit">Connect account</button></form></main></html>"""


class BindLinkCookie(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        location = response.headers.get("location", "")
        if (
            request.url.path == "/authorize"
            and response.status_code == 302
            and location.startswith("/connect#")
        ):
            response.headers["location"] = "/connect"
            response.set_cookie(
                cookie_name(request.app.state.accounts.origin),
                location.split("#", 1)[1],
                max_age=300,
                path="/",
                httponly=True,
                samesite="lax",
                secure=request.app.state.accounts.origin.startswith("https://"),
            )
        return response


async def submitted_key(request: Request) -> str:
    if (
        request.headers.get("content-type", "").split(";")[0]
        != "application/x-www-form-urlencoded"
    ):
        raise HTTPException(415, headers=HEADERS)
    data = bytearray()
    async for chunk in request.stream():
        if len(data) + len(chunk) > 2048:
            raise HTTPException(413, headers=HEADERS)
        data.extend(chunk)
    try:
        values = parse_qs(data.decode(), max_num_fields=1).get("api_key", [])
    except ValueError:
        values = []
    if len(values) != 1 or not 1 <= len(key := values[0].strip()) <= 256:
        raise HTTPException(400, "Enter your FMP API key.", headers=HEADERS)
    return key


async def connect(request: Request) -> Response:
    accounts: Accounts = request.app.state.accounts
    try:
        payload = accounts.cipher.decrypt(
            request.cookies.get(cookie_name(accounts.origin), "").encode(), ttl=300
        )
        params = AuthorizationParams.model_validate_json(payload)
    except (InvalidToken, ValueError):
        return PlainTextResponse(
            "Start a new connection from ChatGPT.", 400, headers=HEADERS
        )
    if request.method == "GET":
        target = urlsplit(str(params.redirect_uri))
        policy = HEADERS["Content-Security-Policy"].replace(
            "form-action 'self'",
            f"form-action 'self' {target.scheme}://{target.netloc}",
        )
        return HTMLResponse(
            FORM, headers={**HEADERS, "Content-Security-Policy": policy}
        )
    if request.headers.get("origin") != accounts.origin:
        return Response(status_code=403, headers=HEADERS)
    key = await submitted_key(request)
    try:
        async with AsyncFMPDataClient(api_key=key, max_retries=1) as client:
            await client.company.get_simple_quote("AAPL")
    except AuthenticationError:
        return PlainTextResponse(
            "FMP rejected this key. Check your FMP account and try again.",
            400,
            headers=HEADERS,
        )
    except FMPError:
        return PlainTextResponse(
            "FMP could not verify quote access. Check your plan and try again.",
            503,
            headers=HEADERS,
        )
    callback = construct_redirect_uri(
        str(params.redirect_uri),
        code=accounts.issue_code(params, key),
        state=params.state,
    )
    response = RedirectResponse(
        callback,
        status_code=303,
        headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
    )
    response.delete_cookie(
        cookie_name(accounts.origin),
        path="/",
        secure=accounts.origin.startswith("https://"),
        httponly=True,
    )
    return response
