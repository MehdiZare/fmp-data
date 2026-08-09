"""Guard: one ``ParameterHint`` definition per concept name (#135).

``ParameterHint`` drives natural-language parameter extraction for LangChain
tools. When two modules bind the same name to *different* hints, the same user
phrasing resolves on one tool and not another, and nothing in the codebase
compares them -- the divergence is invisible. This module scans every importable
``fmp_data`` submodule and fails if any concept name has more than one distinct
definition.

The shared definitions live in :mod:`fmp_data.lc.hints`; domain modules import
from there rather than redeclaring.

Deliberately placed outside ``tests/unit/lc/`` -- that package's ``conftest``
skips the whole directory without the ``langchain`` extra, and this guard needs
no extra beyond pydantic. CI runs the default matrix with no extras installed.
"""

from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType
from typing import Any

import fmp_data
from fmp_data.company.schema import IntradayTimeInterval
from fmp_data.lc.hints import INTERVAL_HINT
from fmp_data.lc.models import ParameterHint

# Floors, so the scan cannot pass by finding nothing. Each is set below the
# value observed at the time of writing (127 modules, 107 bindings, 22 shared
# names) with enough slack that ordinary edits do not trip it, but an import
# regression that empties the scan does.
MIN_MODULES_SCANNED = 60
MIN_HINT_BINDINGS = 80
MIN_SHARED_NAMES = 15

# Floors for the examples-vs-valid_values guard below (observed: 215 endpoints,
# 29 parameters that both constrain their values and carry a hint).
MIN_ENDPOINTS_SCANNED = 200
MIN_CONSTRAINED_PARAMS = 20

# Floor for the same-concept-different-name guard below (#157). Observed: 36
# candidate pairs, all instances of the one known divergence recorded in
# _KNOWN_SAME_CONCEPT_DIVERGENCES.
MIN_SAME_CONCEPT_CANDIDATES = 20

#: Minimum shared substring length for two ``extraction_patterns`` entries to
#: count as "the same underlying shape". Long enough that a shared capture
#: group like ``(\d{4}-\d{2}-\d{2})`` (18 chars) counts; short enough that it
#: is not defeated by a wrapping literal. Kept well above trivial fragments
#: such as ``\d+`` so two unrelated numeric patterns do not collide.
MIN_PATTERN_OVERLAP_LEN = 10

# Every module that declares or re-exports hints. Import failure here is a
# hard error, not a skip: swallowing it would let a module drop out of the
# comparison and take its divergent hints with it, which is exactly the
# invisible failure #135 is about. Only genuinely optional-extra modules
# (``fmp_data.mcp.*``, ``fmp_data.lc.vector_store``) may fail to import.
MUST_IMPORT = [
    "fmp_data.alternative.mapping",
    "fmp_data.batch.mapping",
    "fmp_data.company.hints",
    "fmp_data.company.mapping",
    "fmp_data.economics.mapping",
    "fmp_data.fundamental.mapping",
    "fmp_data.institutional.mapping",
    "fmp_data.intelligence.mapping",
    "fmp_data.investment.mapping",
    "fmp_data.lc.hints",
    "fmp_data.market.hints",
    "fmp_data.market.mapping",
    "fmp_data.sec.mapping",
    "fmp_data.technical.mapping",
    "fmp_data.transcripts.mapping",
]

#: Modules the package walk could not import, recorded rather than discarded so
#: a failure message can say what fell out of the scan.
SKIPPED_MODULES: dict[str, str] = {}


def test_every_hint_bearing_module_imports() -> None:
    """No hint-bearing module may drop out of the scan below via ImportError."""
    broken: dict[str, str] = {}
    for name in MUST_IMPORT:
        try:
            importlib.import_module(name)
        except BaseException as exc:  # SystemExit is not an Exception
            broken[name] = f"{type(exc).__name__}: {exc}"
    assert not broken, f"hint-bearing modules failed to import: {broken}"


def _iter_fmp_modules() -> list[ModuleType]:
    """Import every ``fmp_data`` submodule that imports cleanly.

    Optional-extra modules are allowed to fail; the hint-bearing ones are
    pinned by :func:`test_every_hint_bearing_module_imports` above, so a
    regression there fails loudly instead of shrinking this scan.
    """
    modules: list[ModuleType] = [fmp_data]
    for info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
        try:
            modules.append(importlib.import_module(info.name))
        except BaseException as exc:
            # BaseException, not Exception: fmp_data/mcp/__main__.py calls
            # sys.exit(1) when the mcp extra is absent, and SystemExit does
            # not inherit from Exception. Catching only Exception let that
            # escape and failed the whole scan in a core-only install --
            # which is how CI runs.
            SKIPPED_MODULES[info.name] = f"{type(exc).__name__}: {exc}"
    return modules


