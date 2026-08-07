# PR1: Contained Correctness Fixes (#134, #131) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the uncompilable enum regex in `EndpointBasedRule._get_type_pattern` (#134) and make every `cik` model field accept an integer CIK by coercing it to the canonical 10-digit zero-padded string (#131).

**Architecture:** Two independent fixes sharing one PR because both are contained, low-blast-radius corrections with no public API change. #134 is a two-character fix to one f-string plus an enum-value unwrap, guarded by a test that compiles every pattern the registry can emit. #131 introduces one shared `Annotated` type in `fmp_data/models.py` and swaps 45 `cik: str` annotations to use it, rather than adding 45 separate field validators.

**Tech Stack:** Python 3.10+, pydantic v2 (`BeforeValidator`, `Annotated`), pytest, mypy, ruff.

**Source spec:** `docs/superpowers/specs/2026-08-07-open-issues-remediation-design.md` §4 PR1.

## Global Constraints

- Base branch is `dev`, not `main`. Branch from `dev` and target `dev`.
- Line length limit is 88 characters (ruff).
- Type hints are required and enforced by mypy, including in `tests/` (the `tests.*` override relaxes `disallow_untyped_defs` but still type-checks what you write).
- All Pydantic models use `extra="allow"` with `alias_generator=to_camel` via `default_model_config`. Do not add per-model `model_config`.
- CHANGELOG entries go under `## Unreleased` (which becomes 2.6.0). The `## [2.5.0]` section is cut and closed — do not add to it.
- Run `make lint` and `make format` before committing; pre-commit hooks run ruff and mypy automatically.
- `fmp_data/lc/registry.py` also contains `_find_matching_rule` / `get_expected_category`, landed separately in `d9a37cc`. This plan only touches `_get_type_pattern`; leave those two alone.

---

### Task 1: Guard every emitted regex pattern, and fix the unbalanced paren

`EndpointBasedRule._get_type_pattern` (`fmp_data/lc/registry.py:271-273`) builds `^(annual|quarter))$` — one closing paren too many. The pattern reaches an uncaught `re.match` in `fmp_data/lc/validation.py:140`, so it is a live landmine on a public method.

**Files:**
- Modify: `fmp_data/lc/registry.py:271-273`
- Test: `tests/unit/lc/test_validation_registry.py`

**Interfaces:**
- Consumes: `EndpointBasedRule(endpoints: dict[str, Endpoint], category: SemanticCategory)`; `rule.get_parameter_requirements(method_name: str) -> dict[str, list[str]] | None`; `get_endpoint_groups() -> dict[str, GroupConfig]` where `GroupConfig` is a `TypedDict` with keys `endpoint_map`, `semantics_map`, `category`.
- Produces: nothing new — this task only changes the body of an existing static method.

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/lc/test_validation_registry.py`. Add `import re` and `from fmp_data.lc.registry import get_endpoint_groups` to the existing imports if not already present.

```python
def test_every_emitted_pattern_compiles() -> None:
    """Every regex the registry can emit must compile.

    Patterns from this family are consumed by an uncaught ``re.match`` in
    ``fmp_data/lc/validation.py``, so an uncompilable pattern is a crash
    waiting for the first caller that reaches it.
    """
    uncompilable: list[tuple[str, str, str]] = []
    for group_name, config in get_endpoint_groups().items():
        rule = EndpointBasedRule(config["endpoint_map"], config["category"])
        for method_name in config["endpoint_map"]:
            requirements = rule.get_parameter_requirements(method_name) or {}
            for param_name, patterns in requirements.items():
                for pattern in patterns:
                    try:
                        re.compile(pattern)
                    except re.error as exc:
                        uncompilable.append(
                            (f"{group_name}.{method_name}", param_name, str(exc))
                        )
    assert not uncompilable, f"uncompilable patterns: {uncompilable}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/unit/lc/test_validation_registry.py::test_every_emitted_pattern_compiles -v`

