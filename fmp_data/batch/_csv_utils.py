"""Shared CSV parsing utilities for batch operations."""

import csv
import io
import logging
from typing import Any, TypeVar, get_args, get_origin

from pydantic import AnyHttpUrl, BaseModel, HttpUrl
from pydantic import ValidationError as PydanticValidationError

from fmp_data.base import BaseClient, ValidationMode
from fmp_data.exceptions import ValidationError

logger = logging.getLogger(__name__)
ModelT = TypeVar("ModelT", bound=BaseModel)


def parse_csv_rows(raw: bytes) -> list[dict[str, Any]]:
    """
    Parse raw CSV bytes into dict rows.

    Args:
        raw: Raw CSV data as bytes

    Returns:
        List of dictionaries, one per CSV row (excluding empty rows)
    """
    text = raw.decode("utf-8").strip()
    if not text:
        return []
    reader = csv.DictReader(io.StringIO(text))
    rows: list[dict[str, Any]] = []
    for row in reader:
        if not row or all(value in (None, "", " ") for value in row.values()):
            continue
        normalized: dict[str, str | None] = {}
        for key, value in row.items():
            if value is None:
                normalized[key] = None
                continue
            stripped = value.strip()
            normalized[key] = stripped if stripped else None
        rows.append(normalized)
    return rows


def parse_csv_models(
    raw: bytes,
    model: type[ModelT],
    *,
    validation_mode: ValidationMode = "warn",
    endpoint_name: str | None = None,
) -> list[ModelT]:
    """
    Convert CSV rows to Pydantic models.

    Unknown headers follow the same ``FMP_VALIDATION_MODE`` policy as JSON
    extras (``warn`` / ``strict`` / ``lenient``), keyed per endpoint + field
    set. Invalid cells keep the existing URL-field retry, then either skip the
    row (``lenient`` / ``warn``) or fail the request (``strict``).

    Args:
        raw: Raw CSV data as bytes
        model: Pydantic model class to validate against
        validation_mode: Same policy as JSON (``FMP_VALIDATION_MODE``)
        endpoint_name: Bulk endpoint name used to key unknown-field warnings

    Returns:
        List of validated model instances
    """
    return parse_csv_model_rows(
        parse_csv_rows(raw),
        model,
        validation_mode=validation_mode,
        endpoint_name=endpoint_name,
    )


def parse_csv_model_rows(
    rows: list[dict[str, Any]],
    model: type[ModelT],
    *,
    validation_mode: ValidationMode = "warn",
    endpoint_name: str | None = None,
) -> list[ModelT]:
    """Validate already-parsed CSV dict rows with the JSON extras policy."""
    source = endpoint_name or model.__name__
    results: list[ModelT] = []
    url_fields = get_url_fields(model)
    for row in rows:
        try:
            results.append(
                _validate_csv_row(
                    row,
                    model,
                    url_fields=url_fields,
                    validation_mode=validation_mode,
                    endpoint_name=source,
                )
            )
        except PydanticValidationError as exc:
            if validation_mode == "strict":
                raise ValidationError(
                    f"Invalid CSV row for endpoint '{source}': {exc}"
                ) from exc
            logger.warning(
                "Skipping invalid %s row: %s",
                model.__name__,
                exc,
            )
    return results


def _validate_csv_row(
    row: dict[str, Any],
    model: type[ModelT],
    *,
    url_fields: set[str],
    validation_mode: ValidationMode,
    endpoint_name: str,
) -> ModelT:
    """Validate one row, retrying failed URL fields as ``None``."""
    try:
        parsed = BaseClient._validate_model(endpoint_name, model, row, validation_mode)
    except PydanticValidationError as exc:
        if not url_fields:
            raise
        retry_row = dict(row)
        retried = False
        for error in exc.errors():
            if not error.get("loc"):
                continue
            field = error["loc"][0]
            if isinstance(field, str) and field in url_fields:
                retry_row[field] = None
                retried = True
        if not retried:
            raise
        parsed = BaseClient._validate_model(
            endpoint_name, model, retry_row, validation_mode
        )
    return parsed  # type: ignore[return-value]


def get_url_fields(model: type[BaseModel]) -> set[str]:
    """
    Detect URL-annotated fields in a model.

    Args:
        model: Pydantic model class

    Returns:
        Set of field names that have URL type annotations
    """
    url_fields: set[str] = set()
    model_fields = getattr(model, "model_fields", None)
    if not model_fields:
        return url_fields
    for name, field in model_fields.items():
        if is_url_annotation(field.annotation):
            url_fields.add(name)
    return url_fields


def is_url_annotation(annotation: Any) -> bool:
    """
    Check if annotation is a URL type.

    Supports direct URL types (HttpUrl, AnyHttpUrl) and generic containers
    like Optional[HttpUrl], list[HttpUrl], etc.

    Args:
        annotation: Type annotation to check

    Returns:
        True if the annotation involves a URL type
    """
    origin = get_origin(annotation)
    if origin is None:
        return annotation in {AnyHttpUrl, HttpUrl}
    # For list or other generic types, check args recursively
    return any(is_url_annotation(arg) for arg in get_args(annotation))
