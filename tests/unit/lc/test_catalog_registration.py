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
    """Every paired endpoint must survive EndpointRegistry validation."""
    failures: dict[str, str] = {}

    for group, (endpoint_map, semantics_map) in _catalog().items():
        registry = EndpointRegistry()
        batch = {}
        for endpoint_name, endpoint in endpoint_map.items():
            semantics = _semantics_for(endpoint_name, semantics_map)
            if semantics is not None:
                batch[endpoint_name] = (endpoint, semantics)

        for name, error in registry.register_batch(batch).items():
            failures[f"{group}.{name}"] = error

    assert failures == {}, f"Endpoints failing validation: {failures}"
