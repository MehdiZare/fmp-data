"""``create_vector_store`` raises instead of returning ``None`` (#133).

#127 made ``setup_registry`` propagate non-validation errors -- the loud half
of #121. ``create_vector_store`` then wrapped the whole body, that call
included, in ``except Exception: return None``, so nothing #127 made propagate
reached a library user. ``None`` also carried no information: the blanket
handler was the only caller-reachable ``return None``, so it unconditionally
meant "something threw" and never said what.

From 2.6 the function raises :class:`VectorStoreCreationError`, carrying the
underlying ``cause`` and the per-endpoint ``failures`` dict, and its return type
is ``EndpointVectorStore`` with no ``None`` member.

Requires the ``langchain`` extra. An earlier version of this docstring claimed
otherwise -- that every failure path trips before ``create_vector_store``
reaches its ``fmp_data.lc.embedding`` import. That is false: the ``monkeypatch``
targets below resolve that module, so it must be importable. CI installs no
extras, so these passed locally and failed the whole matrix.
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest

pytest.importorskip("langchain_core", reason="langchain extra not installed")

from fmp_data.exceptions import (
    ConfigError,
    FMPError,
    VectorStoreCreationError,
)
from fmp_data.lc import RegistrySetup, create_vector_store, setup_registry


def test_vector_store_creation_error_is_an_fmp_error() -> None:
    """Callers already catching ``FMPError`` keep catching this."""
    assert issubclass(VectorStoreCreationError, FMPError)


def test_error_carries_cause_and_failures() -> None:
    cause = ImportError("no such module")
    failures = {"company.profile": "category mismatch"}
    err = VectorStoreCreationError("boom", cause=cause, failures=failures)

    assert err.cause is cause
    assert err.failures == failures
    assert "boom" in str(err)


def test_failures_defaults_to_an_empty_dict_not_none() -> None:
    """``failures`` is always a dict, so callers need no ``or {}`` dance."""
    err = VectorStoreCreationError("boom", cause=RuntimeError("x"))
    assert err.failures == {}


def test_return_annotation_has_no_none_member() -> None:
    """The ``| None`` is gone from the signature, not merely unreachable."""
    annotation = inspect.signature(create_vector_store).return_annotation
    assert annotation == "EndpointVectorStore"


def test_setup_registry_failure_is_raised_not_swallowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The #127 regression: an ImportError out of ``setup_registry``."""
    boom = ImportError("validation rules unavailable")

    def _explode(_client: Any) -> RegistrySetup:
        raise boom

    monkeypatch.setattr("fmp_data.lc.setup_registry", _explode)

    with pytest.raises(VectorStoreCreationError) as excinfo:
        create_vector_store(fmp_api_key="k", openai_api_key="k")

    assert excinfo.value.cause is boom
    assert excinfo.value.__cause__ is boom


def test_missing_api_key_raises_rather_than_returning_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The most common failure used to be indistinguishable from any other."""
    monkeypatch.delenv("FMP_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(VectorStoreCreationError) as excinfo:
        create_vector_store()

    assert isinstance(excinfo.value.cause, ValueError)


def test_registry_failures_reach_the_caller_on_the_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """#133's closing note: skipped endpoints were log-only until now."""
    failures = {"intelligence.earnings_confirmed": "category mismatch"}

    def _partial(_client: Any) -> RegistrySetup:
        return RegistrySetup(registry=object(), failures=failures)  # type: ignore[arg-type]

    def _explode(*_args: Any, **_kwargs: Any) -> Any:
        raise ConfigError("embeddings unavailable")

    monkeypatch.setattr("fmp_data.lc.setup_registry", _partial)
    monkeypatch.setattr("fmp_data.lc.embedding.EmbeddingConfig", _explode)

    with pytest.raises(VectorStoreCreationError) as excinfo:
        create_vector_store(fmp_api_key="k", openai_api_key="k")

    assert excinfo.value.failures == failures


def test_setup_registry_returns_registry_and_failures() -> None:
    """The widened return: ``register_batch``'s dict is now reachable."""
    from fmp_data.client import FMPDataClient
    from fmp_data.lc.registry import EndpointRegistry

    result = setup_registry(FMPDataClient(api_key="dummy"))

    assert isinstance(result, RegistrySetup)
    assert isinstance(result.registry, EndpointRegistry)
    assert isinstance(result.failures, dict)
    # Non-vacuous: the catalog is large, and a healthy run skips nothing.
    assert len(result.registry.list_endpoints()) > 100
    assert result.failures == {}, (
        f"endpoints failed registry validation: {sorted(result.failures)}"
    )


def test_setup_registry_result_unpacks_as_a_pair() -> None:
    """``registry, failures = setup_registry(client)`` is the migration path."""
    from fmp_data.client import FMPDataClient

    registry, failures = setup_registry(FMPDataClient(api_key="dummy"))

    assert registry.list_endpoints()
    assert failures == {}
