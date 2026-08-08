"""Guard tests: the whole endpoint catalog must register cleanly.

These catch semantics drift (missing/extra parameter hints, category
mismatches, unpaired endpoints) without needing a vector store or API key.
"""

from typing import Any

from fmp_data.lc.models import EndpointSemantics, SemanticCategory
from fmp_data.lc.registry import EndpointRegistry, get_endpoint_groups
from fmp_data.models import Endpoint

# Below the current catalog size but far above zero. An assertion over a
# comprehension is vacuously true on an empty group dict, so any guard whose
# universe is derived from ``get_endpoint_groups()`` needs a floor beneath it.
MINIMUM_SEMANTICS_CHECKED = 200


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
    """``client_name`` must name the client module the semantics is registered under.

    Nothing dispatches on this field today -- MCP resolves tools through the
    module slug -- so a wrong value is silently wrong metadata rather than a
    crash. Eight company price/quote entries claimed ``market`` for exactly
    that reason. Compared against ``config["client"]`` rather than the group
    key, since #129 a module may contribute several groups (``batch_market``,
    ``batch_fundamental``, ...) and every one of them is still ``batch``.
    """
    mismatches = {
        f"{group}.{key}": semantics.client_name
        for group, config in get_endpoint_groups().items()
        for key, semantics in config["semantics_map"].items()
        if semantics.client_name != config["client"]
    }

    assert mismatches == {}, f"client_name does not match owning group: {mismatches}"


# Client modules that MCP discovery exposes but the LangChain registry does not
# enroll. Empty since #129 brought batch, index, sec and transcripts in.
LC_EXCLUDED_CLIENTS: set[str] = set()


def test_lc_registry_covers_every_client_except_declared_exclusions() -> None:
    """A whole client module must not fall out of the LC registry unnoticed.

    Every guard in this file derives its universe from ``get_endpoint_groups()``,
    so none of them can see a module that is absent from it entirely -- the same
    silent-disappearance shape as #121, one level up. Pinning the difference
    against MCP discovery means dropping a client, or adding a 14th without
    enrolling it, fails here instead of going unnoticed.
    """
    from fmp_data.mcp.discovery import discover_all_tools

    discovered = {tool["client"] for tool in discover_all_tools()}
    registered = {config["client"] for config in get_endpoint_groups().values()}

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


def test_every_group_declares_one_category_and_its_semantics_agree() -> None:
    """A client group's category must be the one every entry in it declares.

    ``ValidationRuleRegistry.validate_category`` compares each semantics'
    ``category`` against the category of whichever rule owns the longest
    matching prefix, and a group's endpoint-map keys are exact matches for its
    own endpoints -- so its own rule always wins. One divergent entry therefore
    fails registration and drops out of the registry, which
    ``register_batch``'s skip-and-continue contract turns into a warning rather
    than a crash.

    Note this constrains the *group*, not the client module. batch declares
    five categories and sec two; #129 splits them into one group per category
    rather than rewriting the declarations, since ``category`` feeds the
    semantic search the registry exists to serve.
    """
    groups = get_endpoint_groups()
    divergent = {
        f"{group}.{key}": str(semantics.category)
        for group, config in groups.items()
        for key, semantics in config["semantics_map"].items()
        if semantics.category != config["category"]
    }

    assert divergent == {}, (
        "Semantics entries whose category differs from their group's: "
        f"{divergent}. A group carries exactly one category; pick the group "
        "the endpoint belongs to, or move the endpoint."
    )

    checked = sum(len(config["semantics_map"]) for config in groups.values())
    assert checked >= MINIMUM_SEMANTICS_CHECKED, (
        f"Only {checked} semantics entries checked across {len(groups)} groups; "
        f"expected at least {MINIMUM_SEMANTICS_CHECKED}. An empty or shrunken "
        "group dict passes the assertion above vacuously."
    )