def _hint_bindings(module: ModuleType) -> dict[str, ParameterHint]:
    """Module-level ``ParameterHint`` bindings, including those inside dicts.

    Dict-valued collections (``DATE_HINTS``, ``SYMBOL_HINTS``) are unpacked as
    ``NAME[key]`` so a divergent entry inside one is caught too -- excluding
    them would leave the four ``DATE_HINTS`` copies unguarded.
    """
    bindings: dict[str, ParameterHint] = {}
    for attr, value in vars(module).items():
        if attr.startswith("_"):
            continue
        if isinstance(value, ParameterHint):
            bindings[attr] = value
        elif isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, ParameterHint) and isinstance(key, str):
                    bindings[f"{attr}[{key}]"] = item
    return bindings


def _collect() -> tuple[dict[str, dict[str, ParameterHint]], int, int]:
    """Map concept name -> {module name: hint}, plus scan-size counters."""
    by_name: dict[str, dict[str, ParameterHint]] = {}
    modules = _iter_fmp_modules()
    total_bindings = 0
    for module in modules:
        for name, hint in _hint_bindings(module).items():
            by_name.setdefault(name, {})[module.__name__] = hint
            total_bindings += 1
    return by_name, len(modules), total_bindings


def test_no_two_modules_define_the_same_hint_differently() -> None:
    """Same name, different contents, in two modules is the #135 defect."""
    by_name, module_count, binding_count = _collect()

    # Floor assertions: a scan that imported nothing must not read as a pass.
    assert module_count >= MIN_MODULES_SCANNED, (
        f"only {module_count} fmp_data modules imported; the scan is not "
        "covering the package and this guard would pass vacuously. Modules "
        f"that failed to import: {SKIPPED_MODULES}"
    )
    assert binding_count >= MIN_HINT_BINDINGS, (
        f"only {binding_count} ParameterHint bindings found; expected at least "
        f"{MIN_HINT_BINDINGS}"
    )
    shared = {name: mods for name, mods in by_name.items() if len(mods) > 1}
    assert len(shared) >= MIN_SHARED_NAMES, (
        f"only {len(shared)} hint names are visible from more than one module; "
        "the consolidated hints should be imported widely, so this guard is "
        "not actually comparing anything"
    )

    conflicts: list[str] = []
    for name, modules in sorted(shared.items()):
        distinct: dict[str, list[str]] = {}
        for module_name, hint in sorted(modules.items()):
            distinct.setdefault(hint.model_dump_json(), []).append(module_name)
        if len(distinct) > 1:
            groups = " vs ".join(
                f"{', '.join(mods)}" for mods in sorted(distinct.values())
            )
            conflicts.append(f"{name}: {groups}")

    assert not conflicts, (
        "ParameterHint constants must have exactly one definition per name. "
        "Move the concept to fmp_data.lc.hints and import it. Divergent:\n  "
        + "\n  ".join(conflicts)
    )


def test_interval_hint_examples_track_the_intraday_interval_enum() -> None:
    """``INTERVAL_HINT`` examples are spelled out, so pin them to the enum.

    ``company/hints.py`` used ``examples=list(IntradayTimeInterval)``. Moving
    that into ``lc/hints.py`` would make the shared hints module depend on a
    domain schema, so the values are written literally instead -- and pinned
    here so adding an interval to the enum fails until the hint catches up.
    """
    assert set(INTERVAL_HINT.examples) == {e.value for e in IntradayTimeInterval}


def test_period_and_period_length_stay_distinct_concepts() -> None:
    """``period`` (reporting frequency) is not ``periodLength`` (lookback).

    Merging them would offer ``annual`` as a value for a 14-day RSI window and
    ``50`` as a value for a financial-statement period. See the #135 PR body.
    """
    from fmp_data.lc.hints import PERIOD_HINT, PERIOD_LENGTH_HINT

    assert PERIOD_HINT != PERIOD_LENGTH_HINT
    frequency_examples = {str(e).lower() for e in PERIOD_HINT.examples}
    lookback_examples = {str(e) for e in PERIOD_LENGTH_HINT.examples}
    assert "annual" in frequency_examples
    assert not any(e.isdigit() for e in frequency_examples)
    # Non-empty, else the digit assertion below passes vacuously.
    assert lookback_examples
    assert all(e.isdigit() for e in lookback_examples)


