# Open-issue remediation design

**Date:** 2026-08-07
**Base:** `dev` @ `272fb90` (PR #127 merged)
**Scope:** the nine open issues remaining after #127, delivered as four themed PRs.

## 1. Current state

Twelve issues were open at the start of this pass. Three are already fixed and only need
closing; nine need work.

### Already fixed by #127 — closed, do not re-implement

`closes #N` is inert on dev-base PRs, so #127 merged without closing its linked issues; all
three were closed by hand shortly afterwards (2026-08-07 15:47Z, reason `COMPLETED`, each with
a pointer to `272fb90`). Recorded here so this pass does not re-open or re-implement them.
Verified against the merged tree:

| Issue | Claim | Evidence in `272fb90` |
|---|---|---|
| #121 | `register_batch` aborts whole client group | Now returns `dict[str, str]` of failures and skips invalid endpoints (`lc/registry.py:538`) |
| #123 | Semantics hint / catalog-count drift | Hint drift and docs sync landed |
| #125 | `tests/` unchecked by mypy | `"tests/"` removed from `[tool.mypy].exclude`; `tests.*` override added exactly as proposed (`pyproject.toml:244`, `:310`) |

No action required. Nine issues remain open: #126, #128, #129, #130, #131, #133, #134, #135, #136.

### Measured baseline

| Quantity | Value |
|---|---|
| Registry groups (`_get_endpoint_groups`) | 9 |
| Registry endpoints | 168 |
| MCP catalog tools (`discover_all_tools`) | 224 |
| `DEFAULT_TOOLS` | 159 |

## 2. Live API probe results

Two issues rested on unverified claims about the FMP API. Both were probed against the live
`stable` API on 2026-08-07. Per repo convention, endpoint behaviour is verified rather than
assumed — VCR cassettes are gitignored and so are not checkable from a clean checkout.

### Probe 1 — does `cik-list` support a name filter? **No.**

`GET /stable/cik-list` with `name=Apple`, with `company=Apple`, and with no filter at all
returned byte-identical unfiltered pages. The in-code comment on
`InstitutionalClient.search_cik_by_name` ("The FMP API does not support server-side name
filtering") is accurate.

**Consequence:** #130 option 1 is confirmed correct rather than merely plausible.
`CIK_MAPPER_BY_NAME` models a filter that does not exist and, called through the LangChain
tool layer, is a byte-for-byte duplicate of `CIK_MAPPER`. Removing it is the honest fix.

### Probe 2 — does `institutional-ownership/dates` return `cik` as an integer? **It never returns `cik` at all.**

`GET /stable/institutional-ownership/dates?cik=0001067983` returned 52 rows whose only keys
are `date`, `year`, `quarter`. Padded (`0001067983`) and unpadded (`1067983`) CIK inputs both
work and return the same body. `cik` is a request parameter that is never echoed into the
response.

**This refutes #131's framing.** The issue asks which type `cik` arrives as; the answer is
that it does not arrive. `InstitutionalOwnershipDates.cik` (`institutional/models.py:604`) is a
phantom field that is always `None` in practice, so the `ValidationError` the issue describes
is unreachable from any live call through `get_institutional_ownership_dates`.

Where `cik` *is* returned elsewhere, it is consistently a **10-digit zero-padded string**:

| Endpoint | Observed `cik` |
|---|---|
| `institutional-ownership/latest` | `"0001775391"` (str) |
| `sec-filings-search/cik` | `"0000320193"` (str) |

No integer CIK was observed anywhere on the probed surface.

**Limitation, stated explicitly:** this is one API plan tier, two endpoints, and one CIK for
probe 2. It is strong evidence that `str` is the correct declared type, and it is *not* proof
that no FMP endpoint on any tier ever emits an integer. The design below therefore keeps a
defensive coercer rather than treating the probe as a proof of impossibility.

## 3. Decisions

| # | Decision | Chosen |
|---|---|---|
| D1 | MCP tool-key namespace policy (#126, #130, #136) | One key per `(client, method)`; deprecate aliases over 2.6 → 3.0 |
| D2 | `create_vector_store` error contract (#133) | Dedicated `VectorStoreCreationError`, raised in 2.6, no `None` path |
| D3 | Verify #130/#131 against the live API | Yes — done, see §2 |
| D4 | Delivery shape | Four themed PRs |
| D5 | Int CIK coercion form (#131) | Zero-pad to 10 digits; ints only, strings untouched |
| D6 | Conflicting hint patterns (#135) | Union of existing patterns; record each genuine conflict in the PR body |

### D2 rationale

`create_vector_store` has exactly one caller-reachable `return None` — the blanket
`except Exception` at `lc/__init__.py:257`. The two `return None`s inside
`try_load_existing_store` (`:285`, `:289`) fall through to `create_new_store` and never reach
the caller. So `None` unconditionally means "something threw"; it carries no information a
caller can act on.

That is why the narrower "let a typed subset out" option was rejected: it would preserve a
sentinel whose only meaning is "an error you cannot inspect", fixing visibility for
`ImportError`/`ConfigError` while leaving every other failure exactly as silent as today. A
raised exception carrying `cause` and `failures` also settles #133's closing note — that
`setup_registry` inspects `register_batch`'s failure dict and then discards it, leaving log
parsing as the only way to learn which endpoints were skipped.

## 4. The four PRs

Ordered by blast radius. Each lands independently against `dev`.

---

### PR1 — contained correctness fixes (#134, #131)

**#134 — uncompilable enum regex.** `lc/registry.py:272` has one closing paren too many:

```python
# before
return [
    f"^({'|'.join(map(str, valid_values))}))$"
]  # -> "^(annual|quarter))$"  re.error
# after
return [
    f"^({'|'.join(v.value if hasattr(v, 'value') else str(v) for v in valid_values)})$"
]
```

The same line has a second defect the issue flags: `economics.get_economic_indicators` passes
enum *members*, so `map(str, ...)` yields `EconomicIndicatorType.GDP` rather than `GDP`. Both
are fixed together — fixing only the paren would produce a pattern that compiles and then
silently rejects every valid value.

Reachability: `_get_type_pattern` → `EndpointBasedRule.get_parameter_requirements` (`:299`) →
`ValidationRuleRegistry.get_parameter_requirements` (`:370`), consumed by an uncaught
`re.match` in `lc/validation.py:140`. 22 parameters across 15 endpoints hit this branch.

**Behaviour change to call out in review:** these patterns go from "always raise on use" to
"actually validate". Values that currently slip through unvalidated may now be rejected. This
is the intended fix, but it is the reason #134 was kept out of #127.

**#131 — `cik` typing.** Given probe 2, the fix is not the one the issue proposed:

1. Keep `cik: str | None` on `InstitutionalOwnershipDates`. It is harmless, matches the
   convention in `sec/`, `investment/` and `intelligence/` models, and preserves #127's
   removal of a `strict`-mode "unexpected field" failure should FMP ever add the field.
2. Add a shared `field_validator(mode="before")` coercing an int CIK to the canonical
   zero-padded 10-digit string, and apply it to every `cik` field across the codebase
   (#131 step 3).
3. Add a docstring note recording that this endpoint does not return `cik`, with the probe
   date — so the next reader does not re-derive it.

**Zero-padding — decided: pad to 10 digits.** A bare `str(320193)` yields `"320193"`, which
will not compare equal to the `"0000320193"` every probed endpoint returns. The coercer emits
`f"{v:010d}"` so callers see one canonical form regardless of how the producer serialised it.
This normalises a value rather than merely retyping it, which is deliberate: a CIK is a
fixed-width zero-padded identifier, and a caller keying a dict or joining on `cik` across two
endpoints must not get two spellings of the same institution.

Applies to ints only. A string that arrives already unpadded is left alone — re-padding
strings would silently rewrite whatever an endpoint actually sent, which is a bigger claim
than the probe evidence supports.

**Tests:** compile every pattern returned by `get_parameter_requirements` for all 168
registered endpoints (guards #134 against regression); round-trip int and str CIKs through
each model carrying a `cik` field.

---

### PR2 — LangChain tool-schema correctness (#128, #129)

**#128 — every parameter marked required.** `ToolFactory.create_parameter_fields`
(`lc/vector_store.py:82`) builds `Field(description=...)` with no default, so pydantic treats
every parameter as required. `get_field_type(..., optional=(param.default is not None))`
widens the *type* to `| None` but never supplies a default.

The issue notes an unresolved question that must be settled here: `param.default is not None`
is not the same question as "is this in `mandatory_params`", and the two should be reconciled
in the same change. The call site at `:584` already concatenates
`mandatory_params + (optional_params or [])`, so membership is available — the fix threads
mandatory-ness through explicitly instead of inferring it from `default`.

**#129 — four unguarded modules.** `batch`, `index`, `sec` and `transcripts` are absent from
`_get_endpoint_groups()`, so their semantics never reach `validate_endpoint()`. 33 endpoints
there declare `parameter_hints={}` while taking real parameters:

| module | endpoints | drifted |
|---|---|---|
| `batch` | 30 | 22 |
| `sec` | 12 | 9 |
| `transcripts` | 4 | 2 |
| `index` | 6 | 0 |

Adding the groups (168 → 216 guarded, as built; this line first estimated 224, which
double-counted — the four modules add 52 endpoints, not 56, and four more are held out
as cross-client collisions) reds CI immediately, so the two halves must land
together — registering the groups and filling the hints from `fmp_data.lc.hints` in one
commit. Each of the four modules also needs a `SemanticCategory` assignment, since
`_get_endpoint_groups()` assigns one per group.

**Sequencing note:** PR2 must land after PR1. Bringing 56 more endpoints under
`validate_endpoint()` widens the surface that PR1's now-compiling regexes run against; landing
them in the other order means debugging both changes at once.

**Tests:** for every registered endpoint, assert the generated tool schema's required-field set
equals `{p.name for p in endpoint.mandatory_params}` (#128's proposed guard); the existing #127
hint-drift guard extends to all 224 endpoints for free once the groups are registered.

---

### PR3 — tool-key namespace policy (#126, #130, #136)

The one PR with a public surface change. Establishes the invariant: **one tool key per
`(client, method)` pair.**

| Action | Key | Rationale |
|---|---|---|
| Remove now | `institutional.cik_mapper_by_name` | Dead, not an alias — probe 1 confirms no name filter exists |
| Deprecate → 3.0 | `historical_price` → `historical_prices` | #136 |
| Deprecate → 3.0 | `intraday_price` → `intraday_prices` | #136 |
| Deprecate → 3.0 | `executives` → `key_executives` | #136 |
| Deprecate → 3.0 | key-only `crypto_quotes`, `forex_quotes` | #126 — require `alternative.*` / `batch.*` |

Catalog: 224 → 223 in 2.6, → 220 in 3.0 (three deprecated keys removed, not five —
the two ambiguous `crypto_quotes` / `forex_quotes` keys stay in the catalog, since
only *bare-key resolution* of them is dropped, not either tool).

`cik_mapper_by_name` is removed outright rather than deprecated because it is not a second name
for a working tool — it is a tool that cannot express the operation it claims. The sync/async
`search_cik_by_name` client methods are the genuine interface and are unaffected; they keep
fetching `limit=10000` and filtering locally, which probe 1 confirms is the only option.

Deprecated keys keep resolving for one minor version behind a `DeprecationWarning` naming the
replacement. Closing #126 means emptying the shrinking allowlist in
`tests/unit/test_mcp.py::TestSemanticsMethodResolution::test_discovered_tool_keys_are_unambiguous_globally`.

`docs/mcp/tools.md` counts move with the catalog. CHANGELOG announces all five deprecations
and the one removal under a "Deprecated" heading with the 3.0 removal target.

**Not in scope:** #130 option 3 — teaching the LangChain tool layer to dispatch through client
methods rather than `client.request`, so wrappers carrying real logic become reachable. That is
the general form of the problem and deserves its own design pass. Recorded as follow-up.

---

### PR4 — cross-cutting cleanups (#135, #133)

**#135 — duplicated `ParameterHint` constants.** #127 added shared hints to `lc/hints.py` but
did not retire the per-module copies, so the same concept exists under the same name in several
places with *different extraction patterns*. Confirmed duplicates:

| Constant | Locations |
|---|---|
| `CIK_HINT` | `lc/hints.py:47`, `company/hints.py:11`, `institutional/mapping.py:36`, `investment/mapping.py:62` |
| `PAGE_HINT` | `lc/hints.py:58`, `institutional/mapping.py:56`, `fundamental/mapping.py:105`, `intelligence/mapping.py:181` |
| `LIMIT_HINT` | `lc/hints.py:3`, `fundamental/mapping.py:87`, `intelligence/mapping.py:191` |
| `SYMBOL_HINT` | `lc/hints.py:33`, `institutional/mapping.py:25`, `fundamental/mapping.py:44`, `investment/mapping.py:27`, `intelligence/mapping.py:115` |
| `YEAR_HINT`, `QUARTER_HINT` | `lc/hints.py:89`/`:99`, `investment/mapping.py:48`/`:55` |
| `PERIOD_HINT` | `lc/hints.py:24`, `fundamental/mapping.py:64` |

The migration is partial *within a single file*, not merely across files.
`institutional/mapping.py:16` imports the shared `LIMIT_HINT`, `YEAR_HINT` and `QUARTER_HINT`,
while the same file keeps local copies of `SYMBOL_HINT` (:25), `CIK_HINT` (:36) and `PAGE_HINT`
(:56). Meanwhile `intelligence/mapping.py:50` imports the shared `CIK_HINT` but defines local
`PAGE_HINT` (:181) and `LIMIT_HINT` (:191). So `cik` extracts one way in `intelligence` and
another in `institutional`, and `limit` extracts one way in `institutional` and another in
`intelligence` — the two files disagree in opposite directions, for no principled reason.

For each concept: pick one pattern set (union of the existing patterns unless they conflict,
in which case the decision is recorded in the PR body), move it to `lc/hints.py`, import it in
the domain modules, delete the duplicate. This changes extraction behaviour wherever the winning
pattern differs from the local one — which is the point, and why it is not a mechanical edit.

**Test:** assert no two modules define a `ParameterHint` under the same name with different
contents.

**#133 — `create_vector_store` error contract.** Per D2:

```python
class VectorStoreCreationError(FMPError):
    """Raised when a vector store cannot be built."""

    cause: Exception
    failures: dict[str, str]  # endpoint name -> validation error
```

- `create_vector_store` return type narrows to `EndpointVectorStore` (no `| None`).
- The blanket handler at `lc/__init__.py:257` re-raises as `VectorStoreCreationError`,
  preserving `cause` and attaching the per-endpoint `failures` dict.
- `setup_registry` return type widens to carry `register_batch`'s failure dict, so failures are
  programmatically reachable instead of log-only.
- `try_load_existing_store`'s internal `None` returns are untouched — they mean "fall through to
  create", not "error", and remain internal.
- README (`:226`, `:289`), `LLM.md:85` and `tests/integration/test_lc.py` (`:47`, `:79`) migrate
  from `if store is None` to `try/except VectorStoreCreationError`.
- CHANGELOG documents the break with the before/after migration snippet.

PR4 lands last: #135 touches every mapping module, and #133 changes a public signature.

## 5. Non-goals

- No full test-suite typing sweep (#125's step 3/4 burn-down stays open as its own track).
- No LangChain client-method dispatch rework (#130 option 3) — follow-up.
- No re-litigating #127's decisions; this builds on them.
- No unrelated refactoring in touched files.

## 6. Release targeting

The CHANGELOG's `## [2.5.0] - 2026-08-07` section was cut while this design was being written
(`525a0bb`), so 2.5.0 is closed to new entries. All four PRs land under `## Unreleased`, which
becomes **2.6.0**. Deprecations introduced by PR3 and the breaking change in PR4 are therefore
announced in 2.6.0 with removal in 3.0.

**Pre-existing version drift, not this pass's to fix:** the newest git tag is `v2.4.0` while
the CHANGELOG documents 2.5.0. Since `[tool.hatch.version]` derives the package version from
tags, a build from `dev` today reports a `2.4.x`-series dev version rather than 2.5.0. This
does not block any of the four PRs — they only append to `## Unreleased` — but 2.5.0 needs
tagging before 2.6.0 can be cut, or the two releases will collapse into one.

## 7. Risks

| Risk | Mitigation |
|---|---|
| PR1 flips 22 params from unvalidated to validated; some may newly reject | Pattern-compilation test over all endpoints; call out in PR body for review |
| PR2's two halves cannot be split without redding CI | Land as one PR, stated in the description |
| PR3 removes a public tool key | Only the dead one is removed now; the four live aliases get a full deprecation cycle |
| PR4's hint consolidation silently changes NL extraction | Record each conflicting-pattern decision in the PR body; add the same-name/different-content guard |
| Probe evidence is one plan tier | Coercer kept defensively rather than relying on the probe as proof |
