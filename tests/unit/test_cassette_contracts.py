from __future__ import annotations

import importlib
import inspect
import json
from pathlib import Path
import pkgutil
import re
from urllib.parse import urlparse

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
            "record cassettes first to enable contract validation."
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
