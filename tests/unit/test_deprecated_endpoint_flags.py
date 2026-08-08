"""Guard: which endpoints carry ``EndpointSemantics.deprecated`` (#137).

Three intelligence endpoints return ``[]`` without calling upstream, so they are
marked deprecated and filtered out of the LangChain vector store. The flag has
teeth -- setting it removes an endpoint from everything an LLM can select -- so
the *set* of flagged endpoints is pinned here, in both directions: the three are
marked, and nothing else is.

Deliberately placed outside ``tests/unit/lc/`` -- that package's ``conftest``
skips the whole directory without the ``langchain`` extra, and these assertions
need no extra beyond pydantic. CI runs the default matrix with no extras, so a
guard that lives in ``tests/unit/lc/`` is invisible to it. The store-filtering
behaviour, which genuinely needs langchain, stays in
``tests/unit/lc/test_deprecated_endpoints.py``; the MCP-side half of the
contract lives in ``tests/unit/test_mcp.py``, the only file the ``mcp-server``
CI job runs.
"""

from __future__ import annotations

import importlib
import pkgutil

import fmp_data
from fmp_data.intelligence.mapping import INTELLIGENCE_ENDPOINTS_SEMANTICS
from fmp_data.lc.models import EndpointSemantics

#: The endpoints #137 names. Spelled out rather than derived, so silently
#: un-marking one fails here instead of shrinking a computed set to nothing.
DEPRECATED_INTELLIGENCE_ENDPOINTS = {
    "stock_news_sentiments",
    "earnings_confirmed",
    "earnings_surprises",
}

#: Floor for the catalog scan below; the real count is ~520.
MIN_SEMANTICS_SCANNED = 150


def test_deprecated_defaults_to_false() -> None:
    """Existing semantics keep their meaning without touching every entry."""
    assert EndpointSemantics.model_fields["deprecated"].default is False


def test_the_three_intelligence_endpoints_are_marked() -> None:
    marked = {
        name
        for name, semantics in INTELLIGENCE_ENDPOINTS_SEMANTICS.items()
        if semantics.deprecated
    }
    assert marked == DEPRECATED_INTELLIGENCE_ENDPOINTS


def test_marked_endpoints_are_not_deleted() -> None:
    """#137 is explicit: keep the entries so tool keys stay resolvable."""
    for name in DEPRECATED_INTELLIGENCE_ENDPOINTS:
        assert name in INTELLIGENCE_ENDPOINTS_SEMANTICS


def test_nothing_else_is_marked_deprecated_by_accident() -> None:
    """A floor on the other side: the flag is off for the rest of the catalog.

    Scans every semantics table, not just intelligence -- otherwise another
    domain could acquire ``deprecated=True`` and silently vanish from the
    vector store with nothing to catch it.
    """
    flagged: set[str] = set()
    checked = 0
    for module_info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
        if not module_info.name.endswith(".mapping"):
            continue
        module = importlib.import_module(module_info.name)
        for attr, value in vars(module).items():
            if not (attr.endswith("_SEMANTICS") and isinstance(value, dict)):
                continue
            for key, semantics in value.items():
                if not isinstance(semantics, EndpointSemantics):
                    continue
                checked += 1
                if semantics.deprecated:
                    flagged.add(key)

    assert flagged == DEPRECATED_INTELLIGENCE_ENDPOINTS, (
        "the set of deprecated endpoints changed. Deprecating one is fine, "
        "but it removes the endpoint from the LangChain vector store, so it "
        f"must be deliberate. Expected {sorted(DEPRECATED_INTELLIGENCE_ENDPOINTS)}, "
        f"found {sorted(flagged)}"
    )
    # Without a floor an empty scan reads as a pass.
    assert checked > MIN_SEMANTICS_SCANNED, (
        f"only {checked} semantics scanned; is the walk working?"
    )