def test_every_endpoint_routes_to_its_own_groups_category() -> None:
    """Prefix matching must hand each method back to the group that owns it.

    ``_find_matching_rule`` picks the longest prefix across every registered
    group, and prefixes are derived from method names, so near-misses across
    groups are the failure mode: ``batch.get_quotes`` sits one character away
    from ``company.get_quote``, ``batch.get_income_statement_bulk`` extends
    ``fundamental.get_income_statement``, and ``batch_market``/``index``/
    ``market`` all claim ``MARKET_DATA``. Since #129 a single client module can
    span several rules, so this also checks the partitioning did not hand one
    of batch's endpoints to a sibling batch group.
    """
    validation = EndpointRegistry().validation
    misrouted = {
        f"{group}.{name}": (
            f"routed to {validation.get_expected_category(name)}, "
            f"expected {config['category']}"
        )
        for group, config in get_endpoint_groups().items()
        for name in config["endpoint_map"]
        if validation.get_expected_category(name) != config["category"]
    }

    assert misrouted == {}, f"Endpoints claimed by the wrong group: {misrouted}"

    # The sweep above cannot separate two groups that share a category, so
    # name the near-misses explicitly. A bulk variant must not be swallowed by
    # the shorter method it extends, and vice versa.
    near_misses = {
        "get_quote": SemanticCategory.COMPANY_INFO,  # company
        "get_quotes": SemanticCategory.MARKET_DATA,  # batch_market
        "get_quotes_short": SemanticCategory.MARKET_DATA,  # batch_market
        "get_income_statement": SemanticCategory.FUNDAMENTAL_ANALYSIS,
        "get_income_statement_bulk": SemanticCategory.FUNDAMENTAL_ANALYSIS,
        "get_profile": SemanticCategory.COMPANY_INFO,  # company, not sec
        "get_profile_bulk": SemanticCategory.COMPANY_INFO,  # batch_company
        "get_etf_holder_bulk": SemanticCategory.INSTITUTIONAL,  # batch_institutional
        "get_eod_bulk": SemanticCategory.MARKET_DATA,  # batch_market
    }
    for method_name, expected in near_misses.items():
        assert validation.get_expected_category(method_name) == expected, method_name


def test_pending_collision_exclusions_are_real() -> None:
    """Every declared exclusion must be a genuine cross-client name clash.

    ``PENDING_COLLISION_EXCLUSIONS`` is the one place an endpoint can leave the
    LC registry on purpose, so it has to stay expensive to add to: each entry
    must name a method some *other* client already owns, and the excluded
    semantics still have to hint their endpoint correctly, since they remain
    live MCP tools that nothing else validates.

    It is a stopgap pending #126 and #136, which settle the tool-key namespace
    with a deprecation cycle. When those land this mapping should shrink.
    """
    import importlib

    from fmp_data.lc.registry import PENDING_COLLISION_EXCLUSIONS

    registered = get_endpoint_groups()
    owners = {
        name: config["client"]
        for config in registered.values()
        for name in config["endpoint_map"]
    }

    problems: dict[str, str] = {}
    for client, method_names in PENDING_COLLISION_EXCLUSIONS.items():
        mapping = importlib.import_module(f"fmp_data.{client}.mapping")
        endpoint_map = getattr(mapping, f"{client.upper()}_ENDPOINT_MAP")
        semantics_map = getattr(mapping, f"{client.upper()}_ENDPOINTS_SEMANTICS")

        for method_name in sorted(method_names):
            label = f"{client}.{method_name}"
            if method_name not in endpoint_map:
                problems[label] = "not in the client's endpoint map"
                continue
            owner = owners.get(method_name)
            if owner is None or owner == client:
                problems[label] = (
                    "does not collide with any registered client; drop it from "
                    "PENDING_COLLISION_EXCLUSIONS and let it register"
                )
                continue

            endpoint = endpoint_map[method_name]
            params = {param.name for param in endpoint.mandatory_params}
            params.update(param.name for param in endpoint.optional_params or [])
            semantics = next(
                s for s in semantics_map.values() if s.method_name == method_name
            )
            hints = set(semantics.parameter_hints)
            if params != hints:
                problems[label] = (
                    f"hints drifted: missing={sorted(params - hints)} "
                    f"extra={sorted(hints - params)}"
                )

    assert problems == {}, f"PENDING_COLLISION_EXCLUSIONS entries are wrong: {problems}"

    # An excluded method must actually be absent from every group, not merely
    # declared: a filter applied to the wrong map would still leave it live.
    excluded = {
        name for names in PENDING_COLLISION_EXCLUSIONS.values() for name in names
    }
    for config in registered.values():
        client = config["client"]
        client_exclusions = PENDING_COLLISION_EXCLUSIONS.get(client, frozenset())
        still_present = set(config["endpoint_map"]) & client_exclusions
        assert still_present == set(), (
            f"{client} still exposes excluded methods: {sorted(still_present)}"
        )
    assert excluded, "Exclusion list emptied -- delete the mechanism, not the test"


