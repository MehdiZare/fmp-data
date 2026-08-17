from __future__ import annotations

import importlib
import inspect
import json
from pathlib import Path
import pkgutil
import re
from urllib.parse import urlparse

from pydantic import BaseModel
from pydantic.alias_generators import to_camel
import pytest
import yaml

from fmp_data.base import BaseClient
from fmp_data.fundamental.models import AsReportedFinancialStatementBase
from fmp_data.models import Endpoint, URLType


def _collect_endpoints() -> list[Endpoint]:
    endpoints: list[Endpoint] = []
    for _, modname, _ in pkgutil.walk_packages(["fmp_data"], prefix="fmp_data."):
        if modname.startswith("fmp_data.mcp"):
            continue
        if not modname.endswith(".endpoints"):
            continue
        module = importlib.import_module(modname)
        for _, obj in inspect.getmembers(module):
            if isinstance(obj, Endpoint):
                endpoints.append(obj)
    return endpoints


def _endpoint_path_patterns(endpoint: Endpoint) -> list[str]:
    endpoint_path = endpoint.path.strip("/")
    patterns: list[str] = []
    if endpoint.url_type == URLType.API and endpoint.version is not None:
        patterns.append(f"/{endpoint.version.value}/{endpoint_path}")
    elif endpoint.url_type == URLType.IMAGE:
        patterns.append(f"/{endpoint.url_type.value}/{endpoint_path}")
    else:
        patterns.append(f"/{endpoint_path}")
    return patterns


def _matches_path(pattern: str, actual_path: str) -> bool:
    tokenized = re.sub(r"\{[^}]+\}", r"[^/]+", pattern)
    return re.fullmatch(tokenized, actual_path) is not None


CONTRACTS_PATH = Path("tests/integration/cassette_contracts.json")


def _load_committed_contracts() -> list[dict]:
    payload = json.loads(CONTRACTS_PATH.read_text(encoding="utf-8"))
    return list(payload["cassettes"])


def _declared_wire_names(model: type[BaseModel]) -> set[str]:
    """Field names plus aliases pydantic will actually bind."""
    names: set[str] = set()
    for name, field in model.model_fields.items():
        names.add(name)
        if field.alias:
            names.add(str(field.alias))
        if field.serialization_alias:
            names.add(str(field.serialization_alias))
        validation_alias = field.validation_alias
        if isinstance(validation_alias, str):
            names.add(validation_alias)
        elif validation_alias is not None and hasattr(validation_alias, "choices"):
            names.update(str(choice) for choice in validation_alias.choices)
    return names


def test_committed_cassette_contracts_match_models() -> None:
    """CI has no YAML; the committed snapshot must still fail on alias drift (#336)."""
    contracts = _load_committed_contracts()
    assert contracts, f"{CONTRACTS_PATH} has no cassette entries"

    missing: list[str] = []
    for entry in contracts:
        module_name, _, class_name = entry["model"].rpartition(".")
        model = getattr(importlib.import_module(module_name), class_name)
        assert issubclass(model, BaseModel)
        declared = _declared_wire_names(model)
        for alias in entry["required_aliases"]:
            if alias not in declared:
                missing.append(
                    f"{entry['path']}: {entry['model']} missing alias {alias!r}"
                )
    assert not missing, "Committed cassette contract drift:\n  " + "\n  ".join(missing)


def test_committed_contract_endpoints_exist() -> None:
    """Snapshot endpoint names must still resolve in intelligence.endpoints."""
    import fmp_data.intelligence.endpoints as intel_endpoints

    missing = [
        entry["endpoint"]
        for entry in _load_committed_contracts()
        if not hasattr(intel_endpoints, str(entry["endpoint"]).upper())
    ]
    assert not missing, f"unknown contract endpoints: {missing}"


