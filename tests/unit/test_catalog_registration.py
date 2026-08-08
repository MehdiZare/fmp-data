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
    paired = 0

    for group, (endpoint_map, semantics_map) in _catalog().items():
        batch = {}
        for endpoint_name, endpoint in endpoint_map.items():
            semantics = _semantics_for(endpoint_name, semantics_map)
            if semantics is not None:
                batch[endpoint_name] = (endpoint, semantics)

        # Count what was actually handed to the registry. Counting every
        # endpoint-map key instead would make a *missing semantics* entry
        # surface below as a bogus "name collision".
        paired += len(batch)

        for name, error in registry.register_batch(batch).items():
            failures[f"{group}.{name}"] = error

    assert failures == {}, f"Endpoints failing validation: {failures}"
    assert len(registry.list_endpoints()) == paired, (
        "Endpoint name collision across client groups: "
        f"{paired} endpoints registered but only "
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


# Semantics entries that legitimately have no endpoint: client-side methods
# that build a result without calling the API.
CLIENT_SIDE_METHODS = {"company.company_logo_url"}


def _orphan_semantics() -> set[str]:
    """Semantics entries whose ``method_name`` has no endpoint behind it."""
    return {
        f"{group}.{key}"
        for group, (endpoint_map, semantics_map) in _catalog().items()
        for key, semantics in semantics_map.items()
        if semantics.method_name
        not in _endpoints_by_method(endpoint_map, semantics_map)
    }


def test_every_semantics_entry_has_an_endpoint() -> None:
    """Deleting an endpoint from a client's map must fail, not go unnoticed.

    Every other guard here iterates the endpoint map, so removing an entry from
    it just shrinks the universe they check -- the catalog silently gets smaller
    and the whole suite stays green. That is the #121 regression class this file
    exists to catch, so it needs an assertion that looks the other way, from
    semantics to endpoints.
    """
    assert _orphan_semantics() == CLIENT_SIDE_METHODS, (
        "Semantics entries with no endpoint behind them. A new name here "
        "usually means an endpoint map lost an entry, which drops it from the "
        "LC registry silently; add it to CLIENT_SIDE_METHODS only if the "
        "method genuinely makes no API call."
    )


def test_alias_semantics_match_their_endpoint() -> None:
    """Alias semantics entries must hint the same params as their endpoint.

    ``test_every_endpoint_passes_registry_validation`` iterates endpoint-map
    first, so a semantics entry that no endpoint key selects is never
    validated. Those aliases are still resolvable MCP tools -- ``company``'s
    ``intraday_price`` is deprecated rather than deleted, and keeps resolving
    to the same method as ``intraday_prices`` until 3.0 -- so their hints have
    to track the endpoint for as long as they still answer.

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
                # Only client-side methods may land here; anything else means
                # an endpoint map lost an entry, which
                # test_every_semantics_entry_has_an_endpoint asserts exactly.
                continue

            params = {param.name for param in endpoint.mandatory_params}
            params.update(param.name for param in endpoint.optional_params or [])
            hints = set(semantics.parameter_hints)

            if params != hints:
                drift[f"{group}.{key}"] = (
                    f"missing={sorted(params - hints)} extra={sorted(hints - params)}"
                )

            # Aliases are live MCP tools, so their category has to track the
            # entry that selects the same endpoint -- validation never sees an
            # unselected alias, so nothing else would catch a wrong one.
            selected = next(
                (
                    other
                    for other_key, other in semantics_map.items()
                    if other_key != key and other.method_name == semantics.method_name
                ),
                None,
            )
            if selected is not None and selected.category != semantics.category:
                drift[f"{group}.{key}"] = (
                    f"category={semantics.category} but the endpoint's selected "
                    f"semantics declares {selected.category}"
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


# Client modules that MCP discovery exposes but the LangChain registry does not
# enroll. Tracked in #129 -- registering them means filling 33 missing parameter
# hints at the same time, or the guards above go red in between.
LC_EXCLUDED_CLIENTS = {"batch", "index", "sec", "transcripts"}


def test_lc_registry_covers_every_client_except_declared_exclusions() -> None:
    """A whole client module must not fall out of the LC registry unnoticed.

    Every guard in this file derives its universe from ``get_endpoint_groups()``,
    so none of them can see a module that is absent from it entirely -- the same
    silent-disappearance shape as #121, one level up. Pinning the difference
    against MCP discovery means dropping a 10th group, or adding a 14th client
    without enrolling it, fails here instead of going unnoticed.
    """
    from fmp_data.mcp.discovery import discover_all_tools

    discovered = {tool["client"] for tool in discover_all_tools()}
    registered = set(get_endpoint_groups())

    assert discovered - registered == LC_EXCLUDED_CLIENTS, (
        "LC registry coverage changed. Clients known to MCP but missing from "
        f"the registry: {sorted(discovered - registered)}; expected exactly "
        f"{sorted(LC_EXCLUDED_CLIENTS)}. Update LC_EXCLUDED_CLIENTS only when "
        "the exclusion is deliberate."
    )
    assert registered - discovered == set(), (
        "Registry has client groups MCP discovery does not know about: "
        f"{sorted(registered - discovered)}"
    )
