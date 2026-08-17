# Leftover mandatory defaults and `structure` exposure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the six leftover company mandatory-plus-default params to `optional_params`, expose `structure: Structure = "flat"` on the segmentation methods, and lock both the four endpoints and the catalogue-wide “no mandatory default” invariant (#349).

**Architecture:** Requiredness is list membership (`validate_params` only injects defaults from `optional_params`). Add `Structure = Literal["flat", "nested"]` in `fmp_data/schema.py`, derive leftover `StructureTypeEnum` from it, then move the six params and pass `structure` through the client methods. Live `/stable` returns the same list-of-objects for `flat` and `nested` (probed 2026-08-17); do not add a second model.

**Tech Stack:** Python 3.10+, Pydantic, pytest, ruff. Run tests with `uv run pytest`.

**Spec:** `docs/superpowers/specs/2026-08-17-mandatory-defaults-structure-design.md`

---

## File map

| File | Responsibility |
|---|---|
| `fmp_data/schema.py` | `Structure` Literal, `STRUCTURE_VALUES`, leftover `StructureTypeEnum` unpacked from the tuple |
| `fmp_data/company/endpoints.py` | Move `structure` / `period` to `optional_params`; `structure.valid_values = list(STRUCTURE_VALUES)` |
| `fmp_data/company/client.py` | Sync methods take `structure: Structure = "flat"` and pass it through |
| `fmp_data/company/async_client.py` | Same signatures and pass-through |
| `tests/unit/test_closed_vocabularies.py` | `Structure` Literal + leftover enum pins; `structure` client/endpoint walks. Do **not** add `Structure` to `__all__` |
| `tests/unit/test_param_required_consistency.py` | Catalogue-wide: no mandatory param may carry a `default` |
| `tests/unit/test_company.py` | Local membership + `validate_params` lock (RSS-test shape) |
| `tests/unit/test_company_coverage.py` | Default `structure="flat"` on the wire; explicit `structure="nested"` query |
| `tests/unit/lc/test_endpoint_method_coverage.py` | Empty `KNOWN_DROPPED_MANDATORY_WIRE` |
| `tests/unit/lc/test_method_dispatch.py` | Fixture method accepts `structure`; bare partition expects optional |
| `tests/unit/lc/test_tool_schema.py` | Rewrite stale “13 mandatory-with-default” comment |
| `CHANGELOG.md` | Unreleased / Changed note |

Do not edit: `fmp_data/mcp/tools_manifest.py`, VCR cassettes, `fmp_data/__init__.py`, `tests/e2e/harness.py` (`structure` is optional and not in `_ALWAYS_FILL`). Leave `test_tool_binding.py::test_partition_demotes_params_the_method_defaults` as the unmapped-omit unit (fake method without `structure`).

Work on a branch off `dev`: `fix/349-company-mandatory-defaults`.

---

### Task 1: `Structure` Literal and leftover enum

**Files:**
- Modify: `fmp_data/schema.py`
- Modify: `tests/unit/test_closed_vocabularies.py`

- [ ] **Step 1: Write the failing type tests**

In `tests/unit/test_closed_vocabularies.py`, add `STRUCTURE_VALUES` and `Structure` / `StructureTypeEnum` to the existing imports from `fmp_data.schema`.

Append after `test_period_aliases_are_distinct_contracts`:

```python
def test_structure_alias_is_flat_or_nested() -> None:
    assert literal_values(Structure) == ("flat", "nested")
    assert literal_values(Structure) == STRUCTURE_VALUES
```

Extend `test_legacy_enums_match_the_literal_sets`:

```python
    assert tuple(member.value for member in StructureTypeEnum) == STRUCTURE_VALUES
```

Extend `test_legacy_enums_are_unpacked_from_the_literal_tuples` so the source scan also requires `STRUCTURE_VALUES` in `StructureTypeEnum`, and pin members:

```python
    assert "STRUCTURE_VALUES" in inspect.getsource(schema.StructureTypeEnum)
    assert StructureTypeEnum.FLAT.value == "flat"
    assert StructureTypeEnum.NESTED.value == "nested"
```

