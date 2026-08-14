"""Behaviour of the ``fmp_data.lc`` package module itself.

``fmp_data/lc/__init__.py`` defers every heavy LangChain import to
``__getattr__`` so that domain mapping modules (and MCP discovery) can import
``fmp_data.lc.models`` without the ``langchain`` extra. That laziness, the
registry/vector-store convenience helpers next to it, and their failure paths
are what this module pins.

Not covered here (already pinned elsewhere, do not duplicate):

* ``tests/unit/lc/test_imports.py`` -- ``langchain_core`` import paths used by
  ``fmp_data.lc.vector_store``.
* ``tests/unit/test_vector_store_error_contract.py`` -- the
  ``VectorStoreCreationError`` contract and ``setup_registry`` against the real
  endpoint catalog.
"""

from __future__ import annotations

import logging
import sys
from typing import Any, cast

import pytest

from fmp_data.lc import registry as lc_registry
from fmp_data.lc.models import (
    EndpointSemantics,
    ResponseFieldInfo,
    SemanticCategory,
)
from fmp_data.models import APIVersion, Endpoint, HTTPMethod, URLType

# Dummy credentials used throughout this module. Defined once so the
# literals live on a single annotated line each.
DUMMY_FMP_KEY = "fmp-key"  # pragma: allowlist secret
DUMMY_OPENAI_KEY = "openai-key"  # pragma: allowlist secret
DUMMY_ENV_FMP_KEY = "env-fmp"  # pragma: allowlist secret
DUMMY_ENV_OPENAI_KEY = "env-openai"  # pragma: allowlist secret
DUMMY_ARG_FMP_KEY = "arg-fmp"  # pragma: allowlist secret
DUMMY_ARG_OPENAI_KEY = "arg-openai"  # pragma: allowlist secret

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _endpoint(name: str) -> Endpoint[Any]:
    """A minimal, parameter-free endpoint definition."""
    return Endpoint(
        name=name,
        path=f"{name}/path",
        version=APIVersion.STABLE,
        url_type=URLType.API,
        method=HTTPMethod.GET,
        description=f"Endpoint {name}",
        mandatory_params=[],
        optional_params=None,
        response_model=dict,
        arg_model=None,
    )


def _semantics(method_name: str) -> EndpointSemantics:
    """Semantics with no parameter hints, matching ``_endpoint``."""
    return EndpointSemantics(
        client_name="fake",
        method_name=method_name,
        natural_description="A fabricated endpoint used by the unit tests.",
        example_queries=["show me the fake data"],
        related_terms=["fake"],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={
            "value": ResponseFieldInfo(
                description="A value",
                examples=["1"],
                related_terms=["value"],
            )
        },
        use_cases=["testing"],
    )


def _group(
    endpoint_map: dict[str, Endpoint[Any]],
    semantics_map: dict[str, EndpointSemantics],
) -> dict[str, Any]:
    """A ``GroupConfig``-shaped dict.

    ``category`` and ``client`` are read by ``EndpointRegistry`` when it builds
    its validation rules from the same group table, so they are not optional.
    """
    return {
        "endpoint_map": endpoint_map,
        "semantics_map": semantics_map,
        "category": SemanticCategory.MARKET_DATA,
        "client": "fake",
    }


class _StubRegistry:
    """Stand-in for ``EndpointRegistry``; only ``list_endpoints`` is consumed."""

    def __init__(self, names: list[str]) -> None:
        self._names = names

    def list_endpoints(self) -> dict[str, object]:
        return {name: object() for name in self._names}


def _store_class(
    *,
    validates: bool = True,
    indexed: int = 0,
    ctor_error: Exception | None = None,
) -> tuple[type, list[Any]]:
    """Build a fresh ``EndpointVectorStore`` stand-in plus its instance log.

    A new class per call keeps the recorded instances out of module state, so
    the tests stay order-independent.
    """
    created: list[Any] = []

    class FakeVectorStore:
        def __init__(self, **kwargs: Any) -> None:
            if ctor_error is not None:
                raise ctor_error
            self.kwargs = kwargs
            self.added: list[list[str]] = []
            self.saves = 0
            created.append(self)

        def validate(self) -> bool:
            return validates

        def add_endpoints(self, names: list[str]) -> int:
            self.added.append(list(names))
            return indexed

        def save(self) -> None:
            self.saves += 1

    return FakeVectorStore, created


