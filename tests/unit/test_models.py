# tests/unit/test_models.py
"""Tests for the models module, particularly the validate_params method."""

from typing import Annotated, Any, get_args, get_origin

from pydantic import BaseModel, Field
from pydantic import ValidationError as PydanticValidationError
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

    def test_unknown_keys_warn_policy(self, sample_endpoint) -> None:
        """Test warn policy emits warning for unknown keys."""
        with pytest.warns(UserWarning, match="Unknown parameter 'unknown_param'"):
            result = sample_endpoint.validate_params(
                {"symbol": "AAPL", "unknown_param": "some_value"},
                unknown_param_policy="warn",
            )

        assert result["symbol"] == "AAPL"
        assert "unknown_param" not in result

    def test_unknown_keys_error_policy(self, sample_endpoint) -> None:
        """Test explicit error policy raises ValidationError."""
        with pytest.raises(ValidationError, match="Unknown parameter: unknown_param"):
            sample_endpoint.validate_params(
                {"symbol": "AAPL", "unknown_param": "some_value"},
                unknown_param_policy="error",
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
        endpoint: Endpoint[Any] = Endpoint(
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


def _field_uses_cik_coercer(field: Any) -> bool:
    """Detect the CIK BeforeValidator on a pydantic FieldInfo.

    Pydantic surfaces Annotated metadata on ``field.metadata`` only when the
    field is required. For ``CIK | None`` the Annotated is nested inside
    Optional and ``field.metadata`` is EMPTY, so a metadata-only check
    passes vacuously for every optional field. Both places must be checked.
    """
    from fmp_data.models import _coerce_cik

    if any(getattr(m, "func", None) is _coerce_cik for m in field.metadata):
        return True
    stack = [field.annotation]
    while stack:
        current = stack.pop()
        if get_origin(current) is Annotated:
            args = get_args(current)
            if any(getattr(m, "func", None) is _coerce_cik for m in args[1:]):
                return True
            stack.append(args[0])
        else:
            stack.extend(get_args(current))
    return False


class TestCIKCoercion:
    """CIK is a fixed-width zero-padded identifier, not a number."""

    def test_int_is_zero_padded_to_ten_digits(self) -> None:
        from fmp_data.models import CIK, default_model_config

        class Model(BaseModel):
            model_config = default_model_config
            cik: CIK | None = Field(default=None)

        assert Model(cik=320193).cik == "0000320193"
        assert Model(cik=1067983).cik == "0001067983"

    def test_string_passes_through_untouched(self) -> None:
        from fmp_data.models import CIK, default_model_config

        class Model(BaseModel):
            model_config = default_model_config
            cik: CIK | None = Field(default=None)

        # Already canonical: unchanged.
        assert Model(cik="0000320193").cik == "0000320193"
        # Unpadded string: NOT re-padded — we do not rewrite what the API sent.
        assert Model(cik="320193").cik == "320193"

    def test_none_is_preserved(self) -> None:
        from fmp_data.models import CIK, default_model_config

        class Model(BaseModel):
            model_config = default_model_config
            cik: CIK | None = Field(default=None)

        assert Model().cik is None
        assert Model(cik=None).cik is None

    def test_required_cik_stays_required(self) -> None:
        from fmp_data.models import CIK, default_model_config

        class Model(BaseModel):
            model_config = default_model_config
            cik: CIK = Field(description="CIK number")

        assert Model(cik=320193).cik == "0000320193"
        with pytest.raises(PydanticValidationError):
            Model()  # type: ignore[call-arg]

    def test_bool_is_not_treated_as_int(self) -> None:
        """bool is a subclass of int; padding True to '0000000001' is nonsense."""
        from fmp_data.models import CIK, default_model_config

        class Model(BaseModel):
            model_config = default_model_config
            cik: CIK | None = Field(default=None)

        with pytest.raises(PydanticValidationError):
            Model(cik=True)

    def test_no_model_declares_a_bare_str_cik(self) -> None:
        """Every cik field must route through the CIK coercer.

        A bare ``str`` annotation rejects an integer CIK before
        validation_mode is ever consulted, so one drifted model
        reintroduces the whole bug class.
        """
        import importlib
        import pkgutil

        import fmp_data

        offenders: list[str] = []
        for module_info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
            if not module_info.name.endswith(".models"):
                continue
            module = importlib.import_module(module_info.name)
            for attr_name in dir(module):
                model = getattr(module, attr_name)
                if not (
                    isinstance(model, type)
                    and issubclass(model, BaseModel)
                    and model is not BaseModel
                ):
                    continue
                field = model.model_fields.get("cik")
                if field is None:
                    continue
                if not _field_uses_cik_coercer(field):
                    offenders.append(f"{module_info.name}.{model.__name__}")

        assert not offenders, f"cik fields not using the CIK type: {offenders}"