Add a dedicated walk (do **not** fold `structure` into `_closed_sets`, which is period/interval/timeframe only):

```python
def test_structure_endpoint_valid_values_come_from_the_literal() -> None:
    found: list[str] = []
    wrong: list[str] = []
    for endpoint in _all_endpoints():
        params = list(endpoint.mandatory_params) + list(endpoint.optional_params or [])
        for param in params:
            if param.name != "structure":
                continue
            found.append(endpoint.name)
            values = tuple(str(v) for v in (param.valid_values or ()))
            if values != STRUCTURE_VALUES:
                wrong.append(f"{endpoint.name}.structure={values!r}")
    assert found, "expected revenue-segmentation structure params"
    assert not wrong, "structure valid_values drifted:\n  " + "\n  ".join(wrong)


def test_client_structure_annotations_are_the_typed_literal() -> None:
    untyped: list[str] = []
    seen = 0
    for root_cls in (FMPDataClient, AsyncFMPDataClient):
        for group, method, func in _iter_group_methods(root_cls):
            if "structure" not in bindable_params(func):
                continue
            seen += 1
            hints = get_type_hints(func)
            members = _annotation_members(hints.get("structure", inspect.Parameter.empty))
            default = inspect.signature(func).parameters["structure"].default
            if members != STRUCTURE_VALUES:
                untyped.append(
                    f"{root_cls.__name__}.{group}.{method} members={members!r}"
                )
            if default != "flat":
                untyped.append(
                    f"{root_cls.__name__}.{group}.{method} default={default!r}"
                )
    assert seen >= 4, f"expected sync+async product+geo methods, saw {seen}"
    assert not untyped, "structure annotations drifted:\n  " + "\n  ".join(untyped)
```

Do **not** add `Structure` to `test_closed_vocabularies_are_public_exports`.

- [ ] **Step 2: Run the new tests and confirm they fail**

```bash
uv run pytest tests/unit/test_closed_vocabularies.py::test_structure_alias_is_flat_or_nested tests/unit/test_closed_vocabularies.py::test_legacy_enums_match_the_literal_sets tests/unit/test_closed_vocabularies.py::test_legacy_enums_are_unpacked_from_the_literal_tuples tests/unit/test_closed_vocabularies.py::test_structure_endpoint_valid_values_come_from_the_literal tests/unit/test_closed_vocabularies.py::test_client_structure_annotations_are_the_typed_literal -v
```

Expected: `test_structure_alias_is_flat_or_nested` fails with `ImportError` / `NameError` (`Structure` / `STRUCTURE_VALUES` missing). The endpoint walk fails because `structure` has no `valid_values`. The client walk fails (`seen == 0`) because methods do not take `structure` yet — leave that failure until Task 4; **comment the client walk with `pytest.mark.skip(reason="Task 4: methods gain structure=")` only if you commit Task 1 alone**. Prefer committing Task 1 after the alias exists and running only the alias + leftover-enum tests now:

```bash
uv run pytest tests/unit/test_closed_vocabularies.py::test_structure_alias_is_flat_or_nested tests/unit/test_closed_vocabularies.py::test_legacy_enums_match_the_literal_sets tests/unit/test_closed_vocabularies.py::test_legacy_enums_are_unpacked_from_the_literal_tuples -v
```

Expected after adding the tests but before schema.py: FAIL (`Structure` not exported).

- [ ] **Step 3: Add `Structure` and derive the leftover enum**

In `fmp_data/schema.py`:

1. **Delete** the current `StructureTypeEnum` class (it sits *above* the period Literals today, around the `FLAT = "flat"` / `NESTED = "nested"` block).
2. After `TechnicalInterval: TypeAlias = Interval | IntervalAlias`, add:

```python
Structure: TypeAlias = Literal["flat", "nested"]
```

3. After `TECHNICAL_INTERVAL_VALUES: tuple[str, ...] = literal_values(TechnicalInterval)`, add:

```python
STRUCTURE_VALUES: tuple[str, ...] = literal_values(Structure)
```

4. After `STRUCTURE_VALUES` (and still before `ReportingPeriodEnum`), add:

```python
class StructureTypeEnum(BaseEnum):
    """Data structure types.

    Member *values* come from ``Structure``. Retired with the
    deprecated arg models in 3.0 (#153, #307).
    """

    FLAT, NESTED = STRUCTURE_VALUES
```

`fmp_data/company/schema.py` keeps `from fmp_data.schema import StructureTypeEnum`. Do not add `Structure` to `fmp_data/__init__.py`.

- [ ] **Step 4: Re-run the alias / leftover-enum tests**

```bash
uv run pytest tests/unit/test_closed_vocabularies.py::test_structure_alias_is_flat_or_nested tests/unit/test_closed_vocabularies.py::test_legacy_enums_match_the_literal_sets tests/unit/test_closed_vocabularies.py::test_legacy_enums_are_unpacked_from_the_literal_tuples tests/unit/test_closed_vocabularies.py::test_closed_vocabularies_are_public_exports -v
```

Expected: PASS. Public-export test still lists only Period / Interval / Timeframe / TechnicalInterval.

- [ ] **Step 5: Commit**

```bash
git add fmp_data/schema.py tests/unit/test_closed_vocabularies.py
git commit -m "feat(schema): add Structure Literal and derive leftover enum"
```

---

### Task 2: Failing locks (catalogue-wide + local)

**Files:**
- Modify: `tests/unit/test_param_required_consistency.py`
- Modify: `tests/unit/test_company.py`

- [ ] **Step 1: Write the catalogue-wide lock**

Add after `test_required_is_derived_from_list_membership` in `tests/unit/test_param_required_consistency.py`:

```python
def test_mandatory_params_do_not_carry_defaults() -> None:
    """A default on a mandatory param never applies (#165 / #349)."""
    leftovers: list[str] = []
    checked = 0
    for module_name, attr, endpoint in _endpoints():
        for param in endpoint.mandatory_params:
            checked += 1
            if param.default is not None:
                leftovers.append(
                    f"{module_name}.{attr}.{param.name}: default={param.default!r}"
                )
    assert not leftovers, (
        "mandatory params with a default never apply; move them to "
        "optional_params:\n  " + "\n  ".join(leftovers)
    )
    assert checked >= _MIN_PARAMS, (
        f"only {checked} mandatory params inspected; is the walk working? "
        f"skipped: {SKIPPED_MODULES}"
    )
```

- [ ] **Step 2: Run it and confirm it fails on the six leftovers**

```bash
uv run pytest tests/unit/test_param_required_consistency.py::test_mandatory_params_do_not_carry_defaults -v
```

Expected: FAIL, message names `PRODUCT_REVENUE_SEGMENTATION.structure`, `.period`, `GEOGRAPHIC_REVENUE_SEGMENTATION.structure`, `.period`, `FINANCIAL_REPORTS_JSON.period`, `FINANCIAL_REPORTS_XLSX.period`.

- [ ] **Step 3: Write the local company lock**

At the end of `tests/unit/test_company.py` add:

```python
class TestSegmentationAndReportDefaults:
    """Mandatory structure/period defaults never apply (#349)."""

    def test_segmentation_structure_and_period_are_optional(self) -> None:
        from fmp_data.company.endpoints import (
            GEOGRAPHIC_REVENUE_SEGMENTATION,
            PRODUCT_REVENUE_SEGMENTATION,
        )
        from fmp_data.exceptions import ValidationError as FMPValidationError
        from fmp_data.schema import STRUCTURE_VALUES

        for endpoint in (
            PRODUCT_REVENUE_SEGMENTATION,
            GEOGRAPHIC_REVENUE_SEGMENTATION,
        ):
            mandatory = {param.name for param in endpoint.mandatory_params}
            optional = {param.name for param in endpoint.optional_params or []}
            assert mandatory == {"symbol"}, endpoint.name
            assert "structure" in optional, endpoint.name
            assert "period" in optional, endpoint.name
            assert "structure" not in mandatory, endpoint.name
            assert "period" not in mandatory, endpoint.name
            injected = endpoint.validate_params({"symbol": "AAPL"})
            assert injected["symbol"] == "AAPL"
            assert injected["structure"] == "flat"
            assert injected["period"] == "annual"
            structure = next(
                param
                for param in (endpoint.optional_params or [])
                if param.name == "structure"
            )
            assert tuple(str(v) for v in (structure.valid_values or ())) == (
                STRUCTURE_VALUES
            )
            with pytest.raises(FMPValidationError, match="Must be one of"):
                endpoint.validate_params({"symbol": "AAPL", "structure": "tree"})

    def test_report_period_is_optional(self) -> None:
        from fmp_data.company.endpoints import (
            FINANCIAL_REPORTS_JSON,
            FINANCIAL_REPORTS_XLSX,
        )
        from fmp_data.exceptions import ValidationError as FMPValidationError

        for endpoint in (FINANCIAL_REPORTS_JSON, FINANCIAL_REPORTS_XLSX):
            mandatory = {param.name for param in endpoint.mandatory_params}
            optional = {param.name for param in endpoint.optional_params or []}
            assert mandatory == {"symbol", "year"}, endpoint.name
            assert "period" in optional, endpoint.name
            assert "period" not in mandatory, endpoint.name
            injected = endpoint.validate_params({"symbol": "AAPL", "year": 2024})
            assert injected["period"] == "FY"
            with pytest.raises(FMPValidationError, match="Missing mandatory parameter"):
                endpoint.validate_params({"symbol": "AAPL"})
```

