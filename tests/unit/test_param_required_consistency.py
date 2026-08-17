"""``EndpointParam.required`` is derived from list membership, never stored (#165).

#144 catalogued the defect: an endpoint declares its parameters in two lists,
``mandatory_params`` and ``optional_params``, and each param *also* carried a
``required`` flag saying the same thing. Two representations of one fact, so
they could disagree -- and 14 params did, all sitting in ``optional_params``
while declaring ``required=True``.

#155 reconciled the flags and guarded the reconciliation. This file replaces
that guard, because #165 removed the second representation instead: ``required``
is a read-only property stamped by ``Endpoint`` from the list a param sits in.
There is nothing left to disagree with it.

What is asserted here, in the order the defect would have to come back:

1. No endpoint declaration passes ``required=`` any more -- a source-level scan,
   because a value that is overridden at runtime leaves no runtime trace.
2. The derived value matches list membership for every param in the catalogue.
3. The property has no setter, so it cannot be assigned back into disagreement.
4. A parameter cannot appear in both lists, the last route to being required
   and optional at once.
5. The deprecated ``required=`` argument still works, still warns, and loses to
   list membership when the two disagree.
6. A breadcrumb so 3.0 cannot ship with the argument still accepted.

``test_path_params_and_path_template_agree`` is unrelated to any of that and
predates #165; it lives here because it walks the same catalogue.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path
import pkgutil
import re
import warnings

import pytest

import fmp_data
from fmp_data.models import (
    APIVersion,
    CompanySymbol,
    Endpoint,
    EndpointParam,
    ParamLocation,
    ParamType,
)

#: Modules the walk could not import, kept so a failure can name them.
SKIPPED_MODULES: dict[str, str] = {}

#: 275 endpoints and 544 params across the catalogue today. Floors, not
#: equalities: without one, a walk that stops yielding reads as a pass.
_MIN_ENDPOINTS = 250
_MIN_PARAMS = 500


def _endpoints() -> list[tuple[str, str, Endpoint]]:
    """Every ``Endpoint`` declared in an ``*.endpoints`` module."""
    found: list[tuple[str, str, Endpoint]] = []
    for module_info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
        if not module_info.name.endswith(".endpoints"):
            continue
        try:
            module = importlib.import_module(module_info.name)
        except BaseException as exc:
            # BaseException: fmp_data/mcp/__main__.py raises SystemExit when
            # its extra is absent, and SystemExit is not an Exception. CI
            # installs no extras. Recorded rather than discarded.
            SKIPPED_MODULES[module_info.name] = f"{type(exc).__name__}: {exc}"
            continue
        for attr, value in vars(module).items():
            if isinstance(value, Endpoint):
                found.append((module_info.name, attr, value))
    return found


def _endpoint_source_files() -> list[Path]:
    """The ``fmp_data/*/endpoints.py`` files, read as text rather than imported.

    The source is the only place a ``required=`` declaration survives: at
    runtime ``Endpoint`` overwrites whatever was declared, so an import-based
    check would pass over a catalogue that had gone back to declaring it.
    """
    root = Path(fmp_data.__file__).resolve().parent
    return sorted(root.glob("*/endpoints.py"))


def test_no_endpoint_declares_a_required_flag() -> None:
    """The redundant declaration is gone from all 13 domains.

    Deleted rather than reconciled: a flag that restates list membership can
    be written wrong, and 14 of them were. Nothing to write means nothing to
    write wrong.
    """
    files = _endpoint_source_files()
    assert len(files) >= 10, (
        f"only found {len(files)} endpoint modules under "
        f"{Path(fmp_data.__file__).parent} -- has the layout moved?"
    )

    declarations: list[str] = []
    params_seen = 0

    for path in files:
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
            if name != "EndpointParam":
                continue
            params_seen += 1
            for keyword in node.keywords:
                if keyword.arg == "required":
                    declarations.append(
                        f"{path.parent.name}/endpoints.py:{node.lineno} "
                        f"EndpointParam(required=...)"
                    )

    assert not declarations, (
        "requiredness is derived from mandatory_params/optional_params "
        "membership (#165); declaring it restates the same fact in a second "
        "place that can contradict the first. Remove:\n  " + "\n  ".join(declarations)
    )
    assert params_seen >= _MIN_PARAMS, (
        f"only {params_seen} EndpointParam declarations parsed, expected "
        f">= {_MIN_PARAMS} -- did the source scan stop finding them?"
    )