def test_the_three_period_hints_match_their_valid_values_sets() -> None:
    """``period`` is three hints because the catalog gives it three value sets.

    A single union hint advertised ``FY``/``Q1`` to the three company endpoints
    that accept only ``annual``/``quarter``, and ``annual``/``quarter`` to the
    six bulk endpoints that accept only fiscal labels. Both are rejected by
    ``EndpointParam.validate_value``, so the tool description promised what the
    client refuses to send. The catalog-wide guard below would catch a
    re-merge; this pins the intended shape directly.
    """
    from fmp_data.lc.hints import (
        FISCAL_PERIOD_HINT,
        PERIOD_HINT,
        PERIOD_WITH_FISCAL_HINT,
    )

    plain = {str(e).lower() for e in PERIOD_HINT.examples}
    with_fiscal = {str(e).lower() for e in PERIOD_WITH_FISCAL_HINT.examples}
    fiscal_only = {str(e).lower() for e in FISCAL_PERIOD_HINT.examples}

    assert plain == {"annual", "quarter"}
    assert plain < with_fiscal, "the fiscal variant must still accept the plain values"
    assert "fy" in with_fiscal
    # Fiscal-only: never the plain frequencies, since the bulk endpoints reject
    # them. It enumerates all four quarters, which the fiscal variant does not.
    assert fiscal_only and not (fiscal_only & {"annual", "quarter"})
    assert {"fy", "q1", "q4"} <= fiscal_only


def test_hint_examples_are_within_valid_values() -> None:
    """Advertised examples must be values the endpoint actually accepts.

    ``ToolFactory.generate_description`` renders ``hint.examples`` verbatim into
    the tool description an LLM reads, while ``EndpointParam.validate_value``
    rejects anything outside ``valid_values`` -- and ``create_parameter_fields``
    does not narrow the generated field type, so the enum never reaches the
    model. When the two disagree the catalog advertises a value that fails
    client-side, which is what one shared ``PERIOD_HINT`` did for nine
    endpoints until it was split three ways.
    """
    from fmp_data.lc.registry import (
        get_endpoint_groups,
        resolve_semantics_for_endpoint,
    )

    offenders: list[str] = []
    endpoints_scanned = 0
    constrained_params = 0

    for group in get_endpoint_groups().values():
        for endpoint_name, endpoint in group["endpoint_map"].items():
            semantics = resolve_semantics_for_endpoint(
                endpoint_name, group["semantics_map"]
            )
            if semantics is None:
                continue
            endpoints_scanned += 1
            params = list(endpoint.mandatory_params or []) + list(
                endpoint.optional_params or []
            )
            for param in params:
                valid_values = getattr(param, "valid_values", None)
                hint = (semantics.parameter_hints or {}).get(param.name)
                if not valid_values or hint is None:
                    continue
                constrained_params += 1
                allowed = {str(value).lower() for value in valid_values}
                rejected = [
                    example
                    for example in hint.examples
                    if str(example).lower() not in allowed
                ]
                if rejected:
                    offenders.append(
                        f"{endpoint_name}.{param.name}: advertises {rejected}, "
                        f"but valid_values is {list(valid_values)}"
                    )

    assert endpoints_scanned >= MIN_ENDPOINTS_SCANNED, (
        f"only {endpoints_scanned} endpoints resolved semantics; the scan is "
        "not covering the catalog and this guard would pass vacuously"
    )
    assert constrained_params >= MIN_CONSTRAINED_PARAMS, (
        f"only {constrained_params} parameters both constrain their values and "
        f"carry a hint; expected at least {MIN_CONSTRAINED_PARAMS}"
    )
    assert not offenders, (
        "these parameter hints advertise examples the endpoint rejects:\n  "
        + "\n  ".join(sorted(offenders))
    )


def _domain(module_name: str) -> str:
    """``fmp_data.company.mapping`` -> ``company``; top-level -> ``""``."""
    parts = module_name.split(".")
    return parts[1] if len(parts) > 2 else ""


