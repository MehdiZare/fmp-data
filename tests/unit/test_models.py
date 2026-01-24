# tests/unit/test_models.py
"""Tests for the models module, particularly the validate_params method."""

import pytest

from fmp_data.exceptions import ValidationError
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    ParamLocation,
    ParamType,
)


class TestValidateParams:
    """Tests for the Endpoint.validate_params method."""

    @pytest.fixture
    def sample_endpoint(self):
        """Create a sample endpoint for testing."""
        return Endpoint(
            name="test_endpoint",
            path="test/path",
            version=APIVersion.STABLE,
            description="A test endpoint",
            mandatory_params=[
                EndpointParam(
                    name="symbol",
                    location=ParamLocation.QUERY,
                    param_type=ParamType.STRING,
                    required=True,
                    description="Stock symbol",
                )
            ],
            optional_params=[
                EndpointParam(
                    name="start_date",
                    location=ParamLocation.QUERY,
                    param_type=ParamType.DATE,
                    required=False,
                    description="Start date",
                    alias="from",
                ),
                EndpointParam(
                    name="end_date",
                    location=ParamLocation.QUERY,
                    param_type=ParamType.DATE,
                    required=False,
                    description="End date",
                    alias="to",
                ),
                EndpointParam(
                    name="limit",
                    location=ParamLocation.QUERY,
                    param_type=ParamType.INTEGER,
                    required=False,
                    description="Number of results",
                    default=100,
                ),
            ],
            response_model=dict,
        )

    def test_accepts_canonical_name(self, sample_endpoint):
        """Test that validate_params accepts canonical parameter names."""
        result = sample_endpoint.validate_params(
            {
                "symbol": "AAPL",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            }
        )

        assert result["symbol"] == "AAPL"
        # Wire keys should use aliases
        assert result["from"].strftime("%Y-%m-%d") == "2024-01-01"
        assert result["to"].strftime("%Y-%m-%d") == "2024-12-31"

    def test_accepts_alias_as_input(self, sample_endpoint):
        """Test that validate_params accepts parameter aliases as input keys."""
        result = sample_endpoint.validate_params(
            {
                "symbol": "AAPL",
                "from": "2024-01-01",
                "to": "2024-12-31",
            }
        )

        assert result["symbol"] == "AAPL"
        # Wire keys should use aliases
        assert result["from"].strftime("%Y-%m-%d") == "2024-01-01"
        assert result["to"].strftime("%Y-%m-%d") == "2024-12-31"

    def test_none_values_excluded(self, sample_endpoint):
        """Test that None values for optional params are excluded from result."""
        result = sample_endpoint.validate_params(
            {
                "symbol": "AAPL",
                "start_date": None,
                "end_date": None,
            }
        )

        assert result["symbol"] == "AAPL"
        assert "from" not in result
        assert "to" not in result
        # Default for limit should still be applied
        assert result["limit"] == 100

    def test_unknown_keys_ignored_by_default(self, sample_endpoint):
        """Test that unknown parameter keys are silently ignored by default."""
        result = sample_endpoint.validate_params(
            {
                "symbol": "AAPL",
                "unknown_param": "some_value",
                "another_unknown": 123,
            }
        )

        assert result["symbol"] == "AAPL"
        assert "unknown_param" not in result
        assert "another_unknown" not in result

    def test_strict_mode_raises_on_unknown_keys(self, sample_endpoint):
        """Test that strict mode raises ValidationError on unknown keys."""
        with pytest.raises(ValidationError, match="Unknown parameter: unknown_param"):
            sample_endpoint.validate_params(
                {"symbol": "AAPL", "unknown_param": "some_value"}, strict=True
            )

    def test_defaults_are_validated(self, sample_endpoint):
        """Test that default values are validated through param.validate_value."""
        result = sample_endpoint.validate_params({"symbol": "AAPL"})

        # The default limit value should be applied
        assert result["limit"] == 100
        # Dates should not be present since they have no defaults
        assert "from" not in result
        assert "to" not in result

    def test_missing_mandatory_raises(self, sample_endpoint):
        """Test that missing mandatory params raise ValidationError."""
        with pytest.raises(
            ValidationError, match="Missing mandatory parameter: symbol"
        ):
            sample_endpoint.validate_params({"start_date": "2024-01-01"})

    def test_both_name_and_alias_provided(self, sample_endpoint):
        """Test that when both name and alias are provided, we don't duplicate."""
        result = sample_endpoint.validate_params(
            {
                "symbol": "AAPL",
                "start_date": "2024-01-01",
                # This should be ignored since start_date is first
                "from": "2024-06-01",
            }
        )

        assert result["symbol"] == "AAPL"
        # First one seen (start_date) should win
        assert result["from"].strftime("%Y-%m-%d") == "2024-01-01"

    def test_type_conversion_works(self, sample_endpoint):
        """Test that values are properly type-converted."""
        result = sample_endpoint.validate_params(
            {
                "symbol": "AAPL",
                "limit": "50",  # String should be converted to int
            }
        )

        assert result["limit"] == 50
        assert isinstance(result["limit"], int)

    def test_mandatory_param_with_none_raises(self, sample_endpoint):
        """Test that mandatory params with None value still raise ValidationError."""
        with pytest.raises(ValidationError, match="Missing required parameter: symbol"):
            sample_endpoint.validate_params({"symbol": None})


class TestBuildParamLookup:
    """Tests for the _build_param_lookup helper method."""

    def test_lookup_contains_names_and_aliases(self):
        """Test that lookup contains both param names and aliases."""
        endpoint = Endpoint(
            name="test",
            path="test",
            version=APIVersion.STABLE,
            description="Test",
            mandatory_params=[
                EndpointParam(
                    name="symbol",
                    location=ParamLocation.QUERY,
                    param_type=ParamType.STRING,
                    required=True,
                    description="Symbol",
                )
            ],
            optional_params=[
                EndpointParam(
                    name="start_date",
                    location=ParamLocation.QUERY,
                    param_type=ParamType.DATE,
                    required=False,
                    description="Start date",
                    alias="from",
                )
            ],
            response_model=dict,
        )

        lookup = endpoint._build_param_lookup()

        assert "symbol" in lookup
        assert "start_date" in lookup
        assert "from" in lookup
        # Both should point to the same param
        assert lookup["start_date"] is lookup["from"]
