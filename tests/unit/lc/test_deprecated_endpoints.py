"""Deprecated endpoints are not selectable through the vector store (#137).

Three intelligence endpoints return ``[]`` without calling upstream. They stayed
indexed, so a semantic query could pick one and the LLM got an empty success --
indistinguishable from "no data for your query".

``EndpointSemantics.deprecated`` marks them, and ``EndpointVectorStore`` filters
on it at index time *and* at selection time. The entries are not deleted: their
tool keys stay resolvable for anyone loading them through an explicit MCP
manifest, and the MCP catalog count does not move.

This module holds the half of #137 that genuinely needs the ``langchain`` extra:
the store's filtering behaviour. Which endpoints carry the flag is pinned in
``tests/unit/test_deprecated_endpoint_flags.py`` and the MCP side of the
contract in ``tests/unit/test_mcp.py``, both of which run in CI jobs this
directory is skipped in.
"""

from __future__ import annotations

from typing import Any

import pytest


class _StubRegistry:
    """Minimal registry stand-in: name -> object with ``.semantics``."""

    def __init__(self, entries: dict[str, Any]) -> None:
        self._entries = entries

    def get_endpoint(self, name: str) -> Any:
        return self._entries.get(name)

    def get_embedding_text(self, name: str) -> str:
        return f"text for {name}"

    def list_endpoints(self) -> dict[str, Any]:
        return dict(self._entries)


class _StubInfo:
    def __init__(self, semantics: Any) -> None:
        self.semantics = semantics


class _Semantics:
    def __init__(self, deprecated: bool) -> None:
        self.deprecated = deprecated


@pytest.fixture
def store(monkeypatch: pytest.MonkeyPatch) -> Any:
    """An ``EndpointVectorStore`` with its backing store and IO stubbed out."""
    from fmp_data.lc.vector_store import EndpointVectorStore

    entries = {
        "live_one": _StubInfo(_Semantics(deprecated=False)),
        "live_two": _StubInfo(_Semantics(deprecated=False)),
        "dead_one": _StubInfo(_Semantics(deprecated=True)),
    }

    # Typed ``Any``: the attributes below are deliberately stubs, and the
    # per-line ignores they would otherwise need are reported as unused in
    # the core-only mypy env, where ``EndpointVectorStore`` is not importable.
    instance: Any = EndpointVectorStore.__new__(EndpointVectorStore)
    instance.registry = _StubRegistry(entries)

    from fmp_data.logger import FMPLogger

    instance.logger = FMPLogger().get_logger(__name__)

    class _Backing:
        def __init__(self) -> None:
            self.added: list[Any] = []

        def add_documents(self, documents: list[Any]) -> None:
            self.added.extend(documents)

        def similarity_search(self, _query: str, k: int = 10) -> list[Any]:
            return list(self.added)

        def similarity_search_with_score(
            self, _query: str, k: int = 10
        ) -> list[tuple[Any, float]]:
            # Score 0.0 -> similarity 1.0, so nothing is lost to the
            # threshold and the deprecation filter is what is under test.
            return [(doc, 0.0) for doc in self.added]

    instance.vector_store = _Backing()
    instance.created_tools = []

    monkeypatch.setattr(
        EndpointVectorStore,
        "create_tool",
        lambda self, info: info,
    )
    return instance


def test_add_endpoints_skips_deprecated(store: Any) -> None:
    store.add_endpoints(["live_one", "live_two", "dead_one"])

    indexed = {doc.metadata["endpoint"] for doc in store.vector_store.added}
    assert indexed == {"live_one", "live_two"}


def test_add_endpoint_skips_deprecated(store: Any) -> None:
    store.add_endpoint("dead_one")
    assert not store.vector_store.added

    store.add_endpoint("live_one")
    assert [doc.metadata["endpoint"] for doc in store.vector_store.added] == [
        "live_one"
    ]


def test_add_endpoints_raises_when_every_name_is_deprecated(store: Any) -> None:
    """Silently producing an empty store would be worse than failing."""
    with pytest.raises(RuntimeError):
        store.add_endpoints(["dead_one"])


def test_get_tools_filters_deprecated_from_a_stale_index(store: Any) -> None:
    """Selection-time filtering, so a cached store built before this still works.

    A vector store persisted by an older release has the deprecated endpoints
    baked into its index. Filtering only at ``add_endpoints`` would leave those
    users exactly where #137 found them.
    """
    from langchain_core.documents import Document

    store.vector_store.add_documents(
        [
            Document(page_content="stale", metadata={"endpoint": name})
            for name in ("live_one", "dead_one")
        ]
    )

    tools = store.get_tools()

    assert all(not tool.semantics.deprecated for tool in tools)
    assert len(tools) == 1


