"""Deprecated endpoints are not selectable through the vector store (#137).

Three intelligence endpoints return ``[]`` without calling upstream. They stayed
indexed, so a semantic query could pick one and the LLM got an empty success --
indistinguishable from "no data for your query".

``EndpointSemantics.deprecated`` marks them, and ``EndpointVectorStore`` filters
on it at index time *and* at selection time. The entries are not deleted: their
tool keys stay resolvable for anyone loading them through an explicit MCP
manifest, and the MCP catalog count does not move.
"""

from __future__ import annotations

from typing import Any

import pytest

from fmp_data.intelligence.mapping import INTELLIGENCE_ENDPOINTS_SEMANTICS
from fmp_data.lc.models import EndpointSemantics

#: The endpoints #137 names. Spelled out rather than derived, so silently
#: un-marking one fails here instead of shrinking a computed set to nothing.
DEPRECATED_INTELLIGENCE_ENDPOINTS = {
    "stock_news_sentiments",
    "earnings_confirmed",
    "earnings_surprises",
}


def test_deprecated_defaults_to_false() -> None:
    """Existing semantics keep their meaning without touching every entry."""
    assert EndpointSemantics.model_fields["deprecated"].default is False


def test_the_three_intelligence_endpoints_are_marked() -> None:
    marked = {
        name
        for name, semantics in INTELLIGENCE_ENDPOINTS_SEMANTICS.items()
        if semantics.deprecated
    }
    assert marked == DEPRECATED_INTELLIGENCE_ENDPOINTS


def test_marked_endpoints_are_not_deleted() -> None:
    """#137 is explicit: keep the entries so tool keys stay resolvable."""
    for name in DEPRECATED_INTELLIGENCE_ENDPOINTS:
        assert name in INTELLIGENCE_ENDPOINTS_SEMANTICS


def test_nothing_else_is_marked_deprecated_by_accident() -> None:
    """A floor on the other side: the flag is off for the rest of the catalog.

    Scans every semantics table, not just intelligence -- otherwise another
    domain could acquire ``deprecated=True`` and silently vanish from the
    vector store with nothing to catch it.
    """
    import importlib
    import pkgutil

    import fmp_data
    from fmp_data.lc.models import EndpointSemantics

    flagged: set[str] = set()
    checked = 0
    for module_info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
        if not module_info.name.endswith(".mapping"):
            continue
        module = importlib.import_module(module_info.name)
        for attr, value in vars(module).items():
            if not (attr.endswith("_SEMANTICS") and isinstance(value, dict)):
                continue
            for key, semantics in value.items():
                if not isinstance(semantics, EndpointSemantics):
                    continue
                checked += 1
                if semantics.deprecated:
                    flagged.add(key)

    assert flagged == DEPRECATED_INTELLIGENCE_ENDPOINTS, (
        "the set of deprecated endpoints changed. Deprecating one is fine, "
        "but it removes the endpoint from the LangChain vector store, so it "
        f"must be deliberate. Expected {sorted(DEPRECATED_INTELLIGENCE_ENDPOINTS)}, "
        f"found {sorted(flagged)}"
    )
    # Without a floor an empty scan reads as a pass.
    assert checked > 150, f"only {checked} semantics scanned; is the walk working?"


def test_mcp_catalog_still_advertises_the_deprecated_keys() -> None:
    """The flag is LangChain-side only; MCP tool keys must stay resolvable.

    #137 chose the flag over deleting the entries precisely so the catalog
    count does not move and nothing breaks without a deprecation window. MCP
    reads the semantics tables directly and never consults the vector store.
    """
    pytest.importorskip("mcp", reason="mcp extra not installed")
    from fmp_data.mcp.discovery import discover_all_tools

    keys = {tool["key"] for tool in discover_all_tools()}
    assert DEPRECATED_INTELLIGENCE_ENDPOINTS <= keys


def test_lc_deprecation_and_mcp_deprecated_tools_are_separate() -> None:
    """Two mechanisms, deliberately disjoint -- see the comments on each.

    ``DEPRECATED_TOOLS`` renames duplicate keys for methods that still work;
    ``EndpointSemantics.deprecated`` marks endpoints that return nothing. If a
    future change makes these overlap, that is a design decision to take
    explicitly rather than discover.
    """
    pytest.importorskip("mcp", reason="mcp extra not installed")
    from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS

    aliased = {spec.split(".", 1)[-1] for spec in DEPRECATED_TOOLS}
    assert not (aliased & DEPRECATED_INTELLIGENCE_ENDPOINTS)


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
    from fmp_data.market.endpoints import MARKET_HOURS
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
            # Score 0.0 -> similarity 1.0, so nothing is lost to the
            # threshold and the deprecation filter is what is under test.
            return [(doc, 0.0) for doc in self.added]

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
