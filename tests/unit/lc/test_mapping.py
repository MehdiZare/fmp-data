# tests/lc/test_mapping.py

from typing import Any, cast

from fmp_data.lc.mapping import (
    ALL_ENDPOINT_MAP,
    ALL_ENDPOINT_SEMANTICS,
    ENDPOINT_GROUPS,
)
from fmp_data.lc.models import EndpointSemantics
from fmp_data.lc.registry import resolve_semantics_for_endpoint
from fmp_data.models import Endpoint


def test_endpoint_mappings():
    """Test endpoint mappings"""
    # Test ALL_ENDPOINT_SEMANTICS
    assert isinstance(ALL_ENDPOINT_SEMANTICS, dict)
    assert len(ALL_ENDPOINT_SEMANTICS) > 0

    # Test ALL_ENDPOINT_MAP
    assert isinstance(ALL_ENDPOINT_MAP, dict)
    assert len(ALL_ENDPOINT_MAP) > 0


def test_endpoint_groups():
    """Test endpoint groups structure"""
    assert isinstance(ENDPOINT_GROUPS, dict)

    # Test required keys in each group
    required_keys = {"endpoint_map", "semantics_map", "display_name"}
    for _, group_data in ENDPOINT_GROUPS.items():
        assert isinstance(group_data, dict)
        assert set(group_data.keys()) == required_keys


def test_endpoint_consistency():
    """Test endpoint mapping consistency"""
    from fmp_data.lc.mapping import ALL_ENDPOINT_MAP, ALL_ENDPOINT_SEMANTICS
    from fmp_data.lc.models import EndpointSemantics, SemanticCategory

    # Make copy to avoid modifying original
    semantics_map = dict(ALL_ENDPOINT_SEMANTICS)

    # Add missing crypto endpoints
    for endpoint_name in ALL_ENDPOINT_MAP:
        if endpoint_name not in semantics_map:
            base_name = (
                endpoint_name.replace("get_", "", 1)
                if endpoint_name.startswith("get_")
                else endpoint_name
            )
            semantics_map[endpoint_name] = EndpointSemantics(
                client_name="alternative",
                method_name=endpoint_name,
                category=SemanticCategory.ALTERNATIVE_DATA,
                natural_description=f"Get {base_name} data",
                example_queries=[f"Get {base_name} information"],
                parameter_hints={},
                response_hints={},
                related_terms=[base_name],
                use_cases=[f"{base_name} analysis"],
            )

    # Now test with complete mapping
    for endpoint_name in ALL_ENDPOINT_MAP:
        assert endpoint_name in semantics_map


def test_endpoint_group_organization():
    """Every endpoint in every group must resolve to a semantics entry.

    Resolution goes through :func:`resolve_semantics_for_endpoint`, the same
    function ``setup_registry`` uses, rather than a local reimplementation of
    it. This test used to strip a leading ``get_`` and look the remainder up
    directly -- rule 2 of three. An endpoint-map key that resolves by rule 1
    (exact match) or rule 3 (``EndpointSemantics.method_name``) therefore read
    as *missing* here while registering perfectly well in the real registry,
    which is what ``get_form_13f_by_quarter`` hit in #188. A guard that
    reimplements the rule it is guarding fails on correct code and, worse,
    would pass on code the resolver rejects.
    """
    errors = []

    for group_name, group_data in ENDPOINT_GROUPS.items():
        # ENDPOINT_GROUPS mixes maps with a `display_name` string, so its value
        # type is heterogeneous and a cast is unavoidable -- but cast to the
        # real element types, not Any, so the contents stay type-checked.
        endpoint_map = cast(dict[str, Endpoint[Any]], group_data["endpoint_map"])
        semantics_map = cast(dict[str, EndpointSemantics], group_data["semantics_map"])

        unresolved = [
            endpoint_name
            for endpoint_name in endpoint_map
            if resolve_semantics_for_endpoint(endpoint_name, semantics_map) is None
        ]

        if unresolved:
            errors.append(
                f"\nGroup '{group_name}' is missing semantic mappings for:\n"
                f"  Endpoints: {unresolved}\n"
                f"  Available semantic mappings: {list(semantics_map.keys())}"
            )

    # If we collected any errors, raise AssertionError with detailed message
    if errors:
        raise AssertionError(
            "Found endpoints without corresponding semantic mappings:\n"
            + "\n".join(errors)
            + "\nEvery endpoint-map key must resolve via "
            "resolve_semantics_for_endpoint (exact key, get_-stripped key, or "
            "a semantics entry whose method_name matches)."
        )
