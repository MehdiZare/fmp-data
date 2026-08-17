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
   must stay on the explicit allowlist below, which is currently *empty*; a
   new entry is a PR failure until someone decides request-fallback is
   intended (and adds it) or aligns the shapes. The allowlist pins the
   *uncovered required* method params so a known mismatch cannot silently
   gain more debt.
3. **mandatory wire dropped under method dispatch** — a mandatory endpoint
   field maps to no method parameter, so method dispatch omits it from the
   tool schema. Known cases (e.g. revenue ``structure``) are allowlisted;
   new ones fail until reviewed.

Optional wire fields dropped under method dispatch are intentionally out of
scope here (they are not required for a successful call). MCP registers the
live Python method via :func:`fmp_data.tool_binding.resolve_attr` and does
not run this shape gate, so the two integrations *could* disagree on an
allowlisted fallback — but as of #188 nothing is allowlisted, so both
dispatch through the same method for every tool in the catalogue. This guard
pins LangChain's classification and that every semantics method still
resolves on a real client.

The classification helpers come from :mod:`fmp_data.tool_binding`, the same
module the two integrations bind through. This file used to keep its own
copies; a guard that reimplements the rule it guards can only ever check
itself.
"""

from __future__ import annotations

from typing import Any

import pytest

from fmp_data.client import FMPDataClient
from fmp_data.lc import resolve_semantics_for_endpoint
from fmp_data.lc.registry import get_endpoint_groups
from fmp_data.models import Endpoint, EndpointParam, ParamLocation, ParamType
from fmp_data.tool_binding import (
    bindable_params,
    method_dispatch_compatible,
    resolve_client_method,
    resolve_method_param_name,
    uncovered_required_params,
)

# Floors, not equalities: a walk that stops yielding must fail rather than
# pass vacuously. Observed on the catalogue at time of writing: 215 triples,
# all 215 method-compatible, 0 request-fallback, 0 dropped-mandatory.
_MIN_PAIRS = 200
_MIN_METHOD_COMPATIBLE = 200

# ``(client_name, method_name, frozenset[uncovered required method params])``
# pairs whose wire shape cannot fill every required method parameter.
# LangChain falls back to ``client.request`` for these (#186). Expand only
# when a new shape mismatch is deliberate — and pin the uncovered names so
# the known debt cannot silently grow.
#
# Empty since #188 aligned the last two entries. The institutional Form 13F
# and symbol-positions-summary tools used to sit here because their client
# methods required ``report_date`` while the wire takes ``year``/``quarter``;
# they now dispatch through ``get_form_13f_by_quarter`` /
# ``get_institutional_holdings_by_quarter``, which match the API. Keeping the
# allowlist (rather than deleting it with the entries) is deliberate: the
# assertions below are what make a *new* mismatch a PR failure, and an empty
# allowlist is the strongest form of that guard.
KNOWN_REQUEST_FALLBACK: frozenset[tuple[str, str, frozenset[str]]] = frozenset()
_KNOWN_REQUEST_FALLBACK_METHODS: frozenset[tuple[str, str]] = frozenset(
    (client, method) for client, method, _uncovered in KNOWN_REQUEST_FALLBACK
)

# ``(client_name, method_name, wire_param)``: mandatory endpoint fields that
# method dispatch intentionally omits from the tool schema because the
# client method does not accept them.
#
# Empty since #349: revenue ``structure`` is optional. A new
# dropped-mandatory is a PR failure.
KNOWN_DROPPED_MANDATORY_WIRE: frozenset[tuple[str, str, str]] = frozenset()


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


def _endpoint_param_names(endpoint: Endpoint[Any]) -> list[str]:
    return [
        p.name
        for p in list(endpoint.mandatory_params) + list(endpoint.optional_params or [])
    ]


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
    when a required method param has no wire source. ``KNOWN_REQUEST_FALLBACK``
    is empty: every catalog tool currently dispatches through a client
    method. Any *new* entry is almost always accidental drift between the
    endpoint declaration and the client method, and must be justified (or
    fixed) before landing. The allowlist also pins uncovered required
    param names so known debt cannot silently grow.
    """
    actual_fallback: set[tuple[str, str, frozenset[str]]] = set()
    method_compatible = 0

    for _label, endpoint, semantics in _catalog():
        method = resolve_client_method(
            live_client, semantics.client_name, semantics.method_name
        )
        assert method is not None  # covered by test_every_semantics_method_resolves
        ep_names = _endpoint_param_names(endpoint)
        method_key = (semantics.client_name, semantics.method_name)
        if method_dispatch_compatible(method, ep_names):
            method_compatible += 1
            assert method_key not in _KNOWN_REQUEST_FALLBACK_METHODS, (
                f"{method_key[0]}.{method_key[1]} is method-dispatch compatible "
                f"but still listed in KNOWN_REQUEST_FALLBACK — remove the stale "
                f"allowlist entry"
            )
        else:
            uncovered = uncovered_required_params(method, ep_names)
            actual_fallback.add((*method_key, uncovered))

    unexpected = sorted(
        actual_fallback - KNOWN_REQUEST_FALLBACK,
        key=lambda t: (t[0], t[1], sorted(t[2])),
    )
    stale = sorted(
        KNOWN_REQUEST_FALLBACK - actual_fallback,
        key=lambda t: (t[0], t[1], sorted(t[2])),
    )
    assert not unexpected, (
        "New endpoint↔method shape mismatches (required method params "
        "uncovered by wire fields). Either align the shapes or add to "
        "KNOWN_REQUEST_FALLBACK with a comment (client, method, "
        "frozenset of uncovered required method params):\n"
        + "\n".join(f"  {c}.{m}: {sorted(u)}" for c, m, u in unexpected)
    )
    assert not stale, (
        "KNOWN_REQUEST_FALLBACK lists pairs that no longer match (now "
        "method-compatible, or uncovered required params changed); update "
        "or remove them:\n" + "\n".join(f"  {c}.{m}: {sorted(u)}" for c, m, u in stale)
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
        ep_names = _endpoint_param_names(endpoint)
        if not method_dispatch_compatible(method, ep_names):
            # Request-fallback tools keep the full endpoint schema; drops
            # only apply under method dispatch.
            continue
        method_names = set(bindable_params(method))
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


# ---------------------------------------------------------------------------
# Synthetic cases: prove the classifier fails closed when shapes drift.
# Catalogue walks alone cannot catch a neutered assertion.
# ---------------------------------------------------------------------------


def _fake_endpoint(*mandatory: str, optional: tuple[str, ...] = ()) -> Endpoint[Any]:
    def _param(name: str) -> EndpointParam:
        return EndpointParam(
            name=name,
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description=name,
        )

    return Endpoint(
        name="synthetic",
        path="synthetic",
        description="synthetic endpoint for coverage guard unit tests",
        mandatory_params=[_param(n) for n in mandatory],
        optional_params=[_param(n) for n in optional] or None,
        response_model=dict,
    )


def test_classifier_flags_uncovered_required_method_param() -> None:
    """A required method param with no wire source is request-fallback debt."""

    def method(cik: str, report_date: str) -> None:  # pragma: no cover - signature only
        del cik, report_date

    endpoint = _fake_endpoint("cik", "year", "quarter")
    ep_names = _endpoint_param_names(endpoint)
    assert not method_dispatch_compatible(method, ep_names)
    assert uncovered_required_params(method, ep_names) == frozenset({"report_date"})


def test_classifier_flags_dropped_mandatory_wire_field() -> None:
    """A mandatory wire field with no method param is a method-dispatch drop."""

    def method(symbol: str, period: str = "annual") -> None:  # pragma: no cover
        del symbol, period

    endpoint = _fake_endpoint("symbol", "structure", optional=("period",))
    ep_names = _endpoint_param_names(endpoint)
    assert method_dispatch_compatible(method, ep_names)
    method_names = set(bindable_params(method))
    dropped = [
        p.name
        for p in endpoint.mandatory_params
        if resolve_method_param_name(p.name, method_names) is None
    ]
    assert dropped == ["structure"]


def test_classifier_compatible_when_wire_covers_required_params() -> None:
    """Exact or aliased wire names clear the method-dispatch gate."""

    def method(symbol: str, from_date: str | None = None) -> None:  # pragma: no cover
        del symbol, from_date

    endpoint = _fake_endpoint("symbol", optional=("from",))
    ep_names = _endpoint_param_names(endpoint)
    assert method_dispatch_compatible(method, ep_names)
    assert uncovered_required_params(method, ep_names) == frozenset()