def test_required_is_derived_from_list_membership() -> None:
    """Every param in the catalogue reports the requiredness of its list.

    This is the property the old guard asserted, but it now holds by
    construction rather than by maintenance: ``Endpoint._derive_param_
    requiredness`` writes it, so the only way to fail is for that stamping to
    stop happening.
    """
    wrong: list[str] = []
    checked = 0

    for module_name, attr, endpoint in _endpoints():
        for param in endpoint.mandatory_params:
            checked += 1
            if param.required is not True:
                wrong.append(
                    f"{module_name}.{attr}.{param.name}: in mandatory_params "
                    f"but required is {param.required!r}"
                )
        for param in endpoint.optional_params or []:
            checked += 1
            if param.required is not False:
                wrong.append(
                    f"{module_name}.{attr}.{param.name}: in optional_params "
                    f"but required is {param.required!r}"
                )

    assert not wrong, (
        "Endpoint must stamp requiredness onto every param it holds:\n  "
        + "\n  ".join(wrong)
    )
    assert checked >= _MIN_PARAMS, (
        f"only {checked} params inspected; is the walk working? "
        f"skipped: {SKIPPED_MODULES}"
    )


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


def test_every_param_has_a_description() -> None:
    """``description`` lost its no-default status; this covers what mypy cannot.

    Keeping the deprecated ``required`` argument in positional slot 4 forced
    ``description`` into slot 5 with a default, so omitting it is no longer a
    type error. It is still a documentation hole, and the LangChain tool
    schemas are built straight from these strings.
    """
    blank: list[str] = []
    for module_name, attr, endpoint in _endpoints():
        for param in [*endpoint.mandatory_params, *(endpoint.optional_params or [])]:
            if not param.description.strip():
                blank.append(f"{module_name}.{attr}.{param.name}")

    assert not blank, "params with no description:\n  " + "\n  ".join(blank)


def test_required_has_no_setter() -> None:
    """The flag cannot be assigned back into existence.

    A stored, writable flag is what #144 was. Read-only means a caller cannot
    reintroduce the disagreement at runtime either -- not just that the
    catalogue no longer ships one.
    """
    from fmp_data.market.endpoints import SEARCH_COMPANY

    param = SEARCH_COMPANY.mandatory_params[0]
    assert param.required is True
    with pytest.raises(AttributeError):
        param.required = False  # type: ignore[misc]
    assert param.required is True


def _param(name: str = "symbol", **kwargs: object) -> EndpointParam:
    return EndpointParam(
        name=name,
        location=ParamLocation.QUERY,
        param_type=ParamType.STRING,
        description="probe",
        **kwargs,  # type: ignore[arg-type]
    )


def _endpoint(
    mandatory: list[EndpointParam], optional: list[EndpointParam]
) -> Endpoint:
    return Endpoint(
        name="probe",
        path="probe",
        version=APIVersion.STABLE,
        description="probe",
        mandatory_params=mandatory,
        optional_params=optional,
        response_model=CompanySymbol,
    )


def test_a_param_cannot_be_in_both_lists() -> None:
    """The last remaining way to be required and optional at once.

    Nothing in the package does this, so the check is not fixing a live bug --
    it is closing the one door left open once the flag was removed. It raises
    rather than warns because there is no defensible reading of the
    declaration.
    """
    with pytest.raises(ValueError, match="both"):
        _endpoint([_param("symbol")], [_param("symbol")])


def test_declaring_required_still_works_but_warns() -> None:
    """Deprecated in 2.6, not gone: an external definition must still import."""
    with pytest.warns(DeprecationWarning) as record:
        param = _param(required=True)

    message = str(record[0].message)
    assert "required" in message
    assert "3.0" in message
    # Detached from any endpoint, the declared value is still honoured, so a
    # caller who kept the argument keeps the behaviour they had.
    assert param.required is True


def test_positional_required_in_slot_four_still_works() -> None:
    """Slot 4 stays ``required`` so old positional call sites are not shifted.

    ``EndpointParam("q", loc, typ, True, "desc")`` must still put ``True`` in
    ``required`` and ``"desc"`` in ``description``. Dropping the deprecated
    argument from the signature would land ``True`` in ``description`` instead.
    """
    with pytest.warns(DeprecationWarning):
        param = EndpointParam(
            "q",
            ParamLocation.QUERY,
            ParamType.STRING,
            True,
            "desc",
        )

    assert param.description == "desc"
    assert param.required is True