def test_committed_contracts_include_a_non_generated_alias() -> None:
    """The snapshot is vacuous if every required alias is to_camel(field)."""
    canaries: list[str] = []
    for entry in _load_committed_contracts():
        module_name, _, class_name = entry["model"].rpartition(".")
        model = getattr(importlib.import_module(module_name), class_name)
        generated = set(model.model_fields)
        generated.update(to_camel(name) for name in model.model_fields)
        for alias in entry["required_aliases"]:
            if alias not in generated:
                canaries.append(f"{class_name}.{alias}")
    assert canaries, (
        "every required alias is a field name or to_camel(field); "
        "the snapshot would stay green if those Field aliases were dropped"
    )


def test_vcr_cassettes_match_endpoint_models() -> None:  # noqa: C901
    """Validate JSON cassette payloads against declared endpoint response models."""
    endpoints = _collect_endpoints()
    assert endpoints, "No endpoints discovered for cassette contract validation."

    cassettes_root = Path("tests/integration/vcr_cassettes")
    cassette_files = (
        sorted(cassettes_root.rglob("*.yaml")) if cassettes_root.exists() else []
    )
    if not cassette_files:
        pytest.skip(
            "No VCR cassette YAML files found — "
            "record cassettes first to enable payload contract validation. "
            "Alias drift is still checked by "
            "test_committed_cassette_contracts_match_models."
        )

    unmatched_requests: list[str] = []
    validation_issues: list[str] = []
    extra_fields_report: list[str] = []

    for cassette_path in cassette_files:
        cassette = yaml.safe_load(cassette_path.read_text())
        interactions = (
            cassette.get("interactions", []) if isinstance(cassette, dict) else []
        )

        for interaction in interactions:
            request = interaction.get("request", {})
            response = interaction.get("response", {})
            status_code = (response.get("status") or {}).get("code")
            if not isinstance(status_code, int) or not (200 <= status_code < 300):
                continue

            method = (request.get("method") or "").upper()
            uri = request.get("uri") or ""
            if not method or not uri:
                continue

            path = urlparse(uri).path
            endpoint_match: Endpoint | None = None
            for endpoint in endpoints:
                if endpoint.method.value != method:
                    continue
                patterns = _endpoint_path_patterns(endpoint)
                if any(_matches_path(pattern, path) for pattern in patterns):
                    endpoint_match = endpoint
                    break

            if endpoint_match is None:
                unmatched_requests.append(f"{cassette_path}: {method} {path}")
                continue

            body = (response.get("body") or {}).get("string")
            if isinstance(body, bytes):
                try:
                    body = body.decode()
                except UnicodeDecodeError:
                    continue
            if not isinstance(body, str):
                continue

            text = body.strip()
            if not text:
                continue

            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                # Skip non-JSON payloads (e.g., binary XLSX responses)
                continue

            try:
                result = BaseClient._process_response(
                    endpoint_match, payload, validation_mode="warn"
                )
                # Collect extra fields from parsed models.
                # AsReported models merge a dynamic SEC "data" payload whose
                # keys are raw XBRL taxonomy names that vary per company/filing
                # and cannot be pre-defined -- skip them.
                items = result if isinstance(result, list) else [result]
                for item in items:
                    if isinstance(item, AsReportedFinancialStatementBase):
                        continue
                    extra = getattr(item, "__pydantic_extra__", None)
                    if extra:
                        extra_fields_report.append(
                            f"{cassette_path.name}: endpoint={endpoint_match.name} "
                            f"model={type(item).__name__} "
                            f"extra_fields={sorted(extra.keys())}"
                        )
                        break  # one example per cassette interaction is enough
            except Exception as exc:  # pragma: no cover - failures are asserted below
                validation_issues.append(
                    f"{cassette_path}: endpoint={endpoint_match.name} "
                    f"error={type(exc).__name__} message={exc}"
                )

    assert not unmatched_requests, "Unmatched cassette requests:\n" + "\n".join(
        unmatched_requests[:50]
    )
    assert not validation_issues, "Cassette validation issues:\n" + "\n".join(
        validation_issues[:50]
    )
    assert not extra_fields_report, (
        f"Found {len(extra_fields_report)} model(s) with uncaptured fields:\n"
        + "\n".join(f"  - {r}" for r in extra_fields_report)
    )
