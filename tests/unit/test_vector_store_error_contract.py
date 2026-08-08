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

The exception itself is core: it lives in ``fmp_data.exceptions`` so that
``except VectorStoreCreationError`` works without the ``langchain`` extra, and
the tests covering it run core-only. Only the tests that call
``create_vector_store`` need the extra, and they carry ``@requires_langchain``.

An earlier version of this module claimed no extra was needed at all, which was
false -- the ``monkeypatch`` targets resolve ``fmp_data.lc.embedding``. Skipping
the *whole* module to compensate was also wrong: CI installs no extras, so it
left the exception itself uncovered there.
"""

from __future__ import annotations

from importlib.util import find_spec
import inspect
from typing import Any

import pytest

from fmp_data.exceptions import ConfigError, FMPError, VectorStoreCreationError

# The exception lives in the core exceptions module precisely so that
# ``except VectorStoreCreationError`` works without the langchain extra, so the
# tests covering it must run core-only too. Only the tests that call
# ``create_vector_store`` need the extra; those are marked individually.
# Skipping the whole module instead left the exception uncovered in CI, which
# installs no extras -- a coverage hole disguised as a passing suite.
requires_langchain = pytest.mark.skipif(
    find_spec("langchain_core") is None,
    reason="langchain extra not installed",
)


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


def test_str_surfaces_the_skipped_endpoints() -> None:
    """Logging the exception must not lose what #133 made reachable.

    Plenty of callers do ``logger.error(exc)`` rather than destructuring, and
    the skipped-endpoint dict is the whole point of the new contract.
    """
    err = VectorStoreCreationError(
        "boom",
        cause=RuntimeError("x"),
        failures={"company.profile": "category mismatch"},
    )

    rendered = str(err)
    assert "boom" in rendered
    assert "company.profile" in rendered
    assert "category mismatch" in rendered


def test_str_stays_plain_when_nothing_was_skipped() -> None:
    """No empty ``(0 endpoint(s) skipped)`` noise on the common path."""
    err = VectorStoreCreationError("boom", cause=RuntimeError("x"))
    assert str(err) == "boom"


@requires_langchain
def test_return_annotation_has_no_none_member() -> None:
    """The ``| None`` is gone from the signature, not merely unreachable."""
    from fmp_data.lc import create_vector_store

    annotation = inspect.signature(create_vector_store).return_annotation
    assert annotation == "EndpointVectorStore"


@requires_langchain
def test_setup_registry_failure_is_raised_not_swallowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The #127 regression: an ImportError out of ``setup_registry``."""
    from fmp_data.lc import RegistrySetup, create_vector_store

    boom = ImportError("validation rules unavailable")

    def _explode(_client: Any) -> RegistrySetup:
        raise boom

    monkeypatch.setattr("fmp_data.lc.setup_registry", _explode)

    with pytest.raises(VectorStoreCreationError) as excinfo:
        create_vector_store(fmp_api_key="k", openai_api_key="k")

    assert excinfo.value.cause is boom
    assert excinfo.value.__cause__ is boom


@requires_langchain
def test_missing_api_key_raises_rather_than_returning_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The most common failure used to be indistinguishable from any other."""
    from fmp_data.lc import create_vector_store

    monkeypatch.delenv("FMP_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(VectorStoreCreationError) as excinfo:
        create_vector_store()

    assert isinstance(excinfo.value.cause, ValueError)


@requires_langchain
def test_registry_failures_reach_the_caller_on_the_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """#133's closing note: skipped endpoints were log-only until now."""
    from fmp_data.lc import RegistrySetup, create_vector_store

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


@requires_langchain
def test_setup_registry_returns_registry_and_failures() -> None:
    """The widened return: ``register_batch``'s dict is now reachable."""
    from fmp_data.client import FMPDataClient
    from fmp_data.lc import RegistrySetup, setup_registry
    from fmp_data.lc.registry import EndpointRegistry

    result = setup_registry(FMPDataClient(api_key="dummy"))

    assert isinstance(result, RegistrySetup)
    assert isinstance(result.registry, EndpointRegistry)
    assert isinstance(result.failures, dict)
    # Non-vacuous, and calibrated: the catalog registers 215 endpoints. A loose
    # floor would sit under the 168 that #129 regressed to and call it healthy.
    assert len(result.registry.list_endpoints()) >= 200
    assert result.failures == {}, (
        f"endpoints failed registry validation: {sorted(result.failures)}"
    )


@requires_langchain
def test_setup_registry_result_unpacks_as_a_pair() -> None:
    """``registry, failures = setup_registry(client)`` is the migration path."""
    from fmp_data.client import FMPDataClient
    from fmp_data.lc import setup_registry

    registry, failures = setup_registry(FMPDataClient(api_key="dummy"))

    assert registry.list_endpoints()
    assert failures == {}