@pytest.fixture
def real_store(monkeypatch: pytest.MonkeyPatch) -> Any:
    """A store over the REAL registry, so ``SearchResult`` validation applies.

    ``SearchResult.info`` is typed ``EndpointInfo``, so the stub registry used
    by the fixture above cannot reach ``search`` -- pydantic rejects the stub
    before the deprecation filter is ever exercised.
    """
    from fmp_data.lc.registry import EndpointRegistry
    from fmp_data.lc.vector_store import EndpointVectorStore
    from fmp_data.logger import FMPLogger

    registry = EndpointRegistry()
    from fmp_data.intelligence.endpoints import (
        EARNINGS_CONFIRMED,
        STOCK_NEWS_SENTIMENTS_ENDPOINT,
    )
    from fmp_data.intelligence.mapping import INTELLIGENCE_ENDPOINTS_SEMANTICS
    from fmp_data.market.endpoints import GAINERS, MARKET_HOURS
    from fmp_data.market.mapping import MARKET_ENDPOINTS_SEMANTICS

    registry.register(
        "get_stock_news_sentiments",
        STOCK_NEWS_SENTIMENTS_ENDPOINT,
        INTELLIGENCE_ENDPOINTS_SEMANTICS["stock_news_sentiments"],
    )
    registry.register(
        "get_earnings_confirmed",
        EARNINGS_CONFIRMED,
        INTELLIGENCE_ENDPOINTS_SEMANTICS["earnings_confirmed"],
    )
    registry.register(
        "get_market_hours",
        MARKET_HOURS,
        MARKET_ENDPOINTS_SEMANTICS["market_hours"],
    )
    # A second live endpoint, so a k smaller than the index can be requested
    # and still be satisfiable after deprecated hits are dropped.
    registry.register(
        "get_gainers",
        GAINERS,
        MARKET_ENDPOINTS_SEMANTICS["gainers"],
    )

    instance: Any = EndpointVectorStore.__new__(EndpointVectorStore)
    instance.registry = registry
    instance.logger = FMPLogger().get_logger(__name__)
    instance.created_tools = []

    class _Backing:
        def __init__(self) -> None:
            self.added: list[Any] = []

        def add_documents(self, documents: list[Any]) -> None:
            self.added.extend(documents)

        def similarity_search_with_score(
            self, _query: str, k: int = 10
        ) -> list[tuple[Any, float]]:
            # Honours k, like a real backing index: the caller gets a window,
            # not the whole store. That is what lets a deprecated hit consume a
            # slot, which is the behaviour the over-fetch test below pins.
            #
            # Score 0.0 -> similarity 1.0, so nothing is lost to the threshold
            # and the deprecation filter is what is under test.
            return [(doc, 0.0) for doc in self.added[:k]]

    instance.vector_store = _Backing()
    return instance


def test_search_filters_deprecated(real_store: Any) -> None:
    """``search`` is the path an LLM actually reaches.

    ``get_tools(query=...)`` delegates here, so this is the primary selection
    route -- and the one a deprecated endpoint must not survive. Guarded
    separately from the no-query branch because deleting the filter in
    ``search`` alone left the whole of tests/unit/lc green.
    """
    from langchain_core.documents import Document

    real_store.vector_store.add_documents(
        [
            Document(page_content="stale", metadata={"endpoint": name})
            for name in (
                "get_market_hours",
                "get_stock_news_sentiments",
                "get_earnings_confirmed",
            )
        ]
    )

    results = real_store.search("anything")

    assert [result.name for result in results] == ["get_market_hours"]


def test_search_does_not_return_fewer_than_k_because_of_deprecated_hits(
    real_store: Any,
) -> None:
    """Filtering must not silently cost the caller a result slot.

    On a store persisted by an older release -- the case selection-time
    filtering exists for -- deprecated entries sit in the backing index and a
    plain top-k fetch lets each one consume a slot. ``search(q, k=2)`` would
    then hand back one live endpoint and no indication that it had been
    truncated: under-recall instead of a dead endpoint. Ordering the deprecated
    entries first makes that the failure mode without the widening fetch.
    """
    from langchain_core.documents import Document

    real_store.vector_store.add_documents(
        [
            Document(page_content="stale", metadata={"endpoint": name})
            for name in (
                "get_stock_news_sentiments",
                "get_earnings_confirmed",
                "get_market_hours",
                "get_gainers",
            )
        ]
    )

    results = real_store.search("anything", k=2)

    assert [result.name for result in results] == ["get_market_hours", "get_gainers"]


def test_search_still_caps_results_at_k(real_store: Any) -> None:
    """The widening fetch must not leak extra results past ``k``."""
    from langchain_core.documents import Document

    real_store.vector_store.add_documents(
        [
            Document(page_content="stale", metadata={"endpoint": name})
            for name in ("get_market_hours", "get_gainers")
        ]
    )

    assert len(real_store.search("anything", k=1)) == 1


def test_add_endpoints_reports_what_it_indexed(store: Any) -> None:
    """The return value is the indexed count, not the offered count.

    ``create_new_store`` logs it; reporting ``len(names)`` there overstated the
    store by however many endpoints the deprecation filter had just dropped.
    """
    indexed = store.add_endpoints(["live_one", "live_two", "dead_one"])

    assert indexed == 2
