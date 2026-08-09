"""Catalogue-wide endpoint ↔ client-method parameter coverage guard (#188).

#172 / #186 taught LangChain tools to dispatch through
``client.<client>.<method>`` when every required method parameter can be
filled from the endpoint's wire fields (via alias mapping). When shapes
diverge the tool falls back to ``client.request`` so invoke never
``TypeError``s — but that gate is per-call. Without a catalogue walk, a new
mismatch lands only as a silent request-fallback or a silently-dropped wire
field.

This guard walks every ``(endpoint_map x semantics)`` pair that
``setup_registry`` would enroll and classifies each:

1. **method-dispatch compatible** — every required method param is covered
   by a wire/endpoint field (exact name or alias).
2. **request-fallback** — a required method param has no wire source. These
   must stay on the explicit allowlist below; a new entry is a PR failure
   until someone decides request-fallback is intended (and adds it) or
   aligns the shapes.
3. **mandatory wire dropped under method dispatch** — a mandatory endpoint
   field maps to no method parameter, so method dispatch omits it from the
   tool schema. Known cases (e.g. revenue ``structure``) are allowlisted;
   new ones fail until reviewed.

MCP already resolves methods via ``_resolve_attr``; this guard reuses the LC
helpers so the two integrations cannot silently disagree about *whether* a
method is shape-compatible with its endpoint.
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest

from fmp_data.client import FMPDataClient
from fmp_data.lc import resolve_semantics_for_endpoint
from fmp_data.lc.registry import get_endpoint_groups
from fmp_data.lc.vector_store import (
    method_dispatch_compatible,
    resolve_client_method,
    resolve_method_param_name,
)
from fmp_data.models import Endpoint

# Floors, not equalities: a walk that stops yielding must fail rather than
# pass vacuously. Observed on the catalogue at time of writing: 215 triples,
# 213 method-compatible, 2 request-fallback, 2 dropped-mandatory.
_MIN_PAIRS = 150
_MIN_METHOD_COMPATIBLE = 150

# ``(client_name, method_name)`` pairs whose wire shape cannot fill every
# required method parameter. LangChain falls back to ``client.request`` for
# these (#186). Expand only when a new shape mismatch is deliberate.
KNOWN_REQUEST_FALLBACK: frozenset[tuple[str, str]] = frozenset(
    {
        # Wire year/quarter vs method report_date (#188 institutional debt).
        ("institutional", "get_form_13f"),
        ("institutional", "get_institutional_holdings"),
    }
)

# ``(client_name, method_name, wire_param)``: mandatory endpoint fields that
# method dispatch intentionally omits from the tool schema because the
# client method does not accept them.
KNOWN_DROPPED_MANDATORY_WIRE: frozenset[tuple[str, str, str]] = frozenset(
    {
        # Endpoint still declares structure=flat|hierarchical; methods only
        # take symbol + period and the API default is fine for LLM tools.
        ("company", "get_product_revenue_segmentation", "structure"),
        ("company", "get_geographic_revenue_segmentation", "structure"),
    }
)


def _catalog() -> list[tuple[str, Endpoint[Any], Any]]:
    """Every (label, endpoint, semantics) triple with resolvable semantics."""
    triples: list[tuple[str, Endpoint[Any], Any]] = []
    for group, config in get_endpoint_groups().items():
        semantics_map = config["semantics_map"]
        for name, endpoint in config["endpoint_map"].items():
            semantics = resolve_semantics_for_endpoint(name, semantics_map)
            if semantics is not None:
                triples.append((f"{group}.{name}", endpoint, semantics))
    return triples


def _method_params(method: Any) -> dict[str, inspect.Parameter]:
    return {
        name: param
        for name, param in inspect.signature(method).parameters.items()
        if name != "self"
        and param.kind
        in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    }


@pytest.fixture(scope="module")
def live_client():
    """Real client used only for attribute / signature resolution (no HTTP)."""
    client = FMPDataClient(api_key="dummy-key-for-endpoint-method-coverage")
    try:
        yield client
    finally:
        client.close()


def test_every_semantics_method_resolves(live_client: FMPDataClient) -> None:
    """Ghost method_name values must fail here, not at first tool invoke."""
    missing: list[str] = []
    checked = 0
    for label, _endpoint, semantics in _catalog():
        checked += 1
        method = resolve_client_method(
            live_client, semantics.client_name, semantics.method_name
        )
        if method is None:
            missing.append(
                f"{label} -> {semantics.client_name}.{semantics.method_name}"
            )
    assert checked >= _MIN_PAIRS, (
        f"only walked {checked} endpoint/semantics pairs; expected ≥ {_MIN_PAIRS}"
    )
    assert not missing, "Unresolvable semantics method names:\n" + "\n".join(missing)


def test_request_fallback_set_is_exactly_the_known_mismatches(
    live_client: FMPDataClient,
) -> None:
    """New shape mismatches fail until allowlisted or fixed.

    Method dispatch returns ``None`` (and the tool uses ``client.request``)
    when a required method param has no wire source. That is correct for the
    two institutional year/quarter tools; any *new* entry is almost always
    an accidental drift between endpoint declaration and client method.
    """
    actual_fallback: set[tuple[str, str]] = set()
    method_compatible = 0

    for _label, endpoint, semantics in _catalog():
        method = resolve_client_method(
            live_client, semantics.client_name, semantics.method_name
        )
        assert method is not None  # covered by test_every_semantics_method_resolves
        ep_names = [
            p.name
            for p in list(endpoint.mandatory_params)
            + list(endpoint.optional_params or [])
        ]
        key = (semantics.client_name, semantics.method_name)
        if method_dispatch_compatible(method, ep_names):
            method_compatible += 1
            assert key not in KNOWN_REQUEST_FALLBACK, (
                f"{key[0]}.{key[1]} is method-dispatch compatible but still listed "
                f"in KNOWN_REQUEST_FALLBACK — remove the stale allowlist entry"
            )
        else:
            actual_fallback.add(key)

    unexpected = sorted(actual_fallback - KNOWN_REQUEST_FALLBACK)
    stale = sorted(KNOWN_REQUEST_FALLBACK - actual_fallback)
    assert not unexpected, (
        "New endpoint↔method shape mismatches (required method params "
        "uncovered by wire fields). Either align the shapes or add to "
        "KNOWN_REQUEST_FALLBACK with a comment:\n"
        + "\n".join(f"  {c}.{m}" for c, m in unexpected)
    )
    assert not stale, (
        "KNOWN_REQUEST_FALLBACK lists pairs that are now method-compatible; "
        "remove them:\n" + "\n".join(f"  {c}.{m}" for c, m in stale)
    )
    assert method_compatible >= _MIN_METHOD_COMPATIBLE, (
        f"only {method_compatible} method-compatible pairs; "
        f"expected ≥ {_MIN_METHOD_COMPATIBLE}"
    )
    assert actual_fallback == set(KNOWN_REQUEST_FALLBACK)


def test_mandatory_wire_fields_dropped_under_method_dispatch_are_allowlisted(
    live_client: FMPDataClient,
) -> None:
    """Mandatory wire params that method dispatch omits must be reviewed.

    When method dispatch is active, unmapped endpoint params are dropped
    from the tool schema so LLMs are not asked for values that never reach
    the method (#186). Dropping a *mandatory* wire field is therefore a
    real schema change and must not land silently.
    """
    actual: set[tuple[str, str, str]] = set()

    for _label, endpoint, semantics in _catalog():
        method = resolve_client_method(
            live_client, semantics.client_name, semantics.method_name
        )
        assert method is not None
        ep_names = [
            p.name
            for p in list(endpoint.mandatory_params)
            + list(endpoint.optional_params or [])
        ]
        if not method_dispatch_compatible(method, ep_names):
            # Request-fallback tools keep the full endpoint schema; drops
            # only apply under method dispatch.
            continue
        method_names = set(_method_params(method))
        for param in endpoint.mandatory_params:
            if resolve_method_param_name(param.name, method_names) is None:
                actual.add((semantics.client_name, semantics.method_name, param.name))

    unexpected = sorted(actual - KNOWN_DROPPED_MANDATORY_WIRE)
    stale = sorted(KNOWN_DROPPED_MANDATORY_WIRE - actual)
    assert not unexpected, (
        "New mandatory wire fields would be omitted from LangChain tool "
        "schemas under method dispatch. Align the method signature, stop "
        "declaring the field mandatory, or add to "
        "KNOWN_DROPPED_MANDATORY_WIRE with a comment:\n"
        + "\n".join(f"  {c}.{m}: {p}" for c, m, p in unexpected)
    )
    assert not stale, (
        "KNOWN_DROPPED_MANDATORY_WIRE lists triples that no longer drop; "
        "remove them:\n" + "\n".join(f"  {c}.{m}: {p}" for c, m, p in stale)
    )
    assert actual == set(KNOWN_DROPPED_MANDATORY_WIRE)
