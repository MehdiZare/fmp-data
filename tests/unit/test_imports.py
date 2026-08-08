"""Every module in the package must import.

#139 sat undetected because nothing in the suite imported
``fmp_data.investment.schema``. A field named ``date`` annotated with the
``date`` imported from ``datetime`` made the whole module un-importable under
pydantic 2.13, taking every arg model in it out of reach at runtime, and no
test noticed. This file is that missing guard.
"""

from __future__ import annotations

import importlib
import pkgutil

import fmp_data

# Subpackages gated behind optional extras. When the extra is absent these
# raise ImportError (or SystemExit, in fmp_data.mcp's case) by design, and
# that is not a defect. Any OTHER failure from them, and any failure at all
# from a module outside this set, is a real break.
_OPTIONAL_EXTRA_PREFIXES = ("fmp_data.lc", "fmp_data.mcp")


def _is_optional_extra(module_name: str) -> bool:
    return module_name.startswith(_OPTIONAL_EXTRA_PREFIXES)


def test_every_module_imports() -> None:
    """No module may fail to import for a reason other than a missing extra.

    Guards the #139 class of bug: a module that is syntactically fine but
    explodes at class-construction time, so it is only ever caught by code
    that actually imports it.
    """
    broken: list[str] = []
    checked = 0

    for module_info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
        checked += 1
        try:
            importlib.import_module(module_info.name)
        except (ImportError, SystemExit) as exc:
            # A missing optional dependency is the documented behaviour for
            # these subpackages; anywhere else it is a genuine break.
            if not _is_optional_extra(module_info.name):
                broken.append(f"{module_info.name}: {exc!r}")
        except Exception as exc:
            # Broad on purpose. #139 raised PydanticUserError, not ImportError,
            # which is exactly why an ImportError-only guard would have missed
            # it. Nothing is swallowed.
            broken.append(f"{module_info.name}: {exc!r}")

    assert not broken, f"modules that fail to import: {broken}"
    # Without a floor this passes vacuously if walk_packages stops yielding.
    assert checked > 50, f"only walked {checked} modules — is the walk working?"