class _RecordingEmbeddingConfig:
    """Stand-in for ``EmbeddingConfig`` that records how it was built."""

    calls: list[dict[str, Any]]

    def __init__(self, **kwargs: Any) -> None:
        type(self).calls.append(kwargs)
        self.kwargs = kwargs

    def get_embeddings(self) -> str:
        return "sentinel-embeddings"


class _RecordingClient:
    """Stand-in for ``FMPDataClient`` that keeps the key it was built with.

    Two reasons not to build the real thing here:

    * ``FMPDataClient.__init__`` calls ``FMPLogger().configure(...)``, which
      installs a handler on the process-wide ``fmp_data`` logger and pins its
      level -- global state these tests would leak to whatever runs next.
    * The real client owns an ``httpx`` client that nothing closes, so the
      instances only go away when ``__del__`` happens to run.

    ``setup_registry`` never touches the client; ``create_vector_store`` only
    forwards it to the store, which is exactly what the assertions check.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key


@pytest.fixture
def embedding_config(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Replace ``EmbeddingConfig`` and hand back the recorded kwargs list."""
    calls: list[dict[str, Any]] = []
    cls = type("RecordingEmbeddingConfig", (_RecordingEmbeddingConfig,), {})
    cls.calls = calls  # type: ignore[attr-defined]
    monkeypatch.setattr("fmp_data.lc.embedding.EmbeddingConfig", cls)
    return calls


@pytest.fixture
def recording_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Swap the client ``create_vector_store`` builds for a recording stub."""
    monkeypatch.setattr("fmp_data.client.FMPDataClient", _RecordingClient)


@pytest.fixture
def empty_catalog(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make ``setup_registry`` build an empty registry without the real catalog."""
    monkeypatch.setattr(lc_registry, "get_endpoint_groups", dict)


# ---------------------------------------------------------------------------
# lazy attribute access
# ---------------------------------------------------------------------------


def test_lazy_getattr_returns_the_real_embedding_provider() -> None:
    import fmp_data.lc as lc
    from fmp_data.lc.embedding import EmbeddingProvider

    assert lc.EmbeddingProvider is EmbeddingProvider
    assert lc.EmbeddingProvider.OPENAI.value == "openai"


def test_lazy_getattr_returns_the_real_vector_store_class() -> None:
    import fmp_data.lc as lc
    from fmp_data.lc.vector_store import EndpointVectorStore

    assert lc.EndpointVectorStore is EndpointVectorStore


def test_lazy_getattr_returns_the_real_langchain_config() -> None:
    from fmp_data.config import ClientConfig
    import fmp_data.lc as lc
    from fmp_data.lc.config import LangChainConfig

    assert lc.LangChainConfig is LangChainConfig
    assert issubclass(lc.LangChainConfig, ClientConfig)


def test_endpoint_stays_reachable_although_it_is_not_exported() -> None:
    """Pre-lazy-import code did ``from fmp_data.lc import Endpoint``."""
    import fmp_data.lc as lc
    from fmp_data.models import Endpoint as CoreEndpoint

    assert lc.Endpoint is CoreEndpoint
    assert "Endpoint" not in lc.__all__


def test_embeddings_stays_reachable_although_it_is_not_exported() -> None:
    """Same backwards-compatibility promise for ``Embeddings``."""
    from langchain_core.embeddings import Embeddings

    import fmp_data.lc as lc

    assert lc.Embeddings is Embeddings
    assert "Embeddings" not in lc.__all__


