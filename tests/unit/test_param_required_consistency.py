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
from fmp_data.models import Endpoint

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