- [ ] **Step 4: Run the local lock and confirm it fails**

```bash
uv run pytest tests/unit/test_company.py::TestSegmentationAndReportDefaults -v
```

Expected: FAIL (`structure` / `period` still in `mandatory_params`; `validate_params({"symbol": "AAPL"})` raises `Missing mandatory parameter: structure`).

- [ ] **Step 5: Commit the failing tests**

```bash
git add tests/unit/test_param_required_consistency.py tests/unit/test_company.py
git commit -m "test: lock leftover mandatory defaults on company endpoints"
```

(If pre-commit runs the whole suite and refuses a red commit, keep the tests uncommitted and land them with Task 3.)

---

### Task 3: Move the six params and clear the LC allowlist

**Files:**
- Modify: `fmp_data/company/endpoints.py`
- Modify: `tests/unit/lc/test_endpoint_method_coverage.py`
- Modify: `tests/unit/lc/test_method_dispatch.py`
- Modify: `tests/unit/lc/test_tool_schema.py`

Moving `structure` out of `mandatory_params` makes `KNOWN_DROPPED_MANDATORY_WIRE` **stale** immediately (that guard only walks mandatory params). Empty the allowlist in this task, before the methods grow `structure=`.

- [ ] **Step 1: Import `STRUCTURE_VALUES` and move the params**

In `fmp_data/company/endpoints.py` add `STRUCTURE_VALUES` to the `fmp_data.schema` import.

Replace `PRODUCT_REVENUE_SEGMENTATION` so `mandatory_params` is only `symbol` and `optional_params` is:

```python
    optional_params=[
        EndpointParam(
            name="structure",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Data structure format",
            default="flat",
            valid_values=list(STRUCTURE_VALUES),
        ),
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Annual or quarterly data",
            default="annual",
            valid_values=list(PERIOD_ANNUAL_QUARTER_VALUES),
        ),
    ],
```

Same split for `GEOGRAPHIC_REVENUE_SEGMENTATION` (keep its description / `response_model` / `example_queries`).

For `FINANCIAL_REPORTS_JSON` and `FINANCIAL_REPORTS_XLSX`, keep `symbol` and `year` in `mandatory_params` (no defaults). Move `period` to:

```python
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Report period (FY or Q1-Q4)",
            default="FY",
            valid_values=list(PERIOD_FISCAL_VALUES),
        ),
    ],
```

- [ ] **Step 2: Empty `KNOWN_DROPPED_MANDATORY_WIRE`**

In `tests/unit/lc/test_endpoint_method_coverage.py`:

- Change the header comment `2 dropped-mandatory` to `0 dropped-mandatory`.
- Replace the allowlist with:

```python
# ``(client_name, method_name, wire_param)``: mandatory endpoint fields that
# method dispatch intentionally omits from the tool schema because the
# client method does not accept them.
#
# Empty since #349: revenue ``structure`` is optional and (after Task 4)
# accepted by the methods. A new dropped-mandatory is a PR failure.
KNOWN_DROPPED_MANDATORY_WIRE: frozenset[tuple[str, str, str]] = frozenset()
```