def test_unknown_attribute_error_names_module_and_attribute() -> None:
    import fmp_data.lc as lc

    with pytest.raises(AttributeError) as excinfo:
        lc.no_such_symbol  # noqa: B018

    message = str(excinfo.value)
    assert "fmp_data.lc" in message
    assert "no_such_symbol" in message


def test_unknown_attribute_error_survives_getattr_default() -> None:
    """``getattr(mod, name, default)`` must fall back, not blow up."""
    import fmp_data.lc as lc

    assert getattr(lc, "no_such_symbol", "fallback") == "fallback"


def test_every_exported_name_resolves() -> None:
    import fmp_data.lc as lc

    unresolved = [name for name in lc.__all__ if not hasattr(lc, name)]
    assert unresolved == []


def test_all_has_no_duplicates_and_stays_sorted() -> None:
    import fmp_data.lc as lc

    assert len(lc.__all__) == len(set(lc.__all__))
    assert lc.__all__ == sorted(lc.__all__)


def test_dir_advertises_the_lazy_names() -> None:
    """Completion has to see names that ``globals()`` does not hold yet."""
    import fmp_data.lc as lc

    listed = dir(lc)
    assert listed == sorted(listed)
    assert set(lc.__all__) <= set(listed)
    assert {"Endpoint", "Embeddings"} <= set(listed)


def test_lazy_import_failure_is_not_swallowed_as_an_attribute_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A missing extra must surface as an ImportError naming the module.

    ``None`` in ``sys.modules`` reproduces a missing ``langchain_core`` without
    unloading the real one, so the test is order-independent.

    Reported separately, and deliberately *not* asserted here: unlike
    ``init_langchain``, ``__getattr__`` adds no ``pip install
    'fmp-data[langchain]'`` hint. Pinning that absence would make the test fail
    the day someone adds one.
    """
    import fmp_data.lc as lc

    monkeypatch.setitem(sys.modules, "langchain_core.embeddings", None)

    with pytest.raises(ImportError) as excinfo:
        lc.Embeddings  # noqa: B018

    # ``pytest.raises(ImportError)`` is the load-bearing half: a ``__getattr__``
    # that mapped the missing extra onto ``AttributeError`` -- the usual way
    # this goes wrong -- would fail here rather than silently look absent.
    assert "langchain_core.embeddings" in str(excinfo.value)


def test_lazy_config_import_failure_propagates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The same for a first-party lazy target, so the module is not swallowing."""
    import fmp_data.lc as lc

    monkeypatch.setitem(sys.modules, "fmp_data.lc.config", None)

    with pytest.raises(ImportError) as excinfo:
        lc.LangChainConfig  # noqa: B018

    assert "fmp_data.lc.config" in str(excinfo.value)


# ---------------------------------------------------------------------------
# init_langchain
# ---------------------------------------------------------------------------


