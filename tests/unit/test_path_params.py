"""Path params cannot walk the URL (#252 FMP-SEC-010)."""

from __future__ import annotations

import pytest

from fmp_data.company.endpoints import INTRADAY_PRICE
from fmp_data.exceptions import ValidationError
from fmp_data.models import _safe_path_segment


def test_company_intraday_interval_is_whitelisted() -> None:
    assert INTRADAY_PRICE.mandatory_params[0].valid_values == [
        "1min",
        "5min",
        "15min",
        "30min",
        "1hour",
        "4hour",
    ]
    with pytest.raises(ValidationError, match="Must be one of"):
        INTRADAY_PRICE.validate_params(
            {"interval": "../../stable/profile", "symbol": "AAPL"}
        )


def test_safe_path_segment_rejects_traversal() -> None:
    with pytest.raises(ValidationError, match="not allowed"):
        _safe_path_segment("../../stable/profile")
    with pytest.raises(ValidationError, match="not allowed"):
        _safe_path_segment("%2e%2e/%2e%2e/stable/profile")
    assert _safe_path_segment("1min") == "1min"


def test_safe_path_segment_rejects_encoded_separators_without_a_literal() -> None:
    """Encoded / and \\ must be rejected even when the raw string has none."""
    with pytest.raises(ValidationError, match="not allowed"):
        _safe_path_segment("%2fstable")
    with pytest.raises(ValidationError, match="not allowed"):
        _safe_path_segment("%2Fstable")
    with pytest.raises(ValidationError, match="not allowed"):
        _safe_path_segment("%5cstable")
    with pytest.raises(ValidationError, match="not allowed"):
        _safe_path_segment(".")
    with pytest.raises(ValidationError, match="not allowed"):
        _safe_path_segment("..")
