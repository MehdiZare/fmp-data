"""Store encrypted FMP connections and implement the MCP SDK's OAuth provider."""

from collections.abc import Iterator
from contextlib import closing, contextmanager
import hashlib
import os
from pathlib import Path
import secrets
import sqlite3
import time
from urllib.parse import urlsplit

from cryptography.fernet import Fernet
from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    AuthorizeError,
    OAuthAuthorizationServerProvider,
    RefreshToken,
    TokenError,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from pydantic import AnyHttpUrl

SCOPE = "market:read"
CLIENT_AUTH_METHOD = "client_secret_post"
ACCESS_SECONDS = 3600
CONNECTION_SECONDS = 30 * 86400


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


class Accounts(
    OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]
):
    """One registered ChatGPT client, one independent grant per connection."""

    def __init__(self) -> None:
        self.origin = str(AnyHttpUrl(os.environ["FMP_PLUGIN_ORIGIN"])).rstrip("/")
        url = urlsplit(self.origin)
        if url.path or url.query or url.fragment or url.username or url.password:
            raise ValueError("FMP_PLUGIN_ORIGIN must be an origin")
        if url.scheme != "https" and url.hostname not in {"localhost", "127.0.0.1"}:
            raise ValueError("Public origins require HTTPS")
        self.resource = self.origin + "/mcp"
        callback = AnyHttpUrl(os.environ["FMP_PLUGIN_REDIRECT_URI"])
        if callback.scheme != "https":
            raise ValueError("Register the exact HTTPS callback shown by ChatGPT")
        secret = os.environ["FMP_PLUGIN_CLIENT_SECRET"]
        if len(secret) < 32:
            raise ValueError(
                "Use a randomly generated client secret of at least 32 characters"
            )
        self.client = OAuthClientInformationFull(
            client_id="fmp-data-chatgpt",
            client_secret=secret,
            redirect_uris=[str(callback)],
            token_endpoint_auth_method=CLIENT_AUTH_METHOD,
            scope=SCOPE,
        )
        self.cipher = Fernet(os.environ["FMP_PLUGIN_ENCRYPTION_KEY"])
        self.path = Path(os.environ["FMP_PLUGIN_DATABASE"])
        with self.database() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS grants (
                subject TEXT PRIMARY KEY, encrypted_key BLOB NOT NULL,
                code_hash TEXT UNIQUE, params TEXT, access_hash TEXT UNIQUE,
                refresh_hash TEXT UNIQUE, access_until INTEGER,
                valid_until INTEGER NOT NULL
            )""")

    @contextmanager
    def database(self) -> Iterator[sqlite3.Connection]:
        with closing(sqlite3.connect(self.path)) as db, db:
            db.row_factory = sqlite3.Row
            yield db

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        return self.client if client_id == self.client.client_id else None

    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        if params.resource not in (None, self.resource):
            raise AuthorizeError("invalid_target", "Unknown MCP resource")
        if params.scopes is not None and params.scopes != [SCOPE]:
            raise AuthorizeError("invalid_scope", "Request the market:read scope")
        # The browser middleware moves this sealed request to an HttpOnly cookie.
        return (
            "/connect#"
            + self.cipher.encrypt(params.model_dump_json().encode()).decode()
        )

    def issue_code(self, params: AuthorizationParams, key: str) -> str:
        code = secrets.token_urlsafe(32)
        now = int(time.time())
        with self.database() as db:
            db.execute("DELETE FROM grants WHERE valid_until <= ?", (now,))
            db.execute(
                """INSERT INTO grants
                (subject, encrypted_key, code_hash, params, valid_until)
                VALUES (?, ?, ?, ?, ?)""",
                (
                    secrets.token_urlsafe(24),
                    self.cipher.encrypt(key.encode()),
                    digest(code),
                    params.model_dump_json(),
                    now + 300,
                ),
            )
        return code

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AuthorizationCode | None:
        with self.database() as db:
            row = db.execute(
                "SELECT * FROM grants WHERE code_hash=? AND valid_until>?",
                (digest(authorization_code), time.time()),
            ).fetchone()
        if not row or client.client_id != self.client.client_id:
            return None
        params = AuthorizationParams.model_validate_json(row["params"])
        return AuthorizationCode(
            code=authorization_code,
            scopes=[SCOPE],
            expires_at=row["valid_until"],
            client_id=client.client_id,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=self.resource,
            subject=row["subject"],
        )

    def _rotate(
        self, subject: str | None, code: str | None, refresh: str | None
    ) -> OAuthToken:
        access, renewed = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        now = int(time.time())
        with self.database() as db:
            updated = db.execute(
                """UPDATE grants SET access_hash=?, refresh_hash=?,
                code_hash=NULL, params=NULL, access_until=?, valid_until=?
                WHERE subject=? AND valid_until>?
                AND (code_hash=? OR refresh_hash=?)""",
                (
                    digest(access),
                    digest(renewed),
                    now + ACCESS_SECONDS,
                    now + CONNECTION_SECONDS,
                    subject,
                    now,
                    code,
                    refresh,
                ),
            )
            if updated.rowcount != 1:
                raise TokenError(
                    "invalid_grant", "Connection expired or already exchanged"
                )
        return OAuthToken(
            access_token=access,
            refresh_token=renewed,
            scope=SCOPE,
            expires_in=ACCESS_SECONDS,
        )

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        return self._rotate(
            authorization_code.subject, digest(authorization_code.code), None
        )

    async def load_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: str
    ) -> RefreshToken | None:
        with self.database() as db:
            row = db.execute(
                "SELECT subject,valid_until FROM grants "
                "WHERE refresh_hash=? AND valid_until>?",
                (digest(refresh_token), time.time()),
            ).fetchone()
        if not row or client.client_id != self.client.client_id:
            return None
        return RefreshToken(
            token=refresh_token,
            scopes=[SCOPE],
            client_id=client.client_id,
            expires_at=row["valid_until"],
            resource=self.resource,
            subject=row["subject"],
        )

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        return self._rotate(refresh_token.subject, None, digest(refresh_token.token))

    async def load_access_token(self, token: str) -> AccessToken | None:
        with self.database() as db:
            row = db.execute(
                "SELECT subject,access_until FROM grants "
                "WHERE access_hash=? AND access_until>?",
                (digest(token), time.time()),
            ).fetchone()
        if not row:
            return None
        return AccessToken(
            token=token,
            scopes=[SCOPE],
            client_id=self.client.client_id,
            resource=self.resource,
            expires_at=row["access_until"],
            subject=row["subject"],
        )

    def key_for(self, access_token: str) -> str | None:
        with self.database() as db:
            row = db.execute(
                "SELECT encrypted_key FROM grants "
                "WHERE access_hash=? AND access_until>?",
                (digest(access_token), time.time()),
            ).fetchone()
        return self.cipher.decrypt(row["encrypted_key"]).decode() if row else None

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        hashed = digest(token.token)
        with self.database() as db:
            db.execute(
                "DELETE FROM grants WHERE access_hash=? OR refresh_hash=?",
                (hashed, hashed),
            )