def test_init_langchain_true_when_dependencies_present(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    import fmp_data.lc as lc

    monkeypatch.setattr(lc, "is_langchain_available", lambda: True)

    with caplog.at_level(logging.WARNING, logger="fmp_data.lc"):
        assert lc.init_langchain() is True

    assert caplog.records == [], (
        f"unexpected log output: {[r.getMessage() for r in caplog.records]}"
    )


def test_init_langchain_warns_with_the_install_hint_when_missing(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """The only place the module tells a user how to fix a missing extra."""
    import fmp_data.lc as lc

    monkeypatch.setattr(lc, "is_langchain_available", lambda: False)

    with caplog.at_level(logging.WARNING, logger="fmp_data.lc"):
        assert lc.init_langchain() is False

    messages = [record.getMessage() for record in caplog.records]
    assert len(messages) == 1, f"expected one warning, got {messages}"
    assert "pip install 'fmp-data[langchain]'" in messages[0]


# ---------------------------------------------------------------------------
# validate_api_keys
# ---------------------------------------------------------------------------


def test_validate_api_keys_prefers_arguments_over_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fmp_data.lc import validate_api_keys

    monkeypatch.setenv("FMP_API_KEY", DUMMY_ENV_FMP_KEY)
    monkeypatch.setenv("OPENAI_API_KEY", DUMMY_ENV_OPENAI_KEY)

    assert validate_api_keys(DUMMY_ARG_FMP_KEY, DUMMY_ARG_OPENAI_KEY) == (
        DUMMY_ARG_FMP_KEY,
        DUMMY_ARG_OPENAI_KEY,
    )


def test_validate_api_keys_falls_back_to_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fmp_data.lc import validate_api_keys

    monkeypatch.setenv("FMP_API_KEY", DUMMY_ENV_FMP_KEY)
    monkeypatch.setenv("OPENAI_API_KEY", DUMMY_ENV_OPENAI_KEY)

    assert validate_api_keys() == (DUMMY_ENV_FMP_KEY, DUMMY_ENV_OPENAI_KEY)


def test_validate_api_keys_rejects_a_missing_fmp_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fmp_data.lc import validate_api_keys

    monkeypatch.delenv("FMP_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", DUMMY_ENV_OPENAI_KEY)

    with pytest.raises(ValueError, match="FMP API key required"):
        validate_api_keys()


def test_validate_api_keys_rejects_a_missing_openai_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The second guard: an FMP key alone is not enough for embeddings."""
    from fmp_data.lc import validate_api_keys

    monkeypatch.setenv("FMP_API_KEY", DUMMY_ENV_FMP_KEY)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OpenAI API key required"):
        validate_api_keys(fmp_api_key=DUMMY_ARG_FMP_KEY)


def test_validate_api_keys_treats_empty_strings_as_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``""`` is falsy, so it must not slip through as a usable key."""
    from fmp_data.lc import validate_api_keys

    monkeypatch.delenv("FMP_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="FMP API key required"):
        validate_api_keys(fmp_api_key="", openai_api_key="k")


# ---------------------------------------------------------------------------
# setup_registry
# ---------------------------------------------------------------------------


def test_setup_registry_skips_endpoints_without_semantics(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    from fmp_data.lc import setup_registry

    groups = {"fake": _group({"get_orphan": _endpoint("get_orphan")}, {})}
    monkeypatch.setattr(lc_registry, "get_endpoint_groups", lambda: groups)

    with caplog.at_level(logging.WARNING, logger="fmp_data.lc"):
        result = setup_registry(client=None)  # type: ignore[arg-type]

    assert result.registry.list_endpoints() == {}
    assert result.failures == {}
    messages = [record.getMessage() for record in caplog.records]
    assert any("No semantics found for endpoint: get_orphan" in m for m in messages), (
        f"missing warning in {messages}"
    )


def test_setup_registry_skips_the_batch_for_a_group_with_no_endpoints(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """An empty group must not reach ``register_batch`` at all.

    ``register_batch({})`` returns ``{}`` and logs nothing, so the registry and
    the failure dict look identical either way; the ``Registered 0/0 endpoints
    from ...`` debug line is the only thing that tells the guard apart from its
    absence, which is why this asserts on the log rather than the return value
    alone.
    """
    from fmp_data.lc import setup_registry

    group_name = "solo_empty_group"
    groups = {group_name: _group({}, {})}
    monkeypatch.setattr(lc_registry, "get_endpoint_groups", lambda: groups)

    with caplog.at_level(logging.DEBUG, logger="fmp_data.lc"):
        registry, failures = setup_registry(client=None)  # type: ignore[arg-type]

    assert registry.list_endpoints() == {}
    assert failures == {}
    messages = [record.getMessage() for record in caplog.records]
    assert not any(group_name in message for message in messages), (
        f"the empty group was still batched: {messages}"
    )


def test_setup_registry_reports_invalid_endpoints_as_failures(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """A drifted endpoint is skipped individually and named in ``failures``."""
    from fmp_data.lc import setup_registry

    groups = {
        "fake": _group(
            {"get_drifted": _endpoint("get_drifted")},
            # Semantics claim a different method name -> validation rejects it.
            {"get_drifted": _semantics("get_something_else")},
        )
    }
    monkeypatch.setattr(lc_registry, "get_endpoint_groups", lambda: groups)

    with caplog.at_level(logging.WARNING, logger="fmp_data.lc"):
        registry, failures = setup_registry(client=None)  # type: ignore[arg-type]

    assert registry.list_endpoints() == {}
    assert list(failures) == ["get_drifted"]
    assert "Method name mismatch" in failures["get_drifted"]
    assert any(
        "Skipped 1 invalid fake endpoints: get_drifted" in record.getMessage()
        for record in caplog.records
    ), f"missing summary warning in {[r.getMessage() for r in caplog.records]}"


def test_setup_registry_merges_failures_across_groups(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failures from every group land in one dict, not just the last one's."""
    from fmp_data.lc import setup_registry

    groups = {
        "first": _group(
            {"get_one": _endpoint("get_one")},
            {"get_one": _semantics("mismatch_one")},
        ),
        "second": _group(
            {"get_two": _endpoint("get_two")},
            {"get_two": _semantics("mismatch_two")},
        ),
    }
    monkeypatch.setattr(lc_registry, "get_endpoint_groups", lambda: groups)

    _registry, failures = setup_registry(client=None)  # type: ignore[arg-type]

    assert sorted(failures) == ["get_one", "get_two"]


def test_setup_registry_resolves_semantics_through_the_get_prefix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``get_x`` finds the ``x`` semantics entry and actually registers."""
    from fmp_data.lc import setup_registry

    groups = {
        "fake": _group(
            {"get_quote": _endpoint("get_quote")},
            {"quote": _semantics("get_quote")},
        )
    }
    monkeypatch.setattr(lc_registry, "get_endpoint_groups", lambda: groups)

    registry, failures = setup_registry(client=None)  # type: ignore[arg-type]

    assert failures == {}
    assert list(registry.list_endpoints()) == ["get_quote"]


# ---------------------------------------------------------------------------
# try_load_existing_store
# ---------------------------------------------------------------------------


def test_try_load_existing_store_returns_a_validated_store(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fmp_data.lc import try_load_existing_store

    store_cls, created = _store_class(validates=True)
    monkeypatch.setattr("fmp_data.lc.vector_store.EndpointVectorStore", store_cls)

    registry = _StubRegistry([])
    store = try_load_existing_store(
        client="client",  # type: ignore[arg-type]
        registry=registry,  # type: ignore[arg-type]
        embeddings="embeddings",  # type: ignore[arg-type]
        cache_dir="/some/cache",
        store_name="custom_store",
    )

    assert store is created[0]
    assert store.kwargs == {
        "client": "client",
        "registry": registry,
        "embeddings": "embeddings",
        "cache_dir": "/some/cache",
        "store_name": "custom_store",
    }


def test_try_load_existing_store_returns_none_when_validation_fails(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    from fmp_data.lc import try_load_existing_store

    store_cls, _created = _store_class(validates=False)
    monkeypatch.setattr("fmp_data.lc.vector_store.EndpointVectorStore", store_cls)

    with caplog.at_level(logging.WARNING, logger="fmp_data.lc"):
        store = try_load_existing_store(
            client="client",  # type: ignore[arg-type]
            registry=_StubRegistry([]),  # type: ignore[arg-type]
            embeddings="embeddings",  # type: ignore[arg-type]
            cache_dir=None,
            store_name="fmp_endpoints",
        )

    assert store is None
    assert any(
        "Existing vector store validation failed" in record.getMessage()
        for record in caplog.records
    ), f"missing warning in {[r.getMessage() for r in caplog.records]}"


def test_try_load_existing_store_swallows_construction_errors(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """A corrupt cache must degrade to "rebuild", not crash the caller."""
    from fmp_data.lc import try_load_existing_store

    store_cls, _created = _store_class(ctor_error=OSError("index file is corrupt"))
    monkeypatch.setattr("fmp_data.lc.vector_store.EndpointVectorStore", store_cls)

    with caplog.at_level(logging.WARNING, logger="fmp_data.lc"):
        store = try_load_existing_store(
            client="client",  # type: ignore[arg-type]
            registry=_StubRegistry([]),  # type: ignore[arg-type]
            embeddings="embeddings",  # type: ignore[arg-type]
            cache_dir=None,
            store_name="fmp_endpoints",
        )

    assert store is None
    assert any(
        "index file is corrupt" in record.getMessage() for record in caplog.records
    ), f"error text lost from {[r.getMessage() for r in caplog.records]}"


# ---------------------------------------------------------------------------
# create_new_store
# ---------------------------------------------------------------------------


def test_create_new_store_indexes_every_registered_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fmp_data.lc import create_new_store

    store_cls, created = _store_class(indexed=3)
    monkeypatch.setattr("fmp_data.lc.vector_store.EndpointVectorStore", store_cls)

    registry = _StubRegistry(["a", "b", "c"])
    store = create_new_store(
        client="client",  # type: ignore[arg-type]
        registry=registry,  # type: ignore[arg-type]
        embeddings="embeddings",  # type: ignore[arg-type]
        cache_dir="/some/cache",
        store_name="fresh_store",
    )

    assert store is created[0]
    assert store.added == [["a", "b", "c"]]
    assert store.saves == 1
    # The destination matters as much as the contents: a rebuild that quietly
    # fell back to the default name/dir would still index all three.
    assert store.kwargs == {
        "client": "client",
        "registry": registry,
        "embeddings": "embeddings",
        "cache_dir": "/some/cache",
        "store_name": "fresh_store",
    }


def test_create_new_store_logs_the_indexed_count_not_the_offered_count(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """#137: deprecated endpoints are dropped on the way in, so the two differ."""
    from fmp_data.lc import create_new_store

    store_cls, _created = _store_class(indexed=2)
    monkeypatch.setattr("fmp_data.lc.vector_store.EndpointVectorStore", store_cls)

    with caplog.at_level(logging.INFO, logger="fmp_data.lc"):
        create_new_store(
            client="client",  # type: ignore[arg-type]
            registry=_StubRegistry(["a", "b", "dead"]),  # type: ignore[arg-type]
            embeddings="embeddings",  # type: ignore[arg-type]
            cache_dir=None,
            store_name="fmp_endpoints",
        )

    messages = [record.getMessage() for record in caplog.records]
    assert any("Created new vector store with 2 endpoints" in m for m in messages), (
        f"expected the indexed count in {messages}"
    )


# ---------------------------------------------------------------------------
# create_vector_store orchestration
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("empty_catalog", "recording_client")
def test_create_vector_store_reuses_a_valid_existing_store(
    monkeypatch: pytest.MonkeyPatch, embedding_config: list[dict[str, Any]]
) -> None:
    from fmp_data.lc import create_vector_store

    store_cls, created = _store_class(validates=True)
    monkeypatch.setattr("fmp_data.lc.vector_store.EndpointVectorStore", store_cls)

    store = create_vector_store(
        fmp_api_key=DUMMY_FMP_KEY,
        openai_api_key=DUMMY_OPENAI_KEY,
        cache_dir="/cache",
        store_name="reused",
    )

    assert store is created[0]
    assert len(created) == 1, "a second store was built despite a valid cache"
    assert store.saves == 0
    assert store.added == []
    assert store.kwargs["store_name"] == "reused"
    assert store.kwargs["cache_dir"] == "/cache"
    assert store.kwargs["embeddings"] == "sentinel-embeddings"
    # The FMP key is the client's, not the embeddings': nothing else pins which
    # of the two keys reaches which collaborator.
    assert store.kwargs["client"].api_key == DUMMY_FMP_KEY  # pragma: allowlist secret


@pytest.mark.usefixtures("empty_catalog", "recording_client")
def test_create_vector_store_rebuilds_when_the_cache_does_not_validate(
    monkeypatch: pytest.MonkeyPatch, embedding_config: list[dict[str, Any]]
) -> None:
    from fmp_data.lc import create_vector_store

    store_cls, created = _store_class(validates=False, indexed=0)
    monkeypatch.setattr("fmp_data.lc.vector_store.EndpointVectorStore", store_cls)

    store = create_vector_store(
        fmp_api_key=DUMMY_FMP_KEY,
        openai_api_key=DUMMY_OPENAI_KEY,
        cache_dir="/cache",
        store_name="rebuilt",
    )

    assert len(created) == 2, "expected a load attempt followed by a rebuild"
    assert store is created[1]
    assert store.saves == 1
    assert store.added == [[]]
    # The rebuild has to land where the failed load looked, or the next run
    # rediscovers the same unusable cache.
    assert store.kwargs == created[0].kwargs


@pytest.mark.usefixtures("empty_catalog", "recording_client")
def test_create_vector_store_force_create_skips_the_load_attempt(
    monkeypatch: pytest.MonkeyPatch, embedding_config: list[dict[str, Any]]
) -> None:
    """``force_create`` must rebuild even when the cache would have validated."""
    from fmp_data.lc import create_vector_store

    store_cls, created = _store_class(validates=True)
    monkeypatch.setattr("fmp_data.lc.vector_store.EndpointVectorStore", store_cls)

    store = create_vector_store(
        fmp_api_key=DUMMY_FMP_KEY,
        openai_api_key=DUMMY_OPENAI_KEY,
        force_create=True,
    )

    assert len(created) == 1, "the existing store was loaded despite force_create"
    assert store is created[0]
    assert store.saves == 1


@pytest.mark.usefixtures("empty_catalog", "recording_client")
def test_create_vector_store_defaults_to_the_openai_embedding_provider(
    monkeypatch: pytest.MonkeyPatch, embedding_config: list[dict[str, Any]]
) -> None:
    from fmp_data.lc import create_vector_store
    from fmp_data.lc.embedding import EmbeddingProvider

    store_cls, _created = _store_class(validates=True)
    monkeypatch.setattr("fmp_data.lc.vector_store.EndpointVectorStore", store_cls)

    create_vector_store(
        fmp_api_key=DUMMY_FMP_KEY,
        openai_api_key=DUMMY_OPENAI_KEY,
    )

    assert len(embedding_config) == 1
    assert embedding_config[0]["provider"] is EmbeddingProvider.OPENAI
    assert embedding_config[0]["model_name"] is None
    assert (
        embedding_config[0]["api_key"] == DUMMY_OPENAI_KEY
    )  # pragma: allowlist secret


@pytest.mark.usefixtures("empty_catalog", "recording_client")
def test_create_vector_store_passes_an_explicit_provider_and_model_through(
    monkeypatch: pytest.MonkeyPatch, embedding_config: list[dict[str, Any]]
) -> None:
    from fmp_data.lc import create_vector_store
    from fmp_data.lc.embedding import EmbeddingProvider

    store_cls, _created = _store_class(validates=True)
    monkeypatch.setattr("fmp_data.lc.vector_store.EndpointVectorStore", store_cls)

    create_vector_store(
        fmp_api_key=DUMMY_FMP_KEY,
        openai_api_key=DUMMY_OPENAI_KEY,
        embedding_provider=EmbeddingProvider.HUGGINGFACE,
        embedding_model="sentence-transformers/all-mpnet-base-v2",
    )

    assert embedding_config[0]["provider"] is EmbeddingProvider.HUGGINGFACE
    assert (
        embedding_config[0]["model_name"] == "sentence-transformers/all-mpnet-base-v2"
    )


@pytest.mark.usefixtures("recording_client")
def test_create_vector_store_demands_an_openai_key_for_any_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pins CURRENT behaviour, which looks wrong -- see the reported finding.

    ``EmbeddingConfig(provider=HUGGINGFACE)`` needs no API key at all
    (``tests/unit/lc/test_embedding.py``), yet ``create_vector_store`` runs
    ``validate_api_keys`` unconditionally, so a HuggingFace store cannot be
    built without an unrelated ``OPENAI_API_KEY``.
    """
    from fmp_data.exceptions import VectorStoreCreationError
    from fmp_data.lc import create_vector_store
    from fmp_data.lc.embedding import EmbeddingProvider

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(VectorStoreCreationError) as excinfo:
        create_vector_store(
            fmp_api_key=DUMMY_FMP_KEY,
            embedding_provider=EmbeddingProvider.HUGGINGFACE,
        )

    cause = excinfo.value.cause
    assert isinstance(cause, ValueError)
    assert "OpenAI API key required" in str(cause)


@pytest.mark.usefixtures("empty_catalog", "recording_client")
def test_create_vector_store_reads_keys_from_the_environment(
    monkeypatch: pytest.MonkeyPatch, embedding_config: list[dict[str, Any]]
) -> None:
    from fmp_data.lc import create_vector_store

    store_cls, _created = _store_class(validates=True)
    monkeypatch.setattr("fmp_data.lc.vector_store.EndpointVectorStore", store_cls)
    monkeypatch.setenv("FMP_API_KEY", DUMMY_ENV_FMP_KEY)
    monkeypatch.setenv("OPENAI_API_KEY", DUMMY_ENV_OPENAI_KEY)

    store = create_vector_store()

    assert (
        embedding_config[0]["api_key"] == DUMMY_ENV_OPENAI_KEY
    )  # pragma: allowlist secret
    # `store` is the stub from `_store_class`, not a real EndpointVectorStore,
    # so its recorded ctor kwargs are reached through cast(Any, ...).
    forwarded_client = cast(Any, store).kwargs["client"]
    assert forwarded_client.api_key == DUMMY_ENV_FMP_KEY


@pytest.mark.usefixtures("empty_catalog", "recording_client")
def test_create_vector_store_wraps_a_rebuild_failure(
    monkeypatch: pytest.MonkeyPatch, embedding_config: list[dict[str, Any]]
) -> None:
    """A failure after registration still arrives as ``VectorStoreCreationError``."""
    from fmp_data.exceptions import VectorStoreCreationError
    from fmp_data.lc import create_vector_store

    boom = RuntimeError("disk full")
    store_cls, _created = _store_class(ctor_error=boom)
    monkeypatch.setattr("fmp_data.lc.vector_store.EndpointVectorStore", store_cls)

    with pytest.raises(VectorStoreCreationError) as excinfo:
        create_vector_store(fmp_api_key=DUMMY_FMP_KEY, openai_api_key=DUMMY_OPENAI_KEY)

    assert excinfo.value.cause is boom
    assert excinfo.value.failures == {}
    assert "disk full" in str(excinfo.value)


@pytest.mark.usefixtures("recording_client")
def test_create_vector_store_carries_real_registry_failures(
    monkeypatch: pytest.MonkeyPatch, embedding_config: list[dict[str, Any]]
) -> None:
    """End to end: a genuinely rejected endpoint reaches the caller by name."""
    from fmp_data.exceptions import VectorStoreCreationError
    from fmp_data.lc import create_vector_store

    groups = {
        "fake": _group(
            {"get_drifted": _endpoint("get_drifted")},
            {"get_drifted": _semantics("get_something_else")},
        )
    }
    monkeypatch.setattr(lc_registry, "get_endpoint_groups", lambda: groups)

    store_cls, _created = _store_class(ctor_error=RuntimeError("disk full"))
    monkeypatch.setattr("fmp_data.lc.vector_store.EndpointVectorStore", store_cls)

    with pytest.raises(VectorStoreCreationError) as excinfo:
        create_vector_store(fmp_api_key=DUMMY_FMP_KEY, openai_api_key=DUMMY_OPENAI_KEY)

    assert list(excinfo.value.failures) == ["get_drifted"]
    assert "get_drifted" in str(excinfo.value)
