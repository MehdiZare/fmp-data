"""No class attribute may shadow a name the module imports from ``datetime``.

#139 was a field whose *name* collided with the type imported for its
*annotation*::

    from datetime import date

    class ETFHoldingsArgs(SymbolArg):
        date: date = Field(...)   # PydanticUserError, module un-importable

The failure is total -- the whole module, not the one field -- and the error
message blames "a field name clashing with a type annotation" rather than the
edit that caused it.

#142 found 23 more attributes named ``date`` in modules doing
``from datetime import date``. None were broken, because each was annotated
``datetime`` or ``str`` -- a *different* name, which pydantic resolves fine.
Every one was a landmine: narrowing any of them to the semantically-correct
``date`` reproduces #139 instantly.

``test_imports.py`` catches the explosion after someone steps on it. This guard
removes the landmine, by rejecting the *shadowing* itself rather than the
subset of it that happens to be fatal today. The fix is always the aliased
import already used across the package::

    from datetime import date as dt_date
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from pathlib import Path

import fmp_data

_PACKAGE_ROOT = Path(fmp_data.__file__).resolve().parent

# Floors, so the scan cannot pass by finding nothing. A path typo, a rename of
# the package directory or an AST-shape change would otherwise turn this file
# into a test that asserts an empty list is empty.
#
# The walk yields 127 modules and 3138 class attributes today. The floors sit
# close enough underneath to catch a whole subtree or an entire AST node type
# dropping out of the scan, and far enough to survive ordinary churn.
_MIN_MODULES = 120
_MIN_CLASS_ATTRIBUTES = 2500


def _datetime_bound_names(tree: ast.Module) -> set[str]:
    """Names bound in this module's namespace by importing ``datetime``.

    The binding is what matters, not the original symbol: after
    ``from datetime import date as dt_date`` the name ``date`` is free again,
    which is precisely why aliasing is the fix.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "datetime":
            names.update(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "datetime" or alias.name.startswith("datetime."):
                    # ``import datetime.foo`` binds the top-level ``datetime``.
                    names.add(alias.asname or alias.name.split(".")[0])
    return names


def _class_attributes(node: ast.ClassDef) -> Iterator[tuple[str, int]]:
    """Attribute names assigned directly in a class body, with line numbers.

    Direct body only: an ``ast.walk`` would also sweep up locals inside
    methods, which shadow nothing at class-construction time. Nested classes
    are still covered -- the caller walks every ``ClassDef`` in the module.
    """
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            yield stmt.target.id, stmt.lineno
        elif isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    yield target.id, stmt.lineno


def test_no_class_attribute_shadows_a_datetime_import() -> None:
    """Reject the #139 shape everywhere, not just where it is already fatal."""
    offenders: list[str] = []
    modules_scanned = 0
    attributes_scanned = 0

    for path in sorted(_PACKAGE_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        modules_scanned += 1

        shadowable = _datetime_bound_names(tree)
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

        for class_node in classes:
            for attr_name, lineno in _class_attributes(class_node):
                attributes_scanned += 1
                if attr_name in shadowable:
                    rel = path.relative_to(_PACKAGE_ROOT.parent)
                    offenders.append(
                        f"{rel}:{lineno} {class_node.name}.{attr_name} "
                        f"shadows the `{attr_name}` imported from datetime"
                    )

    assert not offenders, (
        "class attributes shadowing a name imported from datetime "
        f"({len(offenders)}):\n  " + "\n  ".join(offenders) + "\n"
        "Alias the import instead, e.g. `from datetime import date as dt_date`."
    )
    # Without these the assertion above passes vacuously on an empty scan.
    assert modules_scanned >= _MIN_MODULES, (
        f"only scanned {modules_scanned} modules, expected >= {_MIN_MODULES} "
        f"-- is {_PACKAGE_ROOT} still the package root?"
    )
    assert attributes_scanned >= _MIN_CLASS_ATTRIBUTES, (
        f"only scanned {attributes_scanned} class attributes, expected "
        f">= {_MIN_CLASS_ATTRIBUTES} -- did the AST shapes being walked change?"
    )