def test_omitting_required_does_not_warn() -> None:
    """The new spelling is the silent one."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        assert _param().required is False


def test_list_membership_beats_a_contradicting_declaration() -> None:
    """The exact #144 shape: ``required=True`` on a param in ``optional_params``.

    It no longer produces a parameter that two consumers read differently. The
    list wins, and the contradiction is reported rather than absorbed.
    """
    with pytest.warns(DeprecationWarning) as record:
        endpoint = _endpoint([_param("symbol")], [_param("limit", required=True)])

    assert endpoint.optional_params is not None
    assert endpoint.optional_params[0].required is False
    assert any(
        "optional_params" in str(w.message) and "limit" in str(w.message)
        for w in record
    ), f"no warning named the contradiction: {[str(w.message) for w in record]}"


def test_the_reverse_contradiction_is_also_caught() -> None:
    """``required=False`` on a mandatory param -- the other half of #144."""
    with pytest.warns(DeprecationWarning) as record:
        endpoint = _endpoint([_param("symbol", required=False)], [])

    assert endpoint.mandatory_params[0].required is True
    assert any(
        "mandatory_params" in str(w.message) and "symbol" in str(w.message)
        for w in record
    ), f"no warning named the contradiction: {[str(w.message) for w in record]}"


def test_derived_requiredness_reaches_validate_value() -> None:
    """The one read site still sees the answer, by the new route.

    ``validate_value`` is public and raises "Missing required parameter" for a
    ``None`` on a required param. ``validate_params`` skips ``None`` for
    non-mandatory params before reaching it, so this path is only observable by
    calling it directly -- which is exactly why removing the field could not
    simply drop the check.
    """
    from fmp_data.exceptions import ValidationError

    endpoint = _endpoint([_param("symbol")], [_param("limit")])

    with pytest.raises(ValidationError, match="Missing required parameter: symbol"):
        endpoint.mandatory_params[0].validate_value(None)

    assert endpoint.optional_params is not None
    assert endpoint.optional_params[0].validate_value(None) is None


def test_three_zero_must_not_ship_with_the_argument_still_accepted() -> None:
    """Breadcrumb: 3.0 drops the ``required`` slot entirely.

    Same mechanism as ``test_arg_model_deprecation``'s breadcrumb:
    ``fmp_data.__version__`` is hatch-vcs derived and falls back to ``"0.0.0"``
    when the suite imports the source tree, so the CHANGELOG is what actually
    moves in-tree.

    On failure: delete the ``required`` parameter from ``EndpointParam.__init__``
    (which restores ``description`` to positional slot 4 and to being
    mandatory), delete ``_declared_required`` and the contradiction warning in
    ``_derive_required``, and delete the five deprecation tests above.
    """
    from fmp_data import __version__

    reminder = (
        "3.0: drop the deprecated EndpointParam(required=...) argument and "
        "the contradiction warning it exists to emit"
    )

    if __version__ != "0.0.0":
        assert int(__version__.split(".")[0]) < 3, reminder

    changelog = (Path(__file__).resolve().parents[2] / "CHANGELOG.md").read_text()
    released_majors = {
        int(match) for match in re.findall(r"^## \[(\d+)\.", changelog, re.M)
    }
    assert not any(major >= 3 for major in released_majors), reminder


def test_path_params_and_path_template_agree() -> None:
    """``location=PATH`` and the ``{placeholder}``s in ``path`` must match up.

    ``build_url`` substitutes a placeholder only from a param declared
    ``ParamLocation.PATH``, and ``get_query_params`` sends only params
    declared ``ParamLocation.QUERY``. So each direction fails silently in its
    own way:

    * a placeholder with no PATH param leaves a literal ``{symbol}`` in the
      URL, which the API answers with a 404 -- this was
      ``historical-chart/{interval}/{symbol}``, where the API wants ``symbol``
      as a query parameter;
    * a PATH param absent from the template is substituted nowhere and sent
      nowhere, so the value a caller passed is **dropped without a word** --
      this was ``MUTUAL_FUND_HOLDINGS``, whose ``symbol`` never left the
      process.

    Neither shows up in the unit suite, which never builds a real URL, so the
    agreement is asserted directly here.
    """
    mismatches: list[str] = []
    checked = 0

    for module_name, attr, endpoint in _endpoints():
        checked += 1
        placeholders = set(re.findall(r"\{(\w+)\}", endpoint.path))
        path_params = {
            param.name
            for param in [
                *endpoint.mandatory_params,
                *(endpoint.optional_params or []),
            ]
            if param.location is ParamLocation.PATH
        }
        for name in sorted(placeholders - path_params):
            mismatches.append(
                f"{module_name}.{attr}: path {endpoint.path!r} has "
                f"{{{name}}} but no param declares location=PATH for it, so "
                "the placeholder survives into the request URL"
            )
        for name in sorted(path_params - placeholders):
            mismatches.append(
                f"{module_name}.{attr}: param {name!r} is location=PATH but "
                f"{endpoint.path!r} has no {{{name}}}, so it is substituted "
                "nowhere and never sent as a query param either"
            )

    assert not mismatches, (
        "path templates and PATH-located params must correspond one-to-one:"
        "\n  " + "\n  ".join(mismatches)
    )
    assert checked >= _MIN_ENDPOINTS, (
        f"only {checked} endpoints inspected; walk broken?"
    )