Expected: FAIL. The assertion message lists 22 entries across 15 endpoints — every `period`, `interval`, `timeframe` and `name` param — each with `unbalanced parenthesis`.

- [ ] **Step 3: Fix the paren**

In `fmp_data/lc/registry.py`, the `case "string":` branch of `_get_type_pattern`:

```python
            case "string":
                if valid_values:
                    return [f"^({'|'.join(map(str, valid_values))})$"]
                return [r"^.+$"]
```

Only the trailing `))$` becomes `)$`. Leave `map(str, ...)` alone — Task 2 handles it.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/unit/lc/test_validation_registry.py::test_every_emitted_pattern_compiles -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fmp_data/lc/registry.py tests/unit/lc/test_validation_registry.py
git commit -m "fix(lc): drop extra paren in enum string type pattern (#134)

_get_type_pattern emitted '^(annual|quarter))$', which raises re.error
on the uncaught re.match in validation.py. Adds a guard that compiles
every pattern the registry can emit across all 168 registered endpoints."
```

---

### Task 2: Unwrap enum members to their values

`economics.get_economic_indicators` declares `valid_values` as `EconomicIndicatorType` members, so `map(str, ...)` yields `EconomicIndicatorType.GDP` rather than `GDP`. After Task 1 the pattern compiles — and now silently rejects every valid value, which is worse than crashing. It is the only endpoint in this state, but the fix belongs in the shared helper.

**Files:**
- Modify: `fmp_data/lc/registry.py:271-273`
- Test: `tests/unit/lc/test_validation_registry.py`

**Interfaces:**
- Consumes: `EndpointBasedRule.get_parameter_requirements` as in Task 1; `fmp_data.economics.endpoints.ECONOMIC_INDICATORS`; `fmp_data.economics.schema.EconomicIndicatorType` (a `str` Enum whose `.value` is the wire form, e.g. `EconomicIndicatorType.REAL_GDP.value == "realGDP"`).
- Produces: nothing new.

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/lc/test_validation_registry.py`:

```python
def test_enum_valid_values_use_wire_value_not_repr() -> None:
    """Enum members must contribute their .value, not their repr.

    ``economics.get_economic_indicators`` declares valid_values as
    EconomicIndicatorType members. ``str(member)`` yields
    'EconomicIndicatorType.GDP', so the pattern would compile and then
    reject the very values it is supposed to accept.
    """
    from fmp_data.economics.endpoints import ECONOMIC_INDICATORS
    from fmp_data.economics.schema import EconomicIndicatorType

    rule = EndpointBasedRule(
        {"get_economic_indicators": ECONOMIC_INDICATORS},
        SemanticCategory.ECONOMIC,
    )
    requirements = rule.get_parameter_requirements("get_economic_indicators")
    assert requirements is not None
    patterns = requirements["name"]

    assert "EconomicIndicatorType." not in patterns[0]
    for member in EconomicIndicatorType:
        assert any(
            re.match(pattern, member.value) for pattern in patterns
        ), f"{member.value!r} rejected by {patterns}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/unit/lc/test_validation_registry.py::test_enum_valid_values_use_wire_value_not_repr -v`

Expected: FAIL on `assert "EconomicIndicatorType." not in patterns[0]`.

- [ ] **Step 3: Unwrap enum values**

Replace the `case "string":` branch body in `fmp_data/lc/registry.py`:

```python
            case "string":
                if valid_values:
                    alternatives = "|".join(
                        re.escape(
                            value.value if isinstance(value, Enum) else str(value)
                        )
                        for value in valid_values
                    )
                    return [f"^({alternatives})$"]
                return [r"^.+$"]
```

Add `from enum import Enum` to the imports at the top of `fmp_data/lc/registry.py`. `re` is already imported (line 11).

`re.escape` is included because `valid_values` is arbitrary endpoint-declared data — a value containing `.`, `+` or `(` would otherwise be interpreted as regex syntax rather than matched literally.

