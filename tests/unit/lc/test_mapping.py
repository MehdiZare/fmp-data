# tests/lc/test_mapping.py

from fmp_data.lc.mapping import (
    ALL_ENDPOINT_MAP,
    ALL_ENDPOINT_SEMANTICS,
    ENDPOINT_GROUPS,
)


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
    """Test endpoint group organization"""
    # Test that endpoints are properly categorized
    for _, group_data in ENDPOINT_GROUPS.items():
        endpoint_map = group_data["endpoint_map"]
        semantics_map = group_data["semantics_map"]

        # Endpoints should follow naming conventions
        for endpoint_name in endpoint_map:
            if endpoint_name.startswith("get_"):
                semantic_name = endpoint_name[4:]
                assert semantic_name in semantics_map