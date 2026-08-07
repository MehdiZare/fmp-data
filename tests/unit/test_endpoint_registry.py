"""Tests for EndpointRegistry batch registration behaviour."""

from typing import Any

import pytest

from fmp_data.company.mapping import COMPANY_ENDPOINT_MAP, COMPANY_ENDPOINTS_SEMANTICS
from fmp_data.lc.models import EndpointSemantics, ParameterHint
from fmp_data.lc.registry import EndpointRegistry
from fmp_data.market.mapping import MARKET_ENDPOINT_MAP, MARKET_ENDPOINTS_SEMANTICS
from fmp_data.models import Endpoint

BatchEntry = tuple[Endpoint[Any], EndpointSemantics]


@pytest.fixture
def valid_entry() -> tuple[str, BatchEntry]:
    """A catalog pair that passes every validation step."""
    semantics = MARKET_ENDPOINTS_SEMANTICS["gainers"]
    return semantics.method_name, (
        MARKET_ENDPOINT_MAP[semantics.method_name],
        semantics,
    )


@pytest.fixture
def invalid_entry() -> tuple[str, BatchEntry]:
    """A pair that fails parameter validation via an unmatched hint."""
    semantics = COMPANY_ENDPOINTS_SEMANTICS["profile"]
    broken = semantics.model_copy(
        update={
            "parameter_hints": {
                **semantics.parameter_hints,
                "not_a_real_param": ParameterHint(
                    natural_names=["nonsense"],
                    extraction_patterns=[r"(\w+)"],
                    examples=["nonsense"],
                    context_clues=["nonsense"],
                ),
            }
        }
    )
    return broken.method_name, (COMPANY_ENDPOINT_MAP[broken.method_name], broken)


class TestRegisterBatch:
    """register_batch must not let one bad endpoint drop the rest."""

    def test_registers_valid_endpoints_after_an_invalid_one(
        self, invalid_entry: tuple[str, BatchEntry], valid_entry: tuple[str, BatchEntry]
    ) -> None:
        registry = EndpointRegistry()
        invalid_name, invalid_pair = invalid_entry
        valid_name, valid_pair = valid_entry

        registry.register_batch({invalid_name: invalid_pair, valid_name: valid_pair})

        assert registry.get_endpoint(valid_name) is not None
        assert registry.get_endpoint(invalid_name) is None

    def test_returns_failures_for_invalid_endpoints(
        self, invalid_entry: tuple[str, BatchEntry], valid_entry: tuple[str, BatchEntry]
    ) -> None:
        registry = EndpointRegistry()
        invalid_name, invalid_pair = invalid_entry
        valid_name, valid_pair = valid_entry

        failures = registry.register_batch(
            {invalid_name: invalid_pair, valid_name: valid_pair}
        )

        assert list(failures) == [invalid_name]
        assert "not_a_real_param" in failures[invalid_name]

    def test_returns_no_failures_when_every_endpoint_is_valid(
        self, valid_entry: tuple[str, BatchEntry]
    ) -> None:
        registry = EndpointRegistry()
        valid_name, valid_pair = valid_entry

        assert registry.register_batch({valid_name: valid_pair}) == {}

    def test_empty_batch_is_a_no_op(self) -> None:
        registry = EndpointRegistry()

        assert registry.register_batch({}) == {}
        assert registry.list_endpoints() == {}

    def test_a_structurally_malformed_pair_is_a_skip_not_a_crash(
        self, valid_entry: tuple[str, BatchEntry]
    ) -> None:
        """pydantic's ValidationError subclasses ValueError, so it is tolerated.

        Worth pinning explicitly: it means "never raises on validation" covers
        structurally malformed pairs too, not just drifted hints, and the rest
        of the batch still registers.
        """
        registry = EndpointRegistry()
        valid_name, valid_pair = valid_entry
        endpoint, _ = valid_pair

        failures = registry.register_batch(
            {
                "malformed": (endpoint, object()),  # type: ignore[dict-item]
                valid_name: valid_pair,
            }
        )

        assert list(failures) == ["malformed"]
        assert registry.get_endpoint(valid_name) is not None

    def test_non_value_errors_still_abort_the_batch(
        self, valid_entry: tuple[str, BatchEntry], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Only ValueError is tolerated; anything else stays loud.

        register_batch catches ValueError so drifted endpoints degrade to a
        skip. A non-validation failure -- in production, an ImportError while
        register() lazily builds the validation rules -- must propagate, or a
        whole client group could vanish while reporting no failures at all.
        """
        registry = EndpointRegistry()
        valid_name, valid_pair = valid_entry

        def boom(*args: object, **kwargs: object) -> tuple[bool, str]:
            raise RuntimeError("validation rules failed to load")

        monkeypatch.setattr(registry, "validate_endpoint", boom)

        with pytest.raises(RuntimeError, match="validation rules failed to load"):
            registry.register_batch({valid_name: valid_pair})