- [ ] **Step 4: Run both regex tests to verify they pass**

Run: `python3 -m pytest tests/unit/lc/test_validation_registry.py -v`

Expected: PASS, all tests including `test_every_emitted_pattern_compiles` from Task 1.

- [ ] **Step 5: Verify the fix on a real endpoint**

Run:

```bash
python3 -c "
import re
from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.registry import EndpointBasedRule
from fmp_data.fundamental.endpoints import INCOME_STATEMENT
r = EndpointBasedRule({'get_income_statement': INCOME_STATEMENT}, SemanticCategory.FUNDAMENTAL_ANALYSIS)
pats = r.get_parameter_requirements('get_income_statement')['period']
print(pats)
print('annual ->', bool(re.match(pats[0], 'annual')))
print('bogus  ->', bool(re.match(pats[0], 'bogus')))
"
```

Expected output:

```
['^(annual|quarter|FY|Q1|Q2|Q3|Q4)$']
annual -> True
bogus  -> False
```

- [ ] **Step 6: Commit**

```bash
git add fmp_data/lc/registry.py tests/unit/lc/test_validation_registry.py
git commit -m "fix(lc): use enum .value in string type patterns (#134)

economics.get_economic_indicators declares valid_values as enum members,
so map(str, ...) produced 'EconomicIndicatorType.GDP' and the pattern
rejected every real value. Also escapes alternatives, since valid_values
is endpoint-declared data rather than trusted regex source."
```

---

### Task 3: Add the shared CIK coercing type

Live probes on 2026-08-07 found `cik` returned as a 10-digit zero-padded string from every endpoint that returns it (`institutional-ownership/latest`, `sec-filings-search/cik`). A bare `str(320193)` would yield `"320193"`, which does not compare equal to `"0000320193"` — so the coercer pads. Ints only; strings pass through untouched, because re-padding a string would rewrite whatever the endpoint actually sent.

**Files:**
- Modify: `fmp_data/models.py` (add after the `default_model_config` definition, currently ending line 34)
- Test: `tests/unit/test_models.py`

**Interfaces:**
- Consumes: `pydantic.BeforeValidator`, `typing.Annotated`.
- Produces: `fmp_data.models.CIK` — a type alias usable as `cik: CIK` (required) or `cik: CIK | None = Field(default=None)` (optional). Tasks 4 and 5 import it. Also `fmp_data.models._coerce_cik(value: Any) -> Any`, not part of the public surface.

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_models.py`:

```python
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
            Model()

    def test_bool_is_not_treated_as_int(self) -> None:
        """bool is a subclass of int; padding True to '0000000001' is nonsense."""
        from fmp_data.models import CIK, default_model_config

        class Model(BaseModel):
            model_config = default_model_config
            cik: CIK | None = Field(default=None)

        with pytest.raises(PydanticValidationError):
            Model(cik=True)
```

Ensure `tests/unit/test_models.py` has these imports at the top:

```python
from typing import Annotated, Any, get_args, get_origin

