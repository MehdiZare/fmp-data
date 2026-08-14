"""Unit tests for the Redis cache backend.

The ``redis`` package is an optional extra, so these tests install a stub
``redis`` module into ``sys.modules`` instead of importing the real client.
That keeps the suite runnable with or without ``fmp-data[cache-redis]`` and
guarantees no socket is ever opened.
"""

from __future__ import annotations

from datetime import datetime
import json
import logging
import sys
import threading
from types import ModuleType
from typing import Any

import pytest

from fmp_data.cache.redis_backend import RedisCache

LOGGER_NAME = "fmp_data.cache.redis_backend"


class FakeRedis:
    """In-process stand-in for ``redis.Redis`` that records every call.

    Set ``fail_on`` to make an operation raise, and ``scan_pages`` to script
    the SCAN cursor loop as a list of ``(next_cursor, keys)`` pages.
    """

    def __init__(self) -> None:
        self.store: dict[str, str] = {}
        self.get_calls: list[str] = []
        self.setex_calls: list[tuple[str, int, str]] = []
        self.delete_calls: list[tuple[str, ...]] = []
        self.scan_calls: list[tuple[int, str | None, int | None]] = []
        self.call_threads: list[int] = []
        self.fail_on: set[str] = set()
        self.scan_pages: list[tuple[int, list[str]]] = [(0, [])]

    def _guard(self, operation: str) -> None:
        self.call_threads.append(threading.get_ident())
        if operation in self.fail_on:
            raise RuntimeError(f"redis {operation} unavailable")

    def get(self, key: str) -> str | None:
        self.get_calls.append(key)
        self._guard("get")
        return self.store.get(key)

    def setex(self, key: str, ttl: int, value: str) -> None:
        self.setex_calls.append((key, ttl, value))
        self._guard("setex")
        self.store[key] = value

    def delete(self, *keys: str) -> int:
        self.delete_calls.append(keys)
        self._guard("delete")
        return sum(self.store.pop(key, None) is not None for key in keys)

    def scan(
        self,
        cursor: int,
        match: str | None = None,
        count: int | None = None,
    ) -> tuple[int, list[str]]:
        self.scan_calls.append((cursor, match, count))
        self._guard("scan")
        if not self.scan_pages:
            return 0, []
        return self.scan_pages.pop(0)


class FakeRedisModule(ModuleType):
    """Stub ``redis`` module whose ``from_url`` hands back a `FakeRedis`."""

    def __init__(self) -> None:
        super().__init__("redis")
        self.from_url_calls: list[tuple[str, dict[str, Any]]] = []
        self.client = FakeRedis()

    def from_url(self, url: str, **kwargs: Any) -> FakeRedis:
        self.from_url_calls.append((url, kwargs))
        return self.client


@pytest.fixture
def redis_stub(monkeypatch: pytest.MonkeyPatch) -> FakeRedisModule:
    """Install the stub ``redis`` module for the duration of one test."""
    stub = FakeRedisModule()
    monkeypatch.setitem(sys.modules, "redis", stub)
    return stub