def test_cross_domain_hints_originate_in_lc_hints() -> None:
    """A hint used by two domain packages must be defined in ``lc.hints``.

    A domain-local hint that its own mapping module imports (``STRUCTURE_HINT``
    in ``company``) is fine -- one definition, one owner. What is not fine is
    two domains reaching for the same concept name without a shared source,
    because that is how the copies in #135 drifted apart in the first place.
    """
    from fmp_data.lc import hints as shared_hints

    by_name, _, _ = _collect()
    offenders = sorted(
        name
        for name, mods in by_name.items()
        if len({_domain(m) for m in mods} - {"lc", ""}) > 1
        and not hasattr(shared_hints, name.split("[", 1)[0])
    )
    assert not offenders, (
        "these hint names are used by more than one domain package but are "
        f"not defined in fmp_data.lc.hints: {offenders}"
    )


# --- #157: same concept, different name ------------------------------------
#
# test_no_two_modules_define_the_same_hint_differently above proves "one
# name -> one definition". It cannot see a concept redefined under a SECOND
# name, which is exactly how fmp_data.technical.mapping.FROM_DATE_HINT /
# TO_DATE_HINT drifted from fmp_data.lc.hints.DATE_HINTS["start_date"] /
# ["end_date"]: different examples, different extraction_patterns, same
# "date range boundary" concept, and nothing compares them because the names
# differ and technical is the sole importer of its own copies (single owner,
# so test_cross_domain_hints_originate_in_lc_hints does not see it either).
#
# Rule: two ParameterHint bindings under different names, in different
# modules, are flagged as a likely same-concept duplicate when BOTH hold:
#
#   1. natural_names overlap -- they share at least one phrasing, so the same
#      user query can resolve to either tool's parameter.
#   2. extraction_patterns overlap (see _pattern_overlap) -- one pattern is a
#      long-enough literal substring of the other, which catches "the same
#      capture group wrapped in different surrounding text" (the ISO-date
#      group ``(\d{4}-\d{2}-\d{2})`` sitting inside ``from\s+(\d{4}-\d{2}-\d{2})``)
#      without demanding byte-identical pattern strings.
#
# Both are required, not either. A single shared generic word is too weak on
# its own: PERIOD_HINT / INTERVAL_HINT / PERIOD_LENGTH_HINT in lc/hints.py all
# list "period" in natural_names but extract nothing in common, and flagging
# that trio would be exactly the noise #157 warns against. A shared pattern
# fragment without shared phrasing is typically coincidence (two unrelated
# concepts that both happen to extract a number). Requiring both signals is
# what keeps the rule predictable: a maintainer can tell in advance that it
# trips only when a user phrase AND the text it extracts both line up.
#
# Deliberately NOT flagged: a hint whose extraction_patterns are an exact
# subset of another's (see _is_extension) is a reviewed refinement -- e.g.
# PERIOD_HINT's three patterns are a strict subset of
# PERIOD_WITH_FISCAL_HINT's four, by design (see the CONFLICT note in
# lc/hints.py: the catalog genuinely has three different valid_values sets
# for "period", pinned by test_the_three_period_hints_match_their_valid_values_sets
# above). Treating that as a #157 violation would be crying wolf on a shape
# the maintainers already reviewed and tested.
def _pattern_overlap(a: list[str], b: list[str]) -> bool:
    """True if some pattern in ``a`` is a literal substring of one in ``b``."""
    return any(
        len(pa) >= MIN_PATTERN_OVERLAP_LEN
        and len(pb) >= MIN_PATTERN_OVERLAP_LEN
        and (pa in pb or pb in pa)
        for pa in a
        for pb in b
    )


def _is_extension(a: list[str], b: list[str]) -> bool:
    """True if one extraction_patterns list is an exact subset of the other."""
    set_a, set_b = set(a), set(b)
    return set_a <= set_b or set_b <= set_a


def _same_concept_candidates() -> list[tuple[str, str, str, str]]:
    """Cross-module, cross-name hint pairs that look like the same concept.

    Returns ``(module_a, name_a, module_b, name_b)`` tuples. See the module
    comment above for the rule.
    """
    by_name, _, _ = _collect()
    flat = [
        (name, module_name, hint)
        for name, modules in by_name.items()
        for module_name, hint in modules.items()
    ]
    candidates: list[tuple[str, str, str, str]] = []
    for i, (name_a, mod_a, hint_a) in enumerate(flat):
        for name_b, mod_b, hint_b in flat[i + 1 :]:
            if name_a == name_b or mod_a == mod_b or hint_a is hint_b:
                continue
            if hint_a.model_dump_json() == hint_b.model_dump_json():
                continue  # identical contents: not a divergence
            nn_a = {n.lower() for n in hint_a.natural_names}
            nn_b = {n.lower() for n in hint_b.natural_names}
            if not nn_a & nn_b:
                continue
            if _is_extension(hint_a.extraction_patterns, hint_b.extraction_patterns):
                continue
            if not _pattern_overlap(
                hint_a.extraction_patterns, hint_b.extraction_patterns
            ):
                continue
            candidates.append((mod_a, name_a, mod_b, name_b))
    return candidates


