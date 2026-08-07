"""Guard tests: the whole endpoint catalog must register cleanly.

These catch semantics drift (missing/extra parameter hints, category
mismatches, unpaired endpoints) without needing a vector store or API key.
"""

from typing import Any

from fmp_data.lc.models import EndpointSemantics
from fmp_data.lc.registry import EndpointRegistry, get_endpoint_groups
from fmp_data.models import Endpoint


def _semantics_for(
    endpoint_name: str, semantics_map: dict[str, EndpointSemantics]
) -> EndpointSemantics | None:
    """Resolve semantics the same way ``setup_registry`` does."""
    from fmp_data.lc import resolve_semantics_for_endpoint

    return resolve_semantics_for_endpoint(endpoint_name, semantics_map)


def _catalog() -> dict[str, tuple[dict[str, Endpoint[Any]], dict[str, Any]]]:
    return {
        name: (config["endpoint_map"], config["semantics_map"])
        for name, config in get_endpoint_groups().items()
    }


def test_every_endpoint_has_semantics() -> None:
    """Every endpoint in a client's map must be paired with semantics."""
    unpaired = [
        f"{group}.{endpoint_name}"
        for group, (endpoint_map, semantics_map) in _catalog().items()
        for endpoint_name in endpoint_map
        if _semantics_for(endpoint_name, semantics_map) is None
    ]

    assert unpaired == [], f"Endpoints without semantics: {unpaired}"


def test_every_endpoint_passes_registry_validation() -> None:
    """Every paired endpoint must survive EndpointRegistry validation.

    Uses a single shared registry across all groups, mirroring
    ``setup_registry``. A per-group registry would hide a cross-group endpoint
    name collision, which in production silently overwrites the first entry.
    """
    failures: dict[str, str] = {}
    registry = EndpointRegistry()
    total = 0

    for group, (endpoint_map, semantics_map) in _catalog().items():
        batch = {}
        for endpoint_name, endpoint in endpoint_map.items():
            total += 1
            semantics = _semantics_for(endpoint_name, semantics_map)
            if semantics is not None:
                batch[endpoint_name] = (endpoint, semantics)

        for name, error in registry.register_batch(batch).items():
            failures[f"{group}.{name}"] = error

    assert failures == {}, f"Endpoints failing validation: {failures}"
    assert len(registry.list_endpoints()) == total, (
        "Endpoint name collision across client groups: "
        f"{total} endpoints registered but only "
        f"{len(registry.list_endpoints())} survived on a shared registry"
    )


def _endpoints_by_method(
    endpoint_map: dict[str, Endpoint[Any]], semantics_map: dict[str, Any]
) -> dict[str, Endpoint[Any]]:
    """Map each endpoint to the ``method_name`` its resolved semantics declares."""
    by_method: dict[str, Endpoint[Any]] = {}
    for endpoint_name, endpoint in endpoint_map.items():
        semantics = _semantics_for(endpoint_name, semantics_map)
        if semantics is not None:
            by_method[semantics.method_name] = endpoint
    return by_method


def _selected_semantics_keys(
    endpoint_map: dict[str, Endpoint[Any]], semantics_map: dict[str, Any]
) -> set[str]:
    """Semantics keys that some endpoint-map key actually resolves to."""
    selected: set[str] = set()
    for endpoint_name in endpoint_map:
        resolved = _semantics_for(endpoint_name, semantics_map)
        if resolved is None:
            continue
        selected.update(
            key for key, value in semantics_map.items() if value is resolved
        )
    return selected


def test_alias_semantics_match_their_endpoint() -> None:
    """Alias semantics entries must hint the same params as their endpoint.

    ``test_every_endpoint_passes_registry_validation`` iterates endpoint-map
    first, so a semantics entry that no endpoint key selects is never
    validated. Those aliases are still live MCP tools -- ``company``'s
    ``intraday_price`` sits in ``DEFAULT_TOOLS`` alongside the
    ``intraday_prices`` entry that shadows it -- so their hints have to track
    the endpoint too.

    Entries whose ``method_name`` has no endpoint at all are skipped: those are
    client-side methods such as ``get_company_logo_url``, which builds a URL
    without calling the API.
    """
    drift: dict[str, str] = {}

    for group, (endpoint_map, semantics_map) in _catalog().items():
        by_method = _endpoints_by_method(endpoint_map, semantics_map)
        unselected = set(semantics_map) - _selected_semantics_keys(
            endpoint_map, semantics_map
        )

        for key in sorted(unselected):
            semantics = semantics_map[key]
            endpoint = by_method.get(semantics.method_name)
            if endpoint is None:
                continue

            params = {param.name for param in endpoint.mandatory_params}
            params.update(param.name for param in endpoint.optional_params or [])
            hints = set(semantics.parameter_hints)

            if params != hints:
                drift[f"{group}.{key}"] = (
                    f"missing={sorted(params - hints)} extra={sorted(hints - params)}"
                )

    assert drift == {}, f"Alias semantics drifted from their endpoint: {drift}"


def test_client_name_matches_owning_group() -> None:
    """``client_name`` must name the client group the semantics is registered under.

    Nothing dispatches on this field today -- MCP resolves tools through the
    module slug -- so a wrong value is silently wrong metadata rather than a
    crash. Eight company price/quote entries claimed ``market`` for exactly
    that reason.
    """
    mismatches = {
        f"{group}.{key}": semantics.client_name
        for group, config in get_endpoint_groups().items()
        for key, semantics in config["semantics_map"].items()
        if semantics.client_name != group
    }

    assert mismatches == {}, f"client_name does not match owning group: {mismatches}"
