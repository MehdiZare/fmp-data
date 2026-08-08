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
        """Every CIK-valued field must route through the CIK coercer.

        A bare ``str`` annotation rejects an integer CIK before
        validation_mode is ever consulted, so one drifted model
        reintroduces the whole bug class. Covers ``cik`` and every
        sibling ``*_cik`` field (reporting_cik, company_cik, ...),
        which carry the same identifier and the same defect.

        Every module is walked, not just ``*.models``: request-argument
        models live in ``*.schema`` (``Form13FArgs``, ``PortfolioDateArgs``)
        and carry cik fields too, so a ``*.models``-only walk left the
        drift hole open in exactly the place it had already happened.
        """
        import importlib
        import pkgutil

        import fmp_data

        # fmp_data.investment.schema cannot be imported under pydantic 2.13:
        # ETFHoldingsArgs declares `date: date`, clashing with the datetime
        # import. Pre-existing on dev, tracked in #139. Listed explicitly
        # rather than swallowed, so a *newly* un-importable module fails this
        # guard instead of quietly dropping out of its coverage.
        known_unimportable = {"fmp_data.investment.schema"}
        unexpected: list[str] = []

        offenders: list[str] = []
        # A model imported into several modules shows up in each one's dir();
        # key on its defining module so the count means what it says.
        seen: set[tuple[str, str, str]] = set()
        for module_info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
            try:
                module = importlib.import_module(module_info.name)
            except Exception as exc:
                # Broad on purpose: a module can fail to import for reasons
                # other than ImportError (#139 raises PydanticUserError).
                # Nothing is swallowed -- it is asserted on below.
                if module_info.name not in known_unimportable:
                    unexpected.append(f"{module_info.name}: {exc!r}")
                continue
            for attr_name in dir(module):
                model = getattr(module, attr_name)
                if not (
                    isinstance(model, type)
                    and issubclass(model, BaseModel)
                    and model is not BaseModel
                ):
                    continue
                for field_name, field in model.model_fields.items():
                    if field_name != "cik" and not field_name.endswith("_cik"):
                        continue
                    key = (model.__module__, model.__qualname__, field_name)
                    if key in seen:
                        continue
                    seen.add(key)
                    if not _field_uses_cik_coercer(field):
                        offenders.append("{}.{}.{}".format(*key))

        assert not offenders, f"cik fields not using the CIK type: {offenders}"
        assert not unexpected, f"modules this guard could not inspect: {unexpected}"

        # walk_packages(onerror=None) swallows ImportError, so an extras-gated
        # subtree can vanish silently and leave this guard passing vacuously.
        assert len(seen) >= 50, (
            f"guard inspected only {len(seen)} fields — "
            "is it still walking the package?"
        )


class TestCIKRequestParam:
    """ParamType.CIK zero-pads a CIK on the way out to the API."""

    @staticmethod
    def _param(required: bool = True) -> EndpointParam:
        return EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.CIK,
            required=required,
            description="CIK number",
        )

    def test_int_is_zero_padded(self) -> None:
        """A plain STRING param would send '320193' and match nothing."""
        assert self._param().validate_value(320193) == "0000320193"

    def test_unpadded_string_is_padded(self) -> None:
        """Unlike the response side, a request value is ours to normalise.

        The response coercer leaves strings alone because rewriting them
        would misreport what the API sent. Outbound there is no such
        constraint: FMP matches on the padded form, so pad it.
        """
        assert self._param().validate_value("320193") == "0000320193"

    def test_canonical_string_is_unchanged(self) -> None:
        assert self._param().validate_value("0000320193") == "0000320193"

    def test_non_numeric_string_passes_through(self) -> None:
        """Better a clear API error than a value we mangled into one."""
        assert self._param().validate_value("AAPL") == "AAPL"

    def test_over_long_digits_are_not_truncated(self) -> None:
        assert self._param().validate_value("12345678901") == "12345678901"

    def test_bool_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            self._param().validate_value(True)

    def test_optional_none_stays_none(self) -> None:
        assert self._param(required=False).validate_value(None) is None

    def test_every_cik_endpoint_param_uses_the_cik_type(self) -> None:
        """No cik param may stay ParamType.STRING.

        A STRING cik silently stringifies an int without padding, so the
        request succeeds and returns nothing — the failure mode this type
        exists to remove.
        """
        import importlib
        import pkgutil

        import fmp_data
        from fmp_data.models import Endpoint as EndpointModel

        offenders: list[str] = []
        checked = 0
        for module_info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
            if not module_info.name.endswith(".endpoints"):
                continue
            module = importlib.import_module(module_info.name)
            for attr_name in dir(module):
                endpoint = getattr(module, attr_name)
                if not isinstance(endpoint, EndpointModel):
                    continue
                params = list(endpoint.mandatory_params) + list(
                    endpoint.optional_params or []
                )
                for param in params:
                    if param.name != "cik" and not param.name.endswith("_cik"):
                        continue
                    checked += 1
                    if param.param_type is not ParamType.CIK:
                        offenders.append(
                            f"{module_info.name}.{attr_name}.{param.name}"
                            f" is {param.param_type}"
                        )

        assert not offenders, f"cik params not using ParamType.CIK: {offenders}"
        # walk_packages(onerror=None) swallows ImportError, so a subtree can
        # vanish silently and leave this guard passing vacuously.
        assert checked >= 15, (
            f"guard inspected only {checked} params — is it still walking the package?"
        )
