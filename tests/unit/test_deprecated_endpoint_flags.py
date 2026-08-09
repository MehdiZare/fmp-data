"""Guard: which endpoints carry ``EndpointSemantics.deprecated`` (#137).

Endpoints that return ``[]`` without calling upstream are marked deprecated and
filtered out of the LangChain vector store. The flag has teeth -- setting it
removes an endpoint from everything an LLM can select -- so the *set* of flagged
endpoints is pinned here, in both directions: the expected ones are marked, and
nothing else is.

The expected set has two halves, and the second is deliberately **derived from
`WITHDRAWN_TOOLS`** rather than spelled out. That is not the same shortcut the
note below warns against: `WITHDRAWN_TOOLS` is the MCP layer's own list, an
independent source, so comparing against it asserts that the two retirement
surfaces agree. They did not. The MCP side was taught to drop withdrawn tools
while the LangChain side still indexed all 19, leaving a semantic query free to
select an endpoint that can only answer empty -- the exact failure #137 exists
to prevent. Deriving here means the next withdrawal cannot fix one surface and
forget the other.

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
from fmp_data.mcp.tools_manifest import WITHDRAWN_TOOLS

#: The endpoints #137 names. Spelled out rather than derived, so silently
#: un-marking one fails here instead of shrinking a computed set to nothing.
DEPRECATED_INTELLIGENCE_ENDPOINTS = {
    "stock_news_sentiments",
    "earnings_confirmed",
    "earnings_surprises",
}

#: Endpoints FMP withdrew: the path 404s and the client method returns empty
#: without a request. Derived from the MCP layer's list on purpose -- see the
#: module docstring. ``WITHDRAWN_TOOLS`` is keyed ``"<client>.<key>"``.
WITHDRAWN_ENDPOINT_KEYS = {spec.split(".", 1)[1] for spec in WITHDRAWN_TOOLS}

#: Every endpoint that must be kept out of the vector store, for either reason.
EXPECTED_DEPRECATED = DEPRECATED_INTELLIGENCE_ENDPOINTS | WITHDRAWN_ENDPOINT_KEYS

#: Floor for the catalog scan below; the real count is ~520.
MIN_SEMANTICS_SCANNED = 150


def test_deprecated_defaults_to_false() -> None:
    """Existing semantics keep their meaning without touching every entry."""
    assert EndpointSemantics.model_fields["deprecated"].default is False


def test_the_intelligence_endpoints_are_marked() -> None:
    """The #137 three, plus any intelligence endpoint since withdrawn."""
    marked = {
        name
        for name, semantics in INTELLIGENCE_ENDPOINTS_SEMANTICS.items()
        if semantics.deprecated
    }
    expected = DEPRECATED_INTELLIGENCE_ENDPOINTS | (
        WITHDRAWN_ENDPOINT_KEYS & set(INTELLIGENCE_ENDPOINTS_SEMANTICS)
    )
    assert marked == expected


def test_every_withdrawn_tool_is_flagged_in_its_semantics() -> None:
    """The cross-surface check: MCP withdrawal implies LangChain exclusion.

    Without this, a withdrawal can be applied to the MCP catalog while the
    vector store keeps offering the same dead endpoint to an LLM, which then
    calls it and receives an empty *success* indistinguishable from "no data
    matched".
    """
    by_key: dict[str, EndpointSemantics] = {}
    for module_info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
        if not module_info.name.endswith(".mapping"):
            continue
        module = importlib.import_module(module_info.name)
        for attr, value in vars(module).items():
            if not (attr.endswith("_SEMANTICS") and isinstance(value, dict)):
                continue
            for key, semantics in value.items():
                if isinstance(semantics, EndpointSemantics):
                    by_key.setdefault(key, semantics)

    unflagged = sorted(
        key
        for key in WITHDRAWN_ENDPOINT_KEYS
        if key in by_key and not by_key[key].deprecated
    )
    assert not unflagged, (
        "these endpoints are withdrawn in WITHDRAWN_TOOLS but still carry "
        "deprecated=False, so the LangChain vector store will index and offer "
        f"them: {unflagged}"
    )
    assert WITHDRAWN_ENDPOINT_KEYS, "WITHDRAWN_TOOLS is empty; guard is vacuous"


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

    assert flagged == EXPECTED_DEPRECATED, (
        "the set of deprecated endpoints changed. Deprecating one is fine, "
        "but it removes the endpoint from the LangChain vector store, so it "
        f"must be deliberate. Expected {sorted(EXPECTED_DEPRECATED)}, "
        f"found {sorted(flagged)}"
    )
    # Without a floor an empty scan reads as a pass.
    assert checked > MIN_SEMANTICS_SCANNED, (
        f"only {checked} semantics scanned; is the walk working?"
    )
