"""Shared CSV parsing utilities for batch operations."""

import csv
import io
import logging
from typing import Any, TypeVar, get_args, get_origin

from pydantic import AnyHttpUrl, BaseModel, HttpUrl
from pydantic import ValidationError as PydanticValidationError

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


def parse_csv_models(raw: bytes, model: type[ModelT]) -> list[ModelT]:
    """
    Convert CSV rows to Pydantic models.

    Handles URL validation errors by retrying with None for failed URL fields.

    Args:
        raw: Raw CSV data as bytes
        model: Pydantic model class to validate against

    Returns:
        List of validated model instances (invalid rows are logged and skipped)
    """
    results: list[ModelT] = []
    url_fields = get_url_fields(model)
    for row in parse_csv_rows(raw):
        try:
            results.append(model.model_validate(row))
        except PydanticValidationError as exc:
            if url_fields:
                retry_row = dict(row)
                for error in exc.errors():
                    if not error.get("loc"):
                        continue
                    field = error["loc"][0]
                    if isinstance(field, str) and field in url_fields:
                        retry_row[field] = None
                try:
                    results.append(model.model_validate(retry_row))
                    continue
                except PydanticValidationError:
                    pass
            logger.warning(
                "Skipping invalid %s row: %s",
                model.__name__,
                exc,
            )
    return results


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
