"""Credential config fields survive serialization without leaking (#252).

``repr`` and ``str`` were redacted by hand long before this, but
``model_dump()`` and ``model_dump_json()`` returned every credential in
cleartext — so anything that serialized a config (structured logging, a JSON
error report, a config endpoint) leaked the key while the eyeball-level checks
all looked clean.

Hand-written ``__repr__``/``__str__`` cannot close that: a third party calling
``model_dump()`` never goes through them. Typing the fields ``SecretStr`` moves
the guarantee into pydantic, where every serialization path inherits it.

These tests drive all four models over every escape route, and pin the two
properties that make the migration safe rather than merely quiet:

* the real value still reaches the wire (a missed ``.get_secret_value()``
  fails *silently* — httpx stringifies a ``SecretStr`` to its mask);
* a python-mode dump still round-trips, because ``LangChainConfig.from_env``
  rebuilds itself through one.
"""

from __future__ import annotations

import json

import httpx
import pytest

from fmp_data.cache.config import CacheConfig
from fmp_data.config import ClientConfig

API_KEY = "SUPERSECRETKEY123456"  # pragma: allowlist secret
REDIS_PASSWORD = "hunter2"  # noqa: S105  # pragma: allowlist secret
REDIS_URL = f"redis://:{REDIS_PASSWORD}@localhost:6379/0"


@pytest.fixture
def config() -> ClientConfig:
    return ClientConfig(
        api_key=API_KEY,
        cache=CacheConfig(backend="redis", redis_url=REDIS_URL),
    )


def _renderings(model: object) -> dict[str, str]:
    """Every way a caller can turn a model into text."""
    return {
        "repr": repr(model),
        "str": str(model),
        "model_dump": str(model.model_dump()),  # type: ignore[attr-defined]
        "model_dump(mode=json)": str(model.model_dump(mode="json")),  # type: ignore[attr-defined]
        "model_dump_json": model.model_dump_json(),  # type: ignore[attr-defined]
    }


def test_client_config_never_renders_the_api_key(config: ClientConfig) -> None:
    for label, text in _renderings(config).items():
        assert API_KEY not in text, f"api_key leaked via {label}: {text[:200]}"


def test_client_config_never_renders_nested_redis_credentials(
    config: ClientConfig,
) -> None:
    for label, text in _renderings(config).items():
        assert REDIS_PASSWORD not in text, f"redis userinfo leaked via {label}"


def test_cache_config_never_renders_redis_credentials() -> None:
    cache = CacheConfig(backend="redis", redis_url=REDIS_URL)
    for label, text in _renderings(cache).items():
        assert REDIS_PASSWORD not in text, f"redis userinfo leaked via {label}"


def test_str_keeps_the_leading_characters_of_the_key(config: ClientConfig) -> None:
    """The mask is still useful for telling two keys apart.

    ``__str__`` derives it from the *field*, not from ``model_dump()`` — the
    dump is already masked, and masking a mask would print ``'*******'`` for
    every key alike.
    """
    assert f"api_key='{API_KEY[:4]}***'" in str(config)


def test_cache_str_still_shows_the_host() -> None:
    """Only the userinfo is secret; the host is why this string is printed."""
    text = str(CacheConfig(backend="redis", redis_url=REDIS_URL))
    assert REDIS_PASSWORD not in text
    assert "localhost:6379" in text


def test_the_real_key_reaches_the_wire(config: ClientConfig) -> None:
    """The silent-failure guard.

    ``httpx`` accepts a ``SecretStr`` query param and stringifies it, so a
    missed ``.get_secret_value()`` sends ``apikey=**********`` and 401s with
    no local error. Assert the literal value rather than comparing against
    the config field, which would match vacuously once both sides are masked.
    """
    request = httpx.Request(
        "GET",
        "https://financialmodelingprep.com/stable/profile",
        params={"apikey": config.api_key.get_secret_value(), "symbol": "AAPL"},
    )
    assert f"apikey={API_KEY}" in str(request.url)
    assert "%2A" not in str(request.url)


def test_python_mode_dump_round_trips(config: ClientConfig) -> None:
    """``LangChainConfig.from_env`` rebuilds itself through this exact path."""
    rebuilt = ClientConfig(**config.model_dump())
    assert rebuilt.api_key.get_secret_value() == API_KEY
    assert rebuilt.cache is not None
    assert rebuilt.cache.redis_url is not None
    assert rebuilt.cache.redis_url.get_secret_value() == REDIS_URL


def test_json_mode_round_trip_is_refused_rather_than_silently_wrong(
    config: ClientConfig,
) -> None:
    """A masked dump must not validate back into a working-looking config.

    ``mode="json"`` is the natural reflex, since ``SecretStr`` is not
    JSON-serialisable — and it substitutes the literal mask. Accepting
    ``'**********'`` as a key yields a client that 401s on every call with
    nothing to point at locally, so it is rejected at construction.
    """
    with pytest.raises(ValueError, match="redaction mask"):
        ClientConfig(**json.loads(config.model_dump_json()))


def test_plain_strings_are_still_accepted_at_construction() -> None:
    """Callers passing a `str` keep working; only *reads* changed."""
    assert ClientConfig(api_key=API_KEY).api_key.get_secret_value() == API_KEY