Leave `test_classifier_flags_dropped_mandatory_wire_field` (synthetic endpoint) unchanged.

- [ ] **Step 3: Update the bare partition assertion**

In `tests/unit/lc/test_method_dispatch.py`, `test_partition_omits_unmapped_when_method_active`:

Keep the fixture method **without** `structure` for this task (methods still hardcode it). Change only the bare (`method is None`) assertion from mandatory to optional:

```python
    bare_mand, bare_opt = partition_params_for_method(
        PRODUCT_REVENUE_SEGMENTATION.mandatory_params,
        PRODUCT_REVENUE_SEGMENTATION.optional_params or [],
        None,
    )
    assert "structure" not in {p.name for p in bare_mand}
    assert "structure" in {p.name for p in bare_opt}
```

The live-method half of that test still expects `structure` omitted from the fixture method — that stays correct until Task 4.

- [ ] **Step 4: Rewrite the stale tool-schema comment**

In `tests/unit/lc/test_tool_schema.py`, replace the docstring lines about “13 endpoints declare a `default` on a mandatory param and 13 more carry `required=True`…” with:

```python
    """A tool's required arguments must be the endpoint's mandatory params.

    Not ``param.required`` and not "has no default": after #349 no
    mandatory param carries a default, and ``required`` is derived from
    list membership (#165). Membership of ``mandatory_params`` is the
    only self-consistent answer, so it is the one the schema follows.
    """
```

- [ ] **Step 5: Run the locks and LC guards**

```bash
uv run pytest \
  tests/unit/test_param_required_consistency.py::test_mandatory_params_do_not_carry_defaults \
  tests/unit/test_company.py::TestSegmentationAndReportDefaults \
  tests/unit/test_closed_vocabularies.py::test_structure_endpoint_valid_values_come_from_the_literal \
  tests/unit/lc/test_endpoint_method_coverage.py \
  tests/unit/lc/test_method_dispatch.py::test_partition_omits_unmapped_when_method_active \
  tests/unit/lc/test_tool_schema.py::test_tool_schema_requires_exactly_the_mandatory_params \
  -v
```

Expected: PASS. `test_client_structure_annotations_are_the_typed_literal` still fails if you already added it unskipped — do not run it yet.

- [ ] **Step 6: Commit**

```bash
git add fmp_data/company/endpoints.py tests/unit/lc/test_endpoint_method_coverage.py tests/unit/lc/test_method_dispatch.py tests/unit/lc/test_tool_schema.py tests/unit/test_param_required_consistency.py tests/unit/test_company.py
git commit -m "fix(company): move leftover structure/period defaults to optional"
```

---

### Task 4: Expose `structure` on sync and async methods

**Files:**
- Modify: `fmp_data/company/client.py`
- Modify: `fmp_data/company/async_client.py`
- Modify: `tests/unit/test_company_coverage.py`
- Modify: `tests/unit/lc/test_method_dispatch.py`
- Modify: `tests/unit/test_closed_vocabularies.py` (unskip the client walk if skipped)

- [ ] **Step 1: Write the failing client tests**

In `tests/unit/test_company_coverage.py`, update `test_get_geographic_revenue_segmentation_period` so the forwarded params also include default structure:

```python
        assert params["symbol"] == "AAPL"
        assert params["period"] == "annual"
        assert params["structure"] == "flat"
```

Add immediately after that method:

```python
    @patch("httpx.Client.request")
    def test_get_geographic_revenue_segmentation_nested_structure(
        self, mock_request, fmp_client, mock_response, geographic_revenue_data
    ):
        """structure=nested is forwarded; response model is unchanged."""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[geographic_revenue_data]
        )

        result = fmp_client.company.get_geographic_revenue_segmentation(
            "AAPL", structure="nested"
        )

        assert len(result) == 1
        assert isinstance(result[0], GeographicRevenueSegment)
        params = mock_request.call_args.kwargs["params"]
        assert params["structure"] == "nested"
        assert params["period"] == "annual"
```