import pytest
from pydantic import BaseModel, Field
from pydantic import ValidationError as PydanticValidationError
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/unit/test_models.py::TestCIKCoercion -v`

Expected: FAIL with `ImportError: cannot import name 'CIK' from 'fmp_data.models'`.

- [ ] **Step 3: Add the type**

In `fmp_data/models.py`, add `Annotated` to the `typing` import on line 6 and `BeforeValidator` to the `pydantic` import on line 9, then insert immediately after the `default_model_config` block:

```python
def _coerce_cik(value: Any) -> Any:
    """Coerce an integer CIK to its canonical zero-padded string form.

    A CIK is a fixed-width 10-digit zero-padded identifier. Every FMP
    endpoint observed returning one returns a string (probed 2026-08-07),
    but JSON producers drop leading zeros routinely, so an int is coerced
    rather than rejected.

    Strings pass through untouched: re-padding would rewrite whatever the
    API actually sent, which is a larger claim than the evidence supports.
    ``bool`` is excluded because it subclasses ``int``.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return f"{value:010d}"
    return value


CIK = Annotated[str, BeforeValidator(_coerce_cik)]
"""SEC Central Index Key, coerced from int to a 10-digit zero-padded string."""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/unit/test_models.py::TestCIKCoercion -v`

Expected: PASS, 5 tests.

- [ ] **Step 5: Commit**

```bash
git add fmp_data/models.py tests/unit/test_models.py
git commit -m "feat(models): add shared CIK type coercing int to zero-padded str (#131)

Every probed endpoint returns cik as a 10-digit zero-padded string, but
JSON producers drop leading zeros. CIK coerces int -> '%010d' so callers
joining on cik across endpoints get one spelling. Strings pass through."
```

---

### Task 4: Apply the CIK type to all 45 `cik` fields

45 `cik` fields across 8 modules currently declare bare `str`, so each one rejects an integer regardless of `validation_mode` — `BaseClient._validate_model` calls `model_validate` before any mode branching. This task is mechanical: swap the annotation, leave `Field(...)` untouched.

**Files:**
- Modify: `fmp_data/fundamental/models.py` (lines 27, 2834)
- Modify: `fmp_data/index/models.py` (line 31)
- Modify: `fmp_data/company/models.py` (lines 110, 284, 322, 333, 553, 985)
- Modify: `fmp_data/investment/models.py` (lines 190, 222, 242, 306)
- Modify: `fmp_data/intelligence/models.py` (lines 381, 412, 556, 724, 753, 879)
- Modify: `fmp_data/institutional/models.py` (lines 25, 98, 112, 128, 239, 324, 363, 521, 550, 573, 604, 616, 744, 848, 883)
- Modify: `fmp_data/sec/models.py` (lines 22, 57, 94, 120, 153, 253)
- Modify: `fmp_data/market/models.py` (lines 297, 379, 406, 426, 444)
- Test: `tests/unit/test_models.py`

**Interfaces:**
- Consumes: `fmp_data.models.CIK` from Task 3.
- Produces: nothing new. Line numbers above are from `272fb90`; re-derive them with the command in Step 2 rather than trusting them if the files have moved.

- [ ] **Step 1: Write the failing test**

Append to `TestCIKCoercion` in `tests/unit/test_models.py`:

```python
    def test_no_model_declares_a_bare_str_cik(self) -> None:
        """Every cik field must route through the CIK coercer.

        A bare ``str`` annotation rejects an integer CIK before
        validation_mode is ever consulted, so one drifted model
        reintroduces the whole bug class.
        """
        import importlib
        import pkgutil

        import fmp_data
        from fmp_data.models import _coerce_cik

        offenders: list[str] = []
        for module_info in pkgutil.walk_packages(
            fmp_data.__path__, prefix="fmp_data."
        ):
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
```

This depends on a module-level helper. Add it to `tests/unit/test_models.py` above the class:

```python
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
```

- [ ] **Step 2: Run test to verify it fails, and get the exact work list**

Run: `python3 -m pytest tests/unit/test_models.py::TestCIKCoercion::test_no_model_declares_a_bare_str_cik -v`

Expected: FAIL listing ~45 model names.

Get the authoritative file/line list:

```bash
grep -rn "^\s*cik\s*:" fmp_data/*/models.py
```

- [ ] **Step 3: Swap the annotations**

In each file, import `CIK`. Only `fmp_data/company/models.py` already imports from
`fmp_data.models` (line 25, `from fmp_data.models import ShareFloat`) — extend that one:

```python
from fmp_data.models import CIK, ShareFloat
```

The other seven modules need a new import line; place it with the other first-party imports
and let `make format` sort it:

```python
from fmp_data.models import CIK
```

Watch for a circular import in `fmp_data/models.py` itself — it does not define `cik` fields,
so it is not in this task's file list, and nothing here imports back into it.

Then rewrite each field, keeping the `Field(...)` call byte-identical:

```python
# required — before / after
cik: str = Field(description="CIK number")
cik: CIK = Field(description="CIK number")

# optional — before / after
cik: str | None = Field(None, description="CIK number")
cik: CIK | None = Field(None, description="CIK number")

# with an alias — preserve it exactly
cik: str = Field(description="CIK number", alias="companyCik")
cik: CIK = Field(description="CIK number", alias="companyCik")
```

`fmp_data/institutional/models.py:324` is the only aliased one. `fmp_data/market/models.py:379` is the only field with no `description`; leave its `Field(default=None)` as-is.

- [ ] **Step 4: Run the test to verify it passes**

Run: `python3 -m pytest tests/unit/test_models.py::TestCIKCoercion -v`

Expected: PASS, 6 tests.

- [ ] **Step 5: Run the full unit suite to catch collateral damage**

Run: `python3 -m pytest tests/unit/ -q`

Expected: PASS. Existing tests that construct these models with string CIKs are unaffected — strings pass through the coercer untouched.

- [ ] **Step 6: Run mypy**

Run: `make lint`

Expected: no errors. `CIK` is `Annotated[str, ...]`, so it is assignable anywhere `str` was.

- [ ] **Step 7: Commit**

```bash
git add fmp_data/*/models.py tests/unit/test_models.py
git commit -m "fix(models): route all 46 cik fields through the CIK type (#131)

A bare str annotation rejects an integer CIK before validation_mode is
consulted, since _validate_model calls model_validate first. Adds a
guard so a new model cannot reintroduce a bare-str cik."
```

---

### Task 5: Record the probe finding on `InstitutionalOwnershipDates`

Probe 2 found that `institutional-ownership/dates` returns only `date`, `year`, `quarter` — no `cik` at all. The field stays (harmless, and it preserves #127's removal of a `strict`-mode "unexpected field" failure should FMP add it), but the next reader should not have to re-derive that from the live API.

**Files:**
- Modify: `fmp_data/institutional/models.py:599-607`
- Test: none — this is a docstring.

**Interfaces:**
- Consumes: nothing.
- Produces: nothing.

- [ ] **Step 1: Update the class docstring**

```python
class InstitutionalOwnershipDates(BaseModel):
    """Form 13F filing dates.

    ``cik`` is a request parameter for this endpoint, not a response field:
    probed 2026-08-07, ``institutional-ownership/dates`` returns rows
    containing only ``date``, ``year`` and ``quarter``. The field is kept
    declared so that a future API addition parses under ``strict`` mode
    rather than failing as an unexpected field; in practice it is always
    ``None``.
    """
```

- [ ] **Step 2: Verify nothing broke**

Run: `python3 -m pytest tests/unit/test_institutional.py -q`

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add fmp_data/institutional/models.py
git commit -m "docs(institutional): record that ownership/dates omits cik (#131)

Probed 2026-08-07: the endpoint returns only date, year and quarter.
Keeps the next reader from re-deriving this against the live API."
```

---

### Task 6: CHANGELOG, full verification, and open the PR

**Files:**
- Modify: `CHANGELOG.md` (under `## Unreleased`)

**Interfaces:**
- Consumes: everything from Tasks 1-5.
- Produces: a PR against `dev`.

- [ ] **Step 1: Add the CHANGELOG entry**

Under `## Unreleased`, add a `### Fixed` section. Do not touch `## [2.5.0]`.

```markdown
## Unreleased

### Fixed
- **Uncompilable enum validation patterns** (#134) - `EndpointBasedRule._get_type_pattern` emitted `^(annual|quarter))$` — one closing paren too many — for every string parameter declaring `valid_values`. The patterns are consumed by an uncaught `re.match` in `fmp_data/lc/validation.py`, so any caller reaching `ValidationRuleRegistry.get_parameter_requirements` on a live registry hit `re.error`. 22 parameters across 15 endpoints were affected (`period`, `interval`, `timeframe`, `name`).
  - Enum members now contribute their `.value` rather than their repr, so `economics.get_economic_indicators` matches `realGDP` instead of `EconomicIndicatorType.REAL_GDP`
  - Alternatives are `re.escape`d, since `valid_values` is endpoint-declared data
  - **Behaviour change:** these patterns previously always raised on use and now actually validate, so a value that used to slip through unvalidated may now be rejected
- **Integer CIK values rejected regardless of `validation_mode`** (#131) - `cik` fields were declared as bare `str`, and `BaseClient._validate_model` calls `model_validate` before any `validation_mode` branching, so an integer CIK raised a `ValidationError` under every mode. All 45 `cik` fields now use the new `fmp_data.models.CIK` type, which coerces an integer to its canonical 10-digit zero-padded form (`320193` → `"0000320193"`). Strings pass through untouched.
```

- [ ] **Step 2: Run the full check suite**

```bash
make lint
make test
```

Expected: lint clean; full unit suite passes.

- [ ] **Step 3: Confirm the #134 guard is non-vacuous**

Temporarily reintroduce the bug to prove the test catches it:

```bash
python3 - <<'EOF'
import pathlib
p = pathlib.Path("fmp_data/lc/registry.py")
s = p.read_text()
p.write_text(s.replace('return [f"^({alternatives})$"]', 'return [f"^({alternatives}))$"]'))
EOF
python3 -m pytest tests/unit/lc/test_validation_registry.py::test_every_emitted_pattern_compiles -q
git checkout fmp_data/lc/registry.py
```

Expected: the middle command FAILS. If it passes, the guard is vacuous — stop and fix it. The `git checkout` restores the fix; confirm with `python3 -m pytest tests/unit/lc/test_validation_registry.py -q` passing afterwards.

- [ ] **Step 3b: Confirm the #131 guard is non-vacuous on an OPTIONAL field**

This one has a specific trap. Pydantic surfaces `Annotated` metadata on `field.metadata` only
for *required* fields; for `CIK | None` the metadata list is empty. A guard that checks only
`field.metadata` therefore passes vacuously for every optional `cik` — and 15 of the 45 are
optional. Prove the guard catches a reverted optional field, not just a required one:

```bash
python3 - <<'EOF'
import pathlib
p = pathlib.Path("fmp_data/sec/models.py")   # line 22 cik is OPTIONAL
s = p.read_text()
assert "cik: CIK | None" in s, "expected an optional CIK field here"
p.write_text(s.replace("cik: CIK | None", "cik: str | None", 1))
EOF
python3 -m pytest tests/unit/test_models.py::TestCIKCoercion::test_no_model_declares_a_bare_str_cik -q
git checkout fmp_data/sec/models.py
```

Expected: the middle command FAILS naming a `fmp_data.sec.models` class. If it PASSES, the
guard is vacuous — `_field_uses_cik_coercer` is not walking `field.annotation`. Fix before
proceeding. Confirm restoration with `python3 -m pytest tests/unit/test_models.py -q`.

- [ ] **Step 4: Commit and push**

```bash
git add CHANGELOG.md
git commit -m "docs(changelog): record #134 and #131 fixes"
git push -u origin HEAD
```

- [ ] **Step 5: Open the PR**

```bash
gh pr create --base dev --title "fix: uncompilable enum regex and integer CIK rejection (#134, #131)" --body "$(cat <<'EOF'
Closes #134
Closes #131

Spec: `docs/superpowers/specs/2026-08-07-open-issues-remediation-design.md` §4 PR1.

## #134 — uncompilable enum regex

`_get_type_pattern` emitted `^(annual|quarter))$`. Reachable via
`EndpointBasedRule.get_parameter_requirements` ->
`ValidationRuleRegistry.get_parameter_requirements`, consumed by an
uncaught `re.match` in `validation.py:140`. 22 parameters across 15
endpoints.

Also unwraps enum members to `.value` — `economics.get_economic_indicators`
would otherwise compile a pattern that rejects every valid value — and
escapes alternatives, since `valid_values` is endpoint-declared data.

**Reviewers: this is a behaviour change.** These patterns went from
"always raise on use" to "actually validate". Values that currently slip
through unvalidated may now be rejected. That is the intended fix and the
reason #134 was kept out of #127.

## #131 — integer CIK

Live probe (2026-08-07) found `institutional-ownership/dates` returns no
`cik` field at all — only `date`, `year`, `quarter` — so the
`ValidationError` in the issue is unreachable from that endpoint. Where
`cik` *is* returned (`institutional-ownership/latest`,
`sec-filings-search/cik`) it is consistently a 10-digit zero-padded string.

New `fmp_data.models.CIK` type coerces int -> `"%010d"` and leaves strings
alone; applied to all 45 `cik` fields. Padding rather than bare `str()` so
a caller joining on `cik` across two endpoints gets one spelling.

## Tests
- `test_every_emitted_pattern_compiles` — compiles every pattern the
  registry can emit across all 168 registered endpoints
- `test_enum_valid_values_use_wire_value_not_repr`
- `TestCIKCoercion` — int padding, string pass-through, None, required-ness, bool rejection
- `test_no_model_declares_a_bare_str_cik` — guards against a new model
  reintroducing the bug class
EOF
)"
```

- [ ] **Step 6: Verify CI**

Run: `gh pr checks --watch`

Expected: all checks green. Note that merging requires `--admin` (the signed-commits rule blocks the normal path), and `Closes #N` does not fire on dev-base PRs — close #134 and #131 by hand after merge.

---

## Self-Review

**Spec coverage.** Spec §4 PR1 lists three items for #134/#131: the paren fix (Task 1), the enum `.value` fix (Task 2), and the three-part #131 resolution — keep the field (Task 4), add the coercer (Tasks 3-4), add the docstring note (Task 5). Spec §6 requires CHANGELOG entries under `## Unreleased` (Task 6, Step 1). Spec §7 requires calling the behaviour change out for reviewers (Task 6, Step 5 PR body) and the pattern-compilation guard (Task 1). All covered.

**Type consistency.** `CIK` and `_coerce_cik` are defined in Task 3 and consumed under those exact names in Tasks 4 (`field.metadata` / `getattr(meta, "func", None) is _coerce_cik`) and 5. `EndpointBasedRule(endpoints, category)` and `get_parameter_requirements(method_name)` are used identically in Tasks 1 and 2. `GroupConfig` keys `endpoint_map` / `category` match `fmp_data/lc/registry.py:23-28`.

**Defects found and fixed during self-review** (both verified against a live interpreter, not reasoned about):

1. The Task 4 guard originally checked only `field.metadata` for the `BeforeValidator`. Pydantic populates that list only for *required* fields — for `CIK | None` the `Annotated` nests inside `Optional` and the list is empty. The guard would have passed vacuously for all 15 optional `cik` fields. Fixed by adding the `field.annotation` walk in `_field_uses_cik_coercer`, and by adding Task 6 Step 3b to prove non-vacuity on an optional field specifically.
2. Task 4 originally instructed extending an existing `from fmp_data.models import ...` line in all eight modules. Only `fmp_data/company/models.py` has one. Fixed with per-module instructions.

**Known risk.** Task 4's line numbers are from `272fb90` and there is concurrent work in this repo; Step 2 re-derives them with `grep` rather than relying on the list.

**Assumptions verified against a live interpreter:** `fmp_data.economics.schema.EconomicIndicatorType` exists and its `.value`s are the wire forms (`realGDP`); the 22 string-with-`valid_values` params match the issue exactly and `economics.get_economic_indicators` is the only enum-member case; both regex defects reproduce; the `Annotated`+`BeforeValidator` CIK approach zero-pads ints, passes strings through, preserves `None`, keeps required-ness, and rejects `bool`.