def test_partitioning_is_a_no_op_for_uniform_clients() -> None:
    """A client whose entries all share a category must yield one unchanged group.

    ``_partition_by_category`` replaced a hand-maintained group dict. Proving
    it reproduces that dict exactly for every uniform client -- the nine that
    predate #129, plus index and transcripts -- is what makes the derivation
    trustworthy for the two clients it does split.
    """
    import importlib

    from fmp_data.lc.registry import _partition_by_category

    uniform = [
        "alternative",
        "company",
        "economics",
        "fundamental",
        "market",
        "technical",
        "institutional",
        "intelligence",
        "investment",
        "index",
        "transcripts",
    ]

    for client in uniform:
        mapping = importlib.import_module(f"fmp_data.{client}.mapping")
        endpoint_map = getattr(mapping, f"{client.upper()}_ENDPOINT_MAP")
        semantics_map = getattr(mapping, f"{client.upper()}_ENDPOINTS_SEMANTICS")

        partitioned = _partition_by_category(client, endpoint_map, semantics_map)

        assert set(partitioned) == {client}, (
            f"{client} is no longer uniform: partitioned into "
            f"{sorted(partitioned)}. Either a category changed, or this list "
            "is stale."
        )
        config = partitioned[client]
        assert config["endpoint_map"] == endpoint_map, (
            f"{client}: partitioning changed the endpoint map; symmetric "
            f"difference: {sorted(set(config['endpoint_map']) ^ set(endpoint_map))}"
        )
        assert config["semantics_map"] == semantics_map, (
            f"{client}: partitioning changed the semantics map; symmetric "
            f"difference: {sorted(set(config['semantics_map']) ^ set(semantics_map))}"
        )
        assert config["client"] == client, (
            f"{client}: group reports client {config['client']!r}"
        )

    # And the two that do split must round-trip: no endpoint or semantics entry
    # may be lost or duplicated across the pieces.
    for client, expected_groups in (("batch", 5), ("sec", 2)):
        mapping = importlib.import_module(f"fmp_data.{client}.mapping")
        endpoint_map = getattr(mapping, f"{client.upper()}_ENDPOINT_MAP")
        semantics_map = getattr(mapping, f"{client.upper()}_ENDPOINTS_SEMANTICS")

        partitioned = _partition_by_category(client, endpoint_map, semantics_map)
        assert len(partitioned) == expected_groups, sorted(partitioned)

        endpoint_names = [
            name for config in partitioned.values() for name in config["endpoint_map"]
        ]
        semantics_keys = [
            key for config in partitioned.values() for key in config["semantics_map"]
        ]
        assert len(endpoint_names) == len(set(endpoint_names)), (
            f"{client}: endpoint duplicated across subgroups: "
            f"{sorted({n for n in endpoint_names if endpoint_names.count(n) > 1})}"
        )
        assert len(semantics_keys) == len(set(semantics_keys)), (
            f"{client}: semantics key duplicated across subgroups: "
            f"{sorted({k for k in semantics_keys if semantics_keys.count(k) > 1})}"
        )

        # Everything survives except the declared exclusions.
        from fmp_data.lc.registry import PENDING_COLLISION_EXCLUSIONS

        excluded = PENDING_COLLISION_EXCLUSIONS.get(client, frozenset())
        expected_endpoints = set(endpoint_map) - excluded
        assert set(endpoint_names) == expected_endpoints, (
            f"{client}: endpoints lost or invented by partitioning; symmetric "
            f"difference: {sorted(set(endpoint_names) ^ expected_endpoints)}"
        )
        expected_keys = {
            key
            for key, entry in semantics_map.items()
            if entry.method_name not in excluded
        }
        assert set(semantics_keys) == expected_keys, (
            f"{client}: semantics entries lost or invented by partitioning; "
            f"symmetric difference: {sorted(set(semantics_keys) ^ expected_keys)}"
        )


def test_every_category_has_a_group_slug() -> None:
    """Adding a ``SemanticCategory`` must not silently break group naming.

    ``_partition_by_category`` indexes ``_CATEGORY_SLUGS`` directly, so a
    missing entry is a ``KeyError`` at import time for whichever client first
    declares the new category -- which could be none of them today and all of
    them after one edit.
    """
    from fmp_data.lc.registry import _CATEGORY_SLUGS

    missing = [
        category for category in SemanticCategory if category not in _CATEGORY_SLUGS
    ]
    assert missing == [], f"SemanticCategory members without a group slug: {missing}"

    slugs = list(_CATEGORY_SLUGS.values())
    assert len(slugs) == len(set(slugs)), f"Duplicate group slugs: {slugs}"