Leave `_COMPANY_LIST_UNWRAP_CASES` / async tables as `{"symbol": "AAPL"}` only.

- [ ] **Step 2: Run the new coverage test and confirm it fails**

```bash
uv run pytest tests/unit/test_company_coverage.py::TestCompanyClientCoverage::test_get_geographic_revenue_segmentation_nested_structure -v
```

Expected: FAIL (`TypeError: ... unexpected keyword argument 'structure'`).

- [ ] **Step 3: Update the methods**

In both `fmp_data/company/client.py` and `fmp_data/company/async_client.py`:

Change the schema import to:

```python
from fmp_data.schema import (
    Interval,
    Period,
    PeriodAnnualQuarter,
    PeriodFiscal,
    Structure,
)
```

Replace both segmentation methods. Sync product method:

```python
    def get_product_revenue_segmentation(
        self,
        symbol: str,
        period: PeriodAnnualQuarter = "annual",
        structure: Structure = "flat",
    ) -> list[ProductRevenueSegment]:
        """Get revenue segmentation by product.

        Args:
            symbol: Company symbol
            period: Data period ('annual' or 'quarter')
            structure: Response layout ('flat' or 'nested'). Stable
                currently returns the same list-of-objects for both
                (probed 2026-08-17).

        Returns:
            List of product revenue segments by fiscal year
        """
        return self._unwrap_list(
            self.client.request(
                PRODUCT_REVENUE_SEGMENTATION,
                symbol=symbol,
                structure=structure,
                period=period,
            ),
            ProductRevenueSegment,
        )
```

Sync geographic: same signature and docstring sentence, `GEOGRAPHIC_REVENUE_SEGMENTATION` / `GeographicRevenueSegment`.

Async: same signatures; `await self.client.request_async(...)` with `structure=structure`.

Do not change report methods.

- [ ] **Step 4: Point the LC fixture method at the new signature**

In `tests/unit/lc/test_method_dispatch.py`, `test_partition_omits_unmapped_when_method_active`, change the revenue fixture and expectations:

```python
    def get_product_revenue_segmentation(
        symbol: str, period: str = "annual", structure: str = "flat"
    ) -> list[Any]:
        return []
```

```python
    assert {p.name for p in rev_mandatory} == {"symbol"}
    assert {p.name for p in rev_optional} == {"period", "structure"}
```

Keep employee `limit` as the unmapped-omit example. Do not change `test_tool_binding.py`.

- [ ] **Step 5: Run client, LC, and the structure signature walk**

```bash
uv run pytest \
  tests/unit/test_company_coverage.py::TestCompanyClientCoverage::test_get_geographic_revenue_segmentation_period \
  tests/unit/test_company_coverage.py::TestCompanyClientCoverage::test_get_geographic_revenue_segmentation_nested_structure \
  tests/unit/test_closed_vocabularies.py::test_client_structure_annotations_are_the_typed_literal \
  tests/unit/lc/test_method_dispatch.py::test_partition_omits_unmapped_when_method_active \
  tests/unit/lc/test_endpoint_method_coverage.py \
  tests/unit/test_company.py::TestSegmentationAndReportDefaults \
  tests/unit/test_async_clients.py -k "revenue_segmentation" \
  tests/unit/test_company.py -k "product_revenue or geographic_revenue" \
  -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add fmp_data/company/client.py fmp_data/company/async_client.py tests/unit/test_company_coverage.py tests/unit/lc/test_method_dispatch.py tests/unit/test_closed_vocabularies.py
git commit -m "feat(company): expose structure= on revenue segmentation methods"
```

---

### Task 5: Changelog and full verification

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add the Unreleased / Changed note**

Insert after the existing RSS leftover bullet (`#345`), same voice:

```markdown
- **Company segmentation/report leftover defaults are optional (#349).**
  `structure` / `period` on product and geographic revenue
  segmentation, and `period` on financial-reports JSON/XLSX, move to
  `optional_params` so `validate_params` applies the documented
  defaults (`flat` / `annual` / `FY`). Segmentation methods now take
  `structure: Structure = "flat"` (`Literal["flat", "nested"]`).
  Stable currently returns the same list-of-objects for both
  (probed 2026-08-17). `Structure` is not re-exported from
  `fmp_data`. No remaining mandatory-plus-default params in the
  catalogue.
```