def test_whitespace_is_still_stripped() -> None:
    """`str_strip_whitespace` does not reach inside a SecretStr."""
    assert ClientConfig(api_key=f"  {API_KEY}  ").api_key.get_secret_value() == API_KEY


@pytest.mark.parametrize("value", ["", "   "])
def test_empty_keys_are_still_rejected(value: str) -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        ClientConfig(api_key=value)


def test_truthiness_still_works_for_the_client_guards() -> None:
    """`fmp_data/client.py` and `async_client.py` test `not config.api_key`."""
    from pydantic import SecretStr

    assert not SecretStr("")
    assert SecretStr("x")


class TestDisplayRedactionIsNotANameAllowlist:
    """`__str__` must not depend on a hard-coded list of field names (#252).

    The previous version dumped the whole model and masked the three names it
    knew about (`api_key`, `embedding_api_key`, `cache.redis_url`). Anything
    else rendered verbatim -- and `LogHandlerConfig.handler_kwargs` is a bare
    `dict[str, Any]` handed straight to a logging handler, so no subclass was
    needed to reach it.
    """

    @staticmethod
    def _with_handler_kwargs(**kwargs: object) -> ClientConfig:
        from fmp_data.config import LoggingConfig, LogHandlerConfig

        return ClientConfig(
            api_key=API_KEY,
            logging=LoggingConfig(
                handlers={
                    "remote": LogHandlerConfig(
                        class_name="StreamHandler", handler_kwargs=dict(kwargs)
                    )
                }
            ),
        )

    def test_secret_in_untyped_handler_kwargs(self) -> None:
        planted = "LOGHANDLERSECRET_bbbbbbbb"
        config = self._with_handler_kwargs(credentials=("user", planted))
        assert planted not in str(config)
        assert planted not in repr(config)

    def test_secret_nested_deeper_in_handler_kwargs(self) -> None:
        """A top-level-only scan copies nested containers by reference."""
        planted = "DEEPSECRET_cccccccc"
        config = self._with_handler_kwargs(outer={"inner": {"api_key": planted}})
        assert planted not in str(config)

    def test_camel_case_key_is_recognised(self) -> None:
        planted = "CAMELSECRET_dddddddd"
        config = self._with_handler_kwargs(refreshToken=planted)
        assert planted not in str(config)

    def test_subclass_credential_field(self) -> None:
        """A subclass must not have to edit `ClientConfig.__str__`."""
        planted = "SUBCLASS_SECRET_gggggggg"

        class WebhookConfig(ClientConfig):
            webhook_secret: str | None = None

        config = WebhookConfig(api_key=API_KEY, webhook_secret=planted)
        assert planted not in str(config)
        assert planted not in repr(config)

    def test_repr_false_is_honoured_even_without_a_secret_shaped_name(self) -> None:
        """`repr=False` is pydantic's own not-for-display marker."""
        from pydantic import Field

        planted = "OPAQUE_dddddddd"

        class OpaqueConfig(ClientConfig):
            internal_note: str | None = Field(default=None, repr=False)

        config = OpaqueConfig(api_key=API_KEY, internal_note=planted)
        assert planted not in str(config)

    def test_non_secret_values_are_still_shown(self) -> None:
        """Over-redaction would make this string useless for debugging."""
        config = self._with_handler_kwargs(maxBytes=1048576, backupCount=3)
        text = str(config)
        assert "maxBytes" in text
        assert "1048576" in text
        assert "backupCount" in text
        assert "base_url=" in text


class TestHandlerKwargsOnTheDumpPath:
    """`handler_kwargs` is out of `SecretStr`'s reach (#252).

    It is a bare `dict[str, Any]` handed straight to a logging handler --
    a `SysLogHandler` password or an HTTP handler's credentials live here.
    `__str__` was swept, but `model_dump()` still emitted them.
    """

    PLANTED = "PLANTEDHANDLERSECRET"

    def _config(self) -> ClientConfig:
        from fmp_data.config import LoggingConfig, LogHandlerConfig

        return ClientConfig(
            api_key=API_KEY,
            logging=LoggingConfig(
                handlers={
                    "file": LogHandlerConfig(
                        class_name="RotatingFileHandler",
                        handler_kwargs={
                            "password": self.PLANTED,
                            "maxBytes": 1048576,
                            "backupCount": 3,
                        },
                    )
                }
            ),
        )

    def test_model_dump_does_not_leak(self) -> None:
        assert self.PLANTED not in str(self._config().model_dump())

    def test_model_dump_json_does_not_leak(self) -> None:
        assert self.PLANTED not in self._config().model_dump_json()

    def test_the_live_value_is_untouched(self) -> None:
        """`logger.py` splats these into the handler constructor."""
        config = self._config()
        config.model_dump()  # must not mutate
        kwargs = config.logging.handlers["file"].handler_kwargs
        assert kwargs["password"] == self.PLANTED

    def test_operational_kwargs_survive(self) -> None:
        dumped = self._config().model_dump()
        kwargs = dumped["logging"]["handlers"]["file"]["handler_kwargs"]
        assert kwargs["maxBytes"] == 1048576
        assert kwargs["backupCount"] == 3
