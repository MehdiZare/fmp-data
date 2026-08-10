"""Every module in the package must import.

#139 sat undetected because nothing in the suite imported
``fmp_data.investment.schema``. A field named ``date`` annotated with the
``date`` imported from ``datetime`` made the whole module un-importable under
pydantic 2.13, taking every arg model in it out of reach at runtime, and no
test noticed. This file is that missing guard.
"""

from __future__ import annotations

import importlib
import importlib.util
import pkgutil

import fmp_data

# Subpackages gated behind optional extras, mapped to the third-party modules
# that extra installs. When the extra is absent these raise ImportError (or
# SystemExit, in fmp_data.mcp's case) by design, and that is not a defect.
#
# The exemption is keyed on whether the extra is actually *installed*, never on
# the module name alone. CI runs a langchain session and an mcp-server session
# with those extras present (.github/workflows/ci.yml, noxfile.py FEATURE_GROUPS),
# and a name-only exemption would let a genuine ImportError sail straight
# through the very jobs meant to catch it.
_EXTRA_PROBES: dict[str, tuple[str, ...]] = {
    "fmp_data.lc": ("langchain_core", "faiss"),
    "fmp_data.mcp": ("mcp",),
}

# The modules that genuinely cannot import without their extra. Anything else
# claiming the exemption is new, and is treated as a break until someone says
# otherwise -- this is what stops the exemption growing silently and quietly
# un-guarding the subpackage.
_EXPECTED_TO_NEED_EXTRA = {
    "fmp_data.lc.config",
    "fmp_data.lc.embedding",
    "fmp_data.lc.vector_store",
    "fmp_data.mcp.__main__",
}

# The walk yields 126 modules today. A floor near that catches a whole subtree
# dropping out; a floor far below it (the original 50) would not have.
_MIN_MODULES = 120


def _is_installed(probe: str) -> bool:
    """True when ``probe`` can be located. A raising finder counts as absent."""
    try:
        return importlib.util.find_spec(probe) is not None
    except (ImportError, ValueError):
        return False


def _missing_extra(module_name: str) -> bool:
    """True when ``module_name`` belongs to an extra that is not installed."""
    for prefix, probes in _EXTRA_PROBES.items():
        if module_name == prefix or module_name.startswith(f"{prefix}."):
            return not all(_is_installed(p) for p in probes)
    return False


def test_every_module_imports() -> None:
    """No module may fail to import for a reason other than a missing extra.

    Guards the #139 class of bug: a module that is syntactically fine but
    explodes at class-construction time, so it is only ever caught by code
    that actually imports it.
    """
    broken: list[str] = []
    exempted: set[str] = set()
    walk_errors: list[str] = []
    checked = 0

    # Without onerror, walk_packages swallows a failure to import a *package*
    # and silently skips its entire subtree -- breaking fmp_data/lc/__init__.py
    # drops 10 modules from the walk without a word.
    for module_info in pkgutil.walk_packages(
        fmp_data.__path__, prefix="fmp_data.", onerror=walk_errors.append
    ):
        checked += 1
        try:
            importlib.import_module(module_info.name)
        except (ImportError, SystemExit) as exc:
            # A missing optional dependency is the documented behaviour for
            # these subpackages; anywhere else it is a genuine break.
            if _missing_extra(module_info.name):
                exempted.add(module_info.name)
            else:
                broken.append(f"{module_info.name}: {exc!r}")
        except Exception as exc:
            # Broad on purpose. #139 raised PydanticUserError, not ImportError,
            # which is exactly why an ImportError-only guard would have missed
            # it. Nothing is swallowed.
            broken.append(f"{module_info.name}: {exc!r}")

    assert not broken, f"modules that fail to import: {broken}"
    assert not walk_errors, f"walk_packages could not recurse into: {walk_errors}"
    # Without a floor this passes vacuously if walk_packages stops yielding.
    assert checked >= _MIN_MODULES, (
        f"only walked {checked} modules, expected >= {_MIN_MODULES} "
        "-- did a package fail to import and take its subtree with it?"
    )
    unexpected_exemptions = exempted - _EXPECTED_TO_NEED_EXTRA
    assert not unexpected_exemptions, (
        "modules newly relying on the optional-extra exemption: "
        f"{sorted(unexpected_exemptions)}. If that is intended, add them to "
        "_EXPECTED_TO_NEED_EXTRA; otherwise they should import without the extra."
    )