class TestRedisCacheInit:
    """Construction, dependency check and constructor defaults."""

    def test_missing_redis_package_raises_import_error_with_extra_hint(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # ``None`` in sys.modules makes ``import redis`` raise ImportError.
        monkeypatch.setitem(sys.modules, "redis", None)

        with pytest.raises(ImportError) as exc_info:
            RedisCache()

        message = str(exc_info.value)
        assert "'redis' package" in message
        assert "pip install 'fmp-data[cache-redis]'" in message
        assert isinstance(exc_info.value.__cause__, ImportError)

    def test_from_url_receives_url_and_decode_responses(
        self, redis_stub: FakeRedisModule
    ) -> None:
        RedisCache(redis_url="redis://cache.internal:6380/2")

        assert redis_stub.from_url_calls == [
            ("redis://cache.internal:6380/2", {"decode_responses": True})
        ]

    def test_default_url(self, redis_stub: FakeRedisModule) -> None:
        RedisCache()

        assert redis_stub.from_url_calls[0][0] == "redis://localhost:6379/0"

    def test_default_ttl_is_300_seconds(self, redis_stub: FakeRedisModule) -> None:
        cache = RedisCache()

        cache.set("quote", {"symbol": "AAPL"})

        assert redis_stub.client.setex_calls[0][1] == 300

    def test_default_key_prefix_is_fmp(self, redis_stub: FakeRedisModule) -> None:
        cache = RedisCache()

        cache.get("quote")

        assert redis_stub.client.get_calls == ["fmp:quote"]

    def test_custom_prefix_applies_to_every_operation(
        self, redis_stub: FakeRedisModule
    ) -> None:
        cache = RedisCache(key_prefix="tenant7:", default_ttl=42)
        client = redis_stub.client
        client.scan_pages = [(0, [])]

        cache.get("quote")
        cache.set("quote", 1)
        cache.delete("quote")
        cache.clear()

        assert client.get_calls == ["tenant7:quote"]
        assert client.setex_calls == [("tenant7:quote", 42, "1")]
        assert client.delete_calls == [("tenant7:quote",)]
        assert client.scan_calls == [(0, "tenant7:*", 100)]


class TestRedisCacheGet:
    """Reads: hits, misses, corrupt payloads and client failures."""

    def test_hit_returns_parsed_json(self, redis_stub: FakeRedisModule) -> None:
        cache = RedisCache()
        redis_stub.client.store["fmp:quotes"] = json.dumps(
            [{"symbol": "AAPL", "price": 150.0}]
        )

        assert cache.get("quotes") == [{"symbol": "AAPL", "price": 150.0}]

    def test_round_trip_through_the_client(self, redis_stub: FakeRedisModule) -> None:
        cache = RedisCache()

        cache.set("profile", {"symbol": "MSFT", "employees": 221000})

        assert cache.get("profile") == {"symbol": "MSFT", "employees": 221000}

    def test_miss_returns_none(self, redis_stub: FakeRedisModule) -> None:
        cache = RedisCache()

        assert cache.get("absent") is None
        assert redis_stub.client.get_calls == ["fmp:absent"]

    def test_malformed_json_returns_none(self, redis_stub: FakeRedisModule) -> None:
        cache = RedisCache()
        redis_stub.client.store["fmp:corrupt"] = "{not valid json"

        assert cache.get("corrupt") is None

    def test_json_null_is_indistinguishable_from_a_miss(
        self, redis_stub: FakeRedisModule
    ) -> None:
        """Current behaviour: a cached ``None`` reads back as a miss."""
        cache = RedisCache()
        cache.set("empty", None)

        assert redis_stub.client.store["fmp:empty"] == "null"
        assert cache.get("empty") is None

    def test_client_error_returns_none_and_logs_key_only(
        self, redis_stub: FakeRedisModule, caplog: pytest.LogCaptureFixture
    ) -> None:
        cache = RedisCache()
        redis_stub.client.store["fmp:user:42:portfolio"] = json.dumps("classified")
        redis_stub.client.fail_on.add("get")

        with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
            result = cache.get("user:42:portfolio")

        assert result is None
        records = [r for r in caplog.records if r.name == LOGGER_NAME]
        assert len(records) == 1
        assert records[0].levelno == logging.WARNING
        assert records[0].getMessage() == "Redis get error for key user:42:portfolio"
        assert records[0].exc_info is not None
        assert records[0].exc_info[0] is RuntimeError
        assert "classified" not in caplog.text


class TestRedisCacheSet:
    """Writes: TTL selection, serialization and swallowed failures."""

    def test_default_ttl_used_when_ttl_omitted(
        self, redis_stub: FakeRedisModule
    ) -> None:
        cache = RedisCache(default_ttl=600)

        cache.set("quote", {"symbol": "AAPL"})

        assert redis_stub.client.setex_calls == [
            ("fmp:quote", 600, '{"symbol": "AAPL"}')
        ]

    def test_explicit_ttl_overrides_default(self, redis_stub: FakeRedisModule) -> None:
        cache = RedisCache(default_ttl=600)

        cache.set("quote", "v", ttl=15)

        assert redis_stub.client.setex_calls == [("fmp:quote", 15, '"v"')]

    def test_zero_ttl_is_forwarded_verbatim(self, redis_stub: FakeRedisModule) -> None:
        """``ttl=0`` is not treated as "unset" -- it reaches SETEX as 0."""
        cache = RedisCache(default_ttl=600)

        cache.set("quote", "v", ttl=0)

        assert redis_stub.client.setex_calls == [("fmp:quote", 0, '"v"')]

    def test_non_serializable_value_falls_back_to_str(
        self, redis_stub: FakeRedisModule
    ) -> None:
        cache = RedisCache()
        moment = datetime(2026, 8, 13, 9, 30)

        cache.set("asof", {"timestamp": moment})

        stored = redis_stub.client.setex_calls[0][2]
        assert json.loads(stored) == {"timestamp": "2026-08-13 09:30:00"}

    def test_client_error_is_swallowed_and_logged_without_value(
        self, redis_stub: FakeRedisModule, caplog: pytest.LogCaptureFixture
    ) -> None:
        cache = RedisCache()
        client = redis_stub.client
        client.fail_on.add("setex")

        with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
            cache.set("user:42:portfolio", "top-holding-plaintext")

        # The write was attempted, and its failure left no entry behind.
        assert client.setex_calls == [
            ("fmp:user:42:portfolio", 300, '"top-holding-plaintext"')
        ]
        assert client.store == {}
        records = [r for r in caplog.records if r.name == LOGGER_NAME]
        assert len(records) == 1
        assert records[0].levelno == logging.WARNING
        assert records[0].getMessage() == "Redis set error for key user:42:portfolio"
        # exc_info keeps the traceback; without it the log line is undebuggable.
        assert records[0].exc_info is not None
        assert records[0].exc_info[0] is RuntimeError
        assert "top-holding-plaintext" not in caplog.text


class TestRedisCacheDelete:
    """Deletes: key prefixing and swallowed failures."""

    def test_deletes_prefixed_key(self, redis_stub: FakeRedisModule) -> None:
        cache = RedisCache()
        cache.set("quote", "v")

        cache.delete("quote")

        assert redis_stub.client.delete_calls == [("fmp:quote",)]
        assert cache.get("quote") is None

    def test_client_error_is_swallowed_and_logged(
        self, redis_stub: FakeRedisModule, caplog: pytest.LogCaptureFixture
    ) -> None:
        cache = RedisCache()
        client = redis_stub.client
        cache.set("quote", "v")
        client.fail_on.add("delete")

        with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
            cache.delete("quote")

        # The delete was attempted and the entry survives the failure.
        assert client.delete_calls == [("fmp:quote",)]
        assert client.store == {"fmp:quote": '"v"'}
        records = [r for r in caplog.records if r.name == LOGGER_NAME]
        assert len(records) == 1
        assert records[0].levelno == logging.WARNING
        assert records[0].getMessage() == "Redis delete error for key quote"
        assert records[0].exc_info is not None
        assert records[0].exc_info[0] is RuntimeError


class TestRedisCacheClear:
    """The SCAN cursor loop."""

    def test_iterates_every_scan_page_and_deletes_each_batch(
        self, redis_stub: FakeRedisModule
    ) -> None:
        cache = RedisCache()
        client = redis_stub.client
        client.scan_pages = [
            (17, ["fmp:a", "fmp:b"]),
            (0, ["fmp:c"]),
        ]

        cache.clear()

        assert client.scan_calls == [(0, "fmp:*", 100), (17, "fmp:*", 100)]
        assert client.delete_calls == [("fmp:a", "fmp:b"), ("fmp:c",)]

    def test_glob_metacharacters_in_prefix_are_not_escaped(
        self, redis_stub: FakeRedisModule
    ) -> None:
        """Current behaviour: the prefix is concatenated into the SCAN
        pattern verbatim, so glob metacharacters change what is matched.
        """
        cache = RedisCache(key_prefix="fmp[1]:")
        client = redis_stub.client
        client.scan_pages = [(0, [])]

        cache.set("quote", "v")
        cache.clear()

        assert client.setex_calls[0][0] == "fmp[1]:quote"
        assert client.scan_calls == [(0, "fmp[1]:*", 100)]

    def test_empty_page_does_not_call_delete(self, redis_stub: FakeRedisModule) -> None:
        cache = RedisCache()
        client = redis_stub.client
        client.scan_pages = [(9, []), (0, ["fmp:only"])]

        cache.clear()

        assert client.scan_calls == [(0, "fmp:*", 100), (9, "fmp:*", 100)]
        assert client.delete_calls == [("fmp:only",)]

    def test_single_empty_page_ends_the_loop_after_one_scan(
        self, redis_stub: FakeRedisModule
    ) -> None:
        """A cursor of 0 on the first page terminates -- no re-SCAN, no DELETE."""
        cache = RedisCache()
        client = redis_stub.client
        client.scan_pages = [(0, [])]

        cache.clear()

        assert client.scan_calls == [(0, "fmp:*", 100)]
        assert client.delete_calls == []

    def test_clear_removes_entries_from_the_backing_store(
        self, redis_stub: FakeRedisModule
    ) -> None:
        cache = RedisCache()
        client = redis_stub.client
        cache.set("a", 1)
        cache.set("b", 2)
        client.scan_pages = [(0, list(client.store))]

        cache.clear()

        assert client.store == {}
        assert cache.get("a") is None

    def test_scan_error_is_swallowed_and_logged(
        self, redis_stub: FakeRedisModule, caplog: pytest.LogCaptureFixture
    ) -> None:
        cache = RedisCache()
        client = redis_stub.client
        cache.set("survivor", "v")
        client.fail_on.add("scan")

        with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
            cache.clear()

        # A failed SCAN aborts before deleting anything.
        assert client.delete_calls == []
        assert client.store == {"fmp:survivor": '"v"'}
        records = [r for r in caplog.records if r.name == LOGGER_NAME]
        assert len(records) == 1
        assert records[0].levelno == logging.WARNING
        assert records[0].getMessage() == "Redis clear error"
        assert records[0].exc_info is not None
        assert records[0].exc_info[0] is RuntimeError

    def test_delete_error_mid_loop_aborts_without_raising(
        self, redis_stub: FakeRedisModule, caplog: pytest.LogCaptureFixture
    ) -> None:
        cache = RedisCache()
        client = redis_stub.client
        client.scan_pages = [(5, ["fmp:a"]), (0, ["fmp:b"])]
        client.fail_on.add("delete")

        with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
            cache.clear()

        assert client.delete_calls == [("fmp:a",)]
        assert client.scan_calls == [(0, "fmp:*", 100)]
        records = [r for r in caplog.records if r.name == LOGGER_NAME]
        assert [r.getMessage() for r in records] == ["Redis clear error"]


class TestRedisCacheAsync:
    """The inherited async wrappers drive the same client."""

    @pytest.mark.asyncio
    async def test_aset_then_aget_round_trip(self, redis_stub: FakeRedisModule) -> None:
        cache = RedisCache(default_ttl=30)

        await cache.aset("quote", {"symbol": "AAPL"})

        assert redis_stub.client.setex_calls == [
            ("fmp:quote", 30, '{"symbol": "AAPL"}')
        ]
        assert await cache.aget("quote") == {"symbol": "AAPL"}

    @pytest.mark.asyncio
    async def test_blocking_client_calls_run_off_the_event_loop_thread(
        self, redis_stub: FakeRedisModule
    ) -> None:
        """``redis-py`` is synchronous, so the wrappers must offload it.

        Without this the coroutines would block the loop on every network
        round trip -- and a plain ``await`` on a direct call still satisfies a
        round-trip assertion, so pin the thread hand-off explicitly.
        """
        cache = RedisCache()

        await cache.aset("quote", "v")
        await cache.aget("quote")
        await cache.adelete("quote")
        await cache.aclear()

        loop_thread = threading.get_ident()
        assert redis_stub.client.call_threads, "no client call was recorded"
        assert loop_thread not in redis_stub.client.call_threads
