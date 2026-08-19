# Leftover mandatory defaults and `structure` exposure

**Date:** 2026-08-17
**Base:** `dev` @ `10fa6af`
**Issue:** #349
**Status:** approved (approach 1)

## Problem

Requiredness is derived from list membership (#165). A param in
`mandatory_params` with a `default=` still raises `Missing mandatory
parameter` when omitted, so the default never applies.

#345 / #347 moved leftover **pagination** cases (`page` / `limit`) to
`optional_params`. A full catalogue walk on 2026-08-17 found exactly six
remaining mandatory-plus-default params, all on company endpoints:

| Endpoint | Param | Dead default |
|---|---|---|
| `PRODUCT_REVENUE_SEGMENTATION` | `structure` | `"flat"` |
| `PRODUCT_REVENUE_SEGMENTATION` | `period` | `"annual"` |
| `GEOGRAPHIC_REVENUE_SEGMENTATION` | `structure` | `"flat"` |
| `GEOGRAPHIC_REVENUE_SEGMENTATION` | `period` | `"annual"` |
| `FINANCIAL_REPORTS_JSON` | `period` | `"FY"` |
| `FINANCIAL_REPORTS_XLSX` | `period` | `"FY"` |

Python client methods already supply those values, so call sites are
unchanged today. Catalogue / `validate_params` / `client.request`
without those keys still fail.

`structure` is also a product gap: FMP documents it as optional
`flat` | `nested`, the deprecated arg model already has
`StructureTypeEnum`, and LangChain allowlists it as a dropped-mandatory
wire field because the methods hardcode `"flat"`.

## Goal

One PR that:

1. Moves the six params to `optional_params` so documented defaults
   inject through `validate_params`.
2. Exposes `structure` on the segmentation methods as
   `Structure = Literal["flat", "nested"]`, default `"flat"`.
3. Locks both the four endpoints' defaults and the catalogue-wide
   invariant that no mandatory param may carry a default.

## Non-goals

- Bounds factory or other leftover classes (#344, #346 are closed and
  unrelated).
- A second response model for `nested`. Live `/stable` returns the same
  list-of-objects for `flat`, `nested`, and omitted (AAPL / MSFT / TSLA,
  annual and quarter, probed 2026-08-17).
- Re-exporting `Structure` from `fmp_data.__all__`.
- New live VCR recordings for `nested`.
- Changing report method signatures (`period` already defaults to
  `"FY"` and is always passed).
- Pydantic / dataclass wrapper for the `structure` choice.
- Accepting undocumented tokens such as `"tree"` (live API ignores
  them; we reject them).

## Decisions

| Fork | Choice |
|---|---|
| Scope | Expand: move leftovers **and** expose `structure` |
| Nested | Advertise `flat` \| `nested`; same models; document no-op |
| Type | `Structure` Literal in `schema.py`; not in `__all__`; derive leftover enum |
| Locks | Local default test **and** catalogue-wide walk |
| Packaging | Single PR, same shape as #347 |

## Design

### Catalogue

On `PRODUCT_REVENUE_SEGMENTATION` and
`GEOGRAPHIC_REVENUE_SEGMENTATION`:

- `mandatory_params`: `symbol` only.
- `optional_params`: `structure` (default `"flat"`,
  `valid_values=list(STRUCTURE_VALUES)`) and `period` (default
  `"annual"`, `valid_values=list(PERIOD_ANNUAL_QUARTER_VALUES)`).

On `FINANCIAL_REPORTS_JSON` and `FINANCIAL_REPORTS_XLSX`:

- `mandatory_params`: `symbol`, `year` (no defaults).
- `optional_params`: `period` (default `"FY"`,
  `valid_values=list(PERIOD_FISCAL_VALUES)`).

`validate_params({"symbol": "AAPL"})` on a segmentation endpoint must
return `structure="flat"` and `period="annual"`.
`validate_params({"symbol": "AAPL", "year": 2024})` on a report
endpoint must return `period="FY"`. Missing `symbol` / `year` still
raises `ValidationError`.

### Types

In `fmp_data/schema.py`, next to the period aliases:

```python
Structure: TypeAlias = Literal["flat", "nested"]
STRUCTURE_VALUES: tuple[str, ...] = literal_values(Structure)
```

Leftover `StructureTypeEnum` unpacks from that tuple:

```python
class StructureTypeEnum(BaseEnum):
    """Data structure types.

    Member *values* come from ``Structure``. Retired with the
    deprecated arg models in 3.0 (#153, #307).
    """

    FLAT, NESTED = STRUCTURE_VALUES
```

`StructureTypeEnum` must be declared **after** `STRUCTURE_VALUES`.
Deprecated `RevenueSegmentationArgs.structure` keeps using the enum.

Do not add `Structure` to `fmp_data.__all__` or to
`test_closed_vocabularies_are_public_exports`.

### Client methods

Sync and async:

```python
def get_product_revenue_segmentation(
    self,
    symbol: str,
    period: PeriodAnnualQuarter = "annual",
    structure: Structure = "flat",
) -> list[ProductRevenueSegment]: ...
```

Same shape for `get_geographic_revenue_segmentation`. Pass `structure`
through to `client.request` / `request_async` instead of hardcoding
`"flat"`. Return type is unchanged for both values.

Docstring must state that stable currently returns the same
list-of-objects for `flat` and `nested` (probed 2026-08-17).

Report methods are unchanged.

Default call `get_product_revenue_segmentation("AAPL")` still sends
`period=annual&structure=flat`. Existing cassettes remain valid.

### LangChain / MCP

`KNOWN_DROPPED_MANDATORY_WIRE` becomes empty: delete both
`structure` allowlist rows. A new dropped-mandatory wire field is then
a PR failure (#188).

Once the methods accept `structure`, method dispatch advertises it as
optional (default `"flat"`). MCP binds the live Python method, so the
argument appears there without a `DEFAULT_TOOLS` edit.

`STRUCTURE_HINT` stays on both semantics maps.

Tests that assume `structure` is omitted under method dispatch must
use a fixture method that **includes** `structure=` and expect it in
optional. Employee-count `limit` remains the unmapped-omit example.
Bare (`method is None`) partition: `structure` is optional, not
mandatory.

`test_tool_binding.py::test_partition_demotes_params_the_method_defaults`
keeps a local fake method without `structure` so the omit-unmapped
rule still has a unit.

Stale LC copy that says “13 mandatory-with-default” is rewritten:
there are none after this change; list membership remains the rule.

### Errors

| Input | Result |
|---|---|
| Missing `symbol` or report `year` | `ValidationError` (`Missing mandatory parameter`) |
| `structure="tree"` or other non-member | `ValidationError` (`Must be one of`) |
| `period` outside that endpoint's Literal | `ValidationError` (`Must be one of`) |
| Valid `nested` | 200, same models as `flat` |

Live FMP accepts undocumented `structure` tokens and ignores them.
This client rejects them. That is intentional.

### Tests

1. **Local lock** (new company unit test, same shape as
   `test_rss_pagination_is_optional_like_latest`):
   membership + the `validate_params` injections above + reject
   `"tree"`.
2. **Catalogue lock** in `test_param_required_consistency.py`: every
   param in `mandatory_params` has `default is None`. Keep
   `_MIN_ENDPOINTS` / `_MIN_PARAMS` floors.
3. **Types:** `literal_values(Structure) == ("flat", "nested")`;
   `test_legacy_enums_*` pins `StructureTypeEnum` unpacked from
   `STRUCTURE_VALUES`. Segmentation methods join the closed-vocab
   signature walk.
4. **Client:** existing geographic period-forward test also asserts
   default `structure="flat"`; add one call that passes
   `structure="nested"` and checks the query string. List-unwrap
   tables stay `{symbol: "AAPL"}` only.

No new VCR cassettes.

### Changelog

Unreleased / Changed, same voice as the #345 RSS note. Closes #349.
`Closes #N` is inert on `dev`-base PRs — close #349 by hand after
merge.

## Out of scope if it shows up in review

- `PaginationArg` / page-limit bounds (explicit #345/#349 non-goal).
- Promoting `Structure` to the public package surface (separate
  decision, same as #308 / #311 for Period / TechnicalInterval).
- Modeling a nested tree if FMP later changes the wire. Re-probe
  before adding a second model.

## PR plan

One PR on `dev`. Conventional subject:

`fix(company): make leftover segmentation/report defaults optional (#349)`