#: Pre-existing, tracked divergence (#157's "Options" section): folding
#: technical/mapping.py's local FROM_DATE_HINT/TO_DATE_HINT onto the shared
#: fmp_data.lc.hints.DATE_HINTS changes the embedding text and tool
#: descriptions of nine indicator tools, which #157 scoped as its own
#: before/after review rather than a guard-only change. Recorded here, not
#: silently dropped: the test below asserts every entry still trips the raw
#: detector, so both "the duplication got fixed" (entry now unused) and "the
#: duplication rotted further out of view" (entry stops matching) fail loudly
#: instead of the allowlist quietly widening.
KNOWN_SAME_CONCEPT_DIVERGENCES = {
    ("fmp_data.technical.mapping", "FROM_DATE_HINT"),
    ("fmp_data.technical.mapping", "TO_DATE_HINT"),
    ("fmp_data.technical.mapping", "COMMON_PARAMS[from]"),
    ("fmp_data.technical.mapping", "COMMON_PARAMS[to]"),
}


def test_no_same_concept_hint_under_a_different_name() -> None:
    """Same concept, different binding name, is the #157 gap in #135's guard.

    New same-concept duplicates must either import the shared hint or be
    added to ``KNOWN_SAME_CONCEPT_DIVERGENCES`` with a reason -- silently
    passing is not an option either way.
    """
    candidates = _same_concept_candidates()

    # Floor: a detector that finds nothing is not proof there is nothing to
    # find. Pinned above the count observed at the time of writing so a
    # change that breaks the comparison (e.g. an accidental early `continue`
    # above) fails here instead of passing vacuously.
    assert len(candidates) >= MIN_SAME_CONCEPT_CANDIDATES, (
        f"only {len(candidates)} same-concept candidate pairs found; the "
        "comparison in _same_concept_candidates may not be running"
    )

    seen_allowlisted: set[tuple[str, str]] = set()
    unexpected: list[str] = []
    for mod_a, name_a, mod_b, name_b in candidates:
        allowed_a = (mod_a, name_a) in KNOWN_SAME_CONCEPT_DIVERGENCES
        allowed_b = (mod_b, name_b) in KNOWN_SAME_CONCEPT_DIVERGENCES
        if allowed_a:
            seen_allowlisted.add((mod_a, name_a))
        if allowed_b:
            seen_allowlisted.add((mod_b, name_b))
        if not (allowed_a or allowed_b):
            unexpected.append(f"{mod_a}.{name_a} vs {mod_b}.{name_b}")

    assert not unexpected, (
        "these hint pairs look like the same concept under different names "
        "(shared phrasing in natural_names, shared shape in "
        "extraction_patterns). Either import the shared fmp_data.lc.hints "
        "definition, or -- if this is a reviewed, deliberate copy -- add it "
        "to KNOWN_SAME_CONCEPT_DIVERGENCES with a reason:\n  " + "\n  ".join(unexpected)
    )

    # An allowlist entry that no longer appears among the candidates is
    # stale: either the duplication was fixed (drop the entry) or the
    # detector itself regressed (a real bug -- do not shrink the allowlist
    # to hide it).
    stale = KNOWN_SAME_CONCEPT_DIVERGENCES - seen_allowlisted
    assert not stale, (
        "these KNOWN_SAME_CONCEPT_DIVERGENCES entries no longer appear among "
        f"the detected candidates and should be removed: {stale}"
    )


def test_collected_hints_are_typed() -> None:
    """Sanity: the collector really is yielding ``ParameterHint`` values."""
    by_name, _, _ = _collect()
    assert by_name, "no hints collected at all"
    sample: dict[str, ParameterHint] = next(iter(by_name.values()))
    value: Any = next(iter(sample.values()))
    assert isinstance(value, ParameterHint)
