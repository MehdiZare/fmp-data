"""``EndpointParam.required`` must agree with the list the param sits in (#144).

An endpoint declares its parameters in two lists, ``mandatory_params`` and
``optional_params``, and each param separately carries a ``required`` flag. The
two say the same thing, so they can disagree -- and 14 params did, all of them
sitting in ``optional_params`` while declaring ``required=True``.

The contradiction was mostly inert. ``Endpoint.validate_params`` skips a
``None`` value for any param not in ``mandatory_params`` *before*
``validate_value`` can consult ``required``, so omitting one of the 14 always
worked. But ``validate_value`` is public, and calling it directly with ``None``
raised "Missing required parameter" for a parameter the endpoint treats as
optional.

The flags now agree with the lists. This guard keeps them agreeing: list
membership is what every consumer reads, so the flag must follow it.
"""

from __future__ import annotations

import importlib
import pkgutil

import fmp_data
from fmp_data.models import Endpoint, ParamLocation

#: Modules the walk could not import, kept so a failure can name them.
SKIPPED_MODULES: dict[str, str] = {}


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


def test_required_flag_agrees_with_list_membership() -> None:
    """A param in ``optional_params`` may not declare ``required=True``.

    Nor the reverse. Whichever way round, one of the two statements is a lie,
    and a reader has no way to tell which.
    """
    contradictions: list[str] = []
    checked = 0

    for module_name, attr, endpoint in _endpoints():
        for param in endpoint.mandatory_params:
            checked += 1
            if not param.required:
                contradictions.append(
                    f"{module_name}.{attr}.{param.name}: in mandatory_params "
                    "but required=False"
                )
        for param in endpoint.optional_params or []:
            checked += 1
            if param.required:
                contradictions.append(
                    f"{module_name}.{attr}.{param.name}: in optional_params "
                    "but required=True"
                )

    assert not contradictions, (
        "EndpointParam.required must match the list the param is declared in. "
        "List membership is what validate_params reads; the flag only reaches "
        "a direct validate_value(None) call, so a disagreement is invisible "
        "until someone hits that path. Contradictions:\n  "
        + "\n  ".join(contradictions)
    )
    # Without a floor an empty walk reads as a pass.
    assert checked > 400, f"only {checked} params inspected; is the walk working?"


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
    import re

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
    assert checked > 200, f"only {checked} endpoints inspected; walk broken?"