- [ ] **Step 2: Run the focused suite plus the requiredness / catalogue guards**

```bash
uv run pytest \
  tests/unit/test_param_required_consistency.py \
  tests/unit/test_closed_vocabularies.py \
  tests/unit/test_company.py::TestSegmentationAndReportDefaults \
  tests/unit/test_company_coverage.py::TestCompanyClientCoverage \
  tests/unit/lc/test_endpoint_method_coverage.py \
  tests/unit/lc/test_method_dispatch.py \
  tests/unit/lc/test_tool_schema.py \
  tests/unit/test_tool_binding.py \
  tests/unit/test_catalog_registration.py \
  -v
```

Expected: PASS.

- [ ] **Step 3: Format / lint the touched Python**

```bash
uv run ruff format fmp_data/schema.py fmp_data/company/endpoints.py fmp_data/company/client.py fmp_data/company/async_client.py tests/unit/test_closed_vocabularies.py tests/unit/test_param_required_consistency.py tests/unit/test_company.py tests/unit/test_company_coverage.py tests/unit/lc/test_endpoint_method_coverage.py tests/unit/lc/test_method_dispatch.py tests/unit/lc/test_tool_schema.py
uv run ruff check fmp_data/schema.py fmp_data/company/endpoints.py fmp_data/company/client.py fmp_data/company/async_client.py tests/unit/test_closed_vocabularies.py tests/unit/test_param_required_consistency.py tests/unit/test_company.py tests/unit/test_company_coverage.py tests/unit/lc/test_endpoint_method_coverage.py tests/unit/lc/test_method_dispatch.py tests/unit/lc/test_tool_schema.py
```

Expected: clean.

- [ ] **Step 4: Commit changelog**

```bash
git add CHANGELOG.md
git commit -m "docs: note leftover company defaults and structure= (#349)"
```

- [ ] **Step 5: Open the PR against `dev`**

Subject (from the spec):

`fix(company): make leftover segmentation/report defaults optional (#349)`

Body must say: `Closes #349` is inert on a `dev`-base PR — close #349 by hand after merge. Mention the live probe (AAPL/MSFT/TSLA, `flat` == `nested`, 2026-08-17). Do not add `release:major`.

---

## Spec coverage

| Spec item | Task |
|---|---|
| Move six params to `optional_params` | 3 |
| `validate_params` injects `flat` / `annual` / `FY` | 2–3 |
| Reject `structure="tree"` | 2–3 |
| `symbol` / `year` stay mandatory | 2–3 |
| `Structure` Literal + `STRUCTURE_VALUES` | 1 |
| Leftover `StructureTypeEnum` from the tuple | 1 |
| Not in `fmp_data.__all__` | 1 |
| Methods take `structure: Structure = "flat"` | 4 |
| Same response models; docstring probe date | 4 |
| Report methods unchanged | 4 (explicit non-edit) |
| Empty `KNOWN_DROPPED_MANDATORY_WIRE` | 3 |
| LC fixture includes `structure`; employee `limit` still omitted | 4 |
| Bare partition: `structure` optional | 3 |
| `test_tool_binding` omit-unmapped unit left alone | file map |
| Stale “13 mandatory-with-default” comment | 3 |
| Catalogue-wide no-mandatory-default lock | 2–3 |
| Closed-vocab walks for `structure` | 1, 4 |
| Coverage test default + nested query | 4 |
| No new VCR / no harness `_ALWAYS_FILL` | file map |
| Changelog | 5 |
| Close #349 by hand after merge | 5 |

## Self-review

- No TBD / “add tests later” / “similar to Task N”.
- `Structure` / `STRUCTURE_VALUES` / method signature `structure: Structure = "flat"` are the same names in every task.
- Client walk in Task 1 will fail until Task 4; the plan says to run only alias/enum tests in Task 1, or skip the client walk until Task 4.
- Emptying the LC allowlist is in Task 3 because moving `structure` to optional makes those triples stale even before the methods change.
