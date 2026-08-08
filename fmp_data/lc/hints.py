"""Shared ``ParameterHint`` definitions (#135).

One definition per concept, imported by the domain mapping modules. Before
this consolidation ten names were bound in several modules at once with
divergent contents, so the same user phrasing resolved on one tool and not
another with nothing comparing them. ``tests/unit/test_hint_consolidation.py``
fails if a name ever gains a second, different definition.

Where two module-local copies genuinely disagreed, the union was taken; where
the union would have produced *wrong* extraction rather than merely a longer
list, the resolution is recorded in a comment on the hint itself.

Note on reach: ``examples`` and ``context_clues`` are rendered into each
generated tool's parameter description (``ToolFactory.generate_description``),
and ``natural_names``/``context_clues``/``examples`` are rendered into the
embedding text an endpoint is indexed under (``EndpointRegistry.
get_embedding_text``). ``extraction_patterns`` is documentation only -- nothing
compiles or applies it today -- so pattern edits below change what a reader and
a reviewer see, not what a query resolves to.
"""

from fmp_data.lc.models import ParameterHint

# Union of the former lc, intelligence and fundamental copies. The three
# disagreed only on which phrasings they listed, so every pattern is kept.
LIMIT_HINT = ParameterHint(
    natural_names=[
        "limit",
        "max results",
        "number of results",
        "count",
        "number",
    ],
    extraction_patterns=[
        r"(?:limit|show|get|return)\s+(\d+)",
        r"top\s+(\d+)",
        r"first\s+(\d+)",
        r"(?i)limit\s*(\d+)",
        r"(?i)(\d+)\s*results",
        r"(?i)last\s+(\d+)",
        r"(?i)recent\s+(\d+)",
        r"(?i)(\d+)\s+periods",
    ],
    examples=["10", "20", "25", "40", "50", "100", "200"],
    context_clues=[
        "limit",
        "maximum",
        "top",
        "first",
        "up to",
        "results",
        "entries",
        "last",
        "recent",
        "previous",
        "historical",
        "periods",
        "statements",
        "reports",
    ],
)

EXCHANGE_HINT = ParameterHint(
    natural_names=["exchange", "market", "trading venue"],
    extraction_patterns=[
        r"\b(NYSE|NASDAQ|LSE|TSX|ASX)\b",
        r"(?:on|at)\s+(the\s+)?([A-Z]{2,6})",
    ],
    examples=["NYSE", "NASDAQ", "LSE", "TSX"],
    context_clues=["on", "listed on", "trading on", "exchange", "market"],
)

# Reporting frequency -- the ``period`` query parameter.
#
# CONFLICT (recorded): the catalog enforces THREE different ``valid_values``
# sets under this one parameter name, so this concept is three hints, not one.
# ``examples`` are rendered verbatim into the tool description by
# ``ToolFactory.generate_description``, while ``EndpointParam.validate_value``
# rejects anything outside ``valid_values`` -- so a union would advertise
# values the endpoint refuses, which is the same failure QUARTER_HINT avoids
# below. ``test_hint_examples_are_within_valid_values`` pins every hint's
# examples against the valid_values of every parameter it is bound to.
#
#   PERIOD_HINT              annual | quarter                (company, 3)
#   PERIOD_WITH_FISCAL_HINT  annual | quarter | FY | Q1..Q4  (fundamental, 7)
#   FISCAL_PERIOD_HINT       FY | Q1..Q4                     (bulk, 6)
#
# CONFLICT (recorded): technical/mapping.py also bound the name PERIOD_HINT,
# but for its ``periodLength`` parameter, which is an indicator lookback in
# bars (14, 20, 50, 200). Unioning the two would advertise "annual" as a valid
# RSI window and "50" as a valid statement period. They are two concepts, not
# one; the lookback lives below as PERIOD_LENGTH_HINT.
PERIOD_HINT = ParameterHint(
    natural_names=["period", "timeframe", "frequency"],
    extraction_patterns=[
        r"\b(annual|quarterly)\b",
        r"(?:by|per)\s+(year|quarter)",
        r"(?i)every\s+(year|quarter)",
    ],
    examples=["annual", "quarter"],
    context_clues=[
        "annual",
        "quarterly",
        "year",
        "quarter",
        "yearly",
        "period",
        "reporting",
        "financial",
    ],
)

# ``period`` where the endpoint also accepts fiscal labels. Union of the former
# lc and fundamental copies -- valid only where valid_values carries FY/Q1..Q4
# alongside annual/quarter, which today is every fundamental statement endpoint.
PERIOD_WITH_FISCAL_HINT = ParameterHint(
    natural_names=["period", "timeframe", "frequency", "interval"],
    extraction_patterns=[
        r"\b(annual|quarterly)\b",
        r"(?:by|per)\s+(year|quarter)",
        r"(?i)(annual|yearly|quarterly|quarter|fy|q1|q2|q3|q4)",
        r"(?i)every\s+(year|quarter)",
    ],
    examples=["annual", "quarter", "FY", "Q1"],
    context_clues=[
        "annual",
        "quarterly",
        "year",
        "quarter",
        "yearly",
        "q1",
        "q2",
        "q3",
        "q4",
        "fy",
        "fiscal",
        "period",
        "reporting",
        "financial",
    ],
)

# ``period`` on the bulk endpoints, which accept fiscal labels ONLY -- there is
# no "annual"/"quarter" in their valid_values. Advertising those (as the shared
# hint did before the split) invited a client-side ValidationError on all six.
FISCAL_PERIOD_HINT = ParameterHint(
    natural_names=["period", "fiscal period", "quarter", "fiscal quarter"],
    extraction_patterns=[
        r"(?i)\b(fy|q1|q2|q3|q4)\b",
        r"(?i)(?:fiscal\s+)?(?:year|quarter)\s+(fy|q[1-4])",
    ],
    examples=["FY", "Q1", "Q2", "Q3", "Q4"],
    context_clues=[
        "fiscal",
        "fy",
        "q1",
        "q2",
        "q3",
        "q4",
        "quarter",
        "period",
        "reporting",
        "financial",
    ],
)

# Indicator lookback length in bars -- the ``periodLength`` parameter on
# technical indicators. See the CONFLICT note on PERIOD_HINT above; these must
# not be merged.
PERIOD_LENGTH_HINT = ParameterHint(
    natural_names=["period", "period length", "lookback"],
    extraction_patterns=[
        r"(\d+)[-\s]?(?:day|period)",
        r"(?:period|lookback)\s+of\s+(\d+)",
    ],
    examples=["14", "20", "50", "200"],
    context_clues=["period", "days", "lookback", "window"],
)

# Union of the former lc, investment, intelligence, institutional, fundamental
# and technical copies.
#
# CONFLICT (recorded): institutional/mapping.py carried an unanchored
# ``[A-Z]{1,5}`` which matches inside a longer token ("NASDAQ" -> "NASDA").
# The anchored ``\b[A-Z]{1,5}\b`` already present is deliberately narrower --
# it matches strictly less, which is the point -- so the unanchored form is
# dropped rather than unioned in. Its case-sensitive
# ``symbol[:\s]+([A-Z]{1,5})`` is a different case: that one really is subsumed
# by intelligence's ``(?i)`` form, which matches everything it does.
SYMBOL_HINT = ParameterHint(
    natural_names=[
        "ticker",
        "symbol",
        "stock",
        "company",
        "code",
        # From institutional's copy. natural_names feed get_embedding_text,
        # so dropping these would shift the embedding for 18 endpoints.
        "company symbol",
        "stock symbol",
    ],
    extraction_patterns=[
        r"\b[A-Z]{1,5}\b",
        r"(?:for|of)\s+([A-Z]{1,5})",
        r"([A-Z]{1,5})(?:'s|')",
        r"(?i)for\s+([A-Z]{1,5})",
        r"(?i)([A-Z]{1,5})(?:'s|'|\s+)",
        r"(?i)symbol[:\s]+([A-Z]{1,5})",
    ],
    examples=[
        "AAPL",
        "MSFT",
        "GOOG",
        "GOOGL",
        "TSLA",
        "AMZN",
        "META",
        "SPY",
        "QQQ",
        "VTI",
        "VFIAX",
    ],
    context_clues=[
        "for",
        "about",
        "'s",
        "of",
        "company",
        "stock",
        "ticker",
        "symbol",
        "shares",
        "corporation",
        "business",
        "enterprise",
        "firm",
        "etf",
        "fund",
    ],
)

# Plural of SYMBOL_HINT: endpoints that take a comma-separated ticker list in
# one parameter rather than one ticker per call.
SYMBOLS_HINT = ParameterHint(
    natural_names=["symbols", "tickers", "symbol list", "watchlist"],
    extraction_patterns=[
        r"\b[A-Z]{1,5}(?:\s*,\s*[A-Z]{1,5})+\b",
        r"(?:for|of)\s+([A-Z]{1,5}(?:\s*,\s*[A-Z]{1,5})+)",
    ],
    examples=["AAPL,MSFT", "AAPL,MSFT,GOOGL", "TSLA,AMZN,NVDA"],
    context_clues=["symbols", "tickers", "multiple", "batch", "list", "these"],
)

# Union of the former lc, company, institutional and investment copies.
#
# CONFLICT (recorded): institutional/mapping.py carried a bare ``(\d{10})``,
# unanchored, which takes the first ten digits out of a longer run and yields a
# truncated CIK. The anchored ``\b\d{10}\b`` is deliberately narrower -- it
# declines the eleven-digit run rather than truncating it -- so the bare form is
# dropped rather than unioned in.
# Its ``CIK[:\s]+(\d+)`` was likewise unbounded; merged with investment's
# ``(?i)cik[:\s]+(\d{1,10})`` into one case-insensitive, length-bounded form,
# since a CIK is at most ten digits.
CIK_HINT = ParameterHint(
    natural_names=[
        "CIK",
        "central index key",
        "SEC identifier",
        "SEC ID",
        # company/hints.py listed these as natural_names, not context_clues.
        # Both fields feed get_embedding_text, but they are not
        # interchangeable, so the union keeps them in both.
        "filing ID",
        "company id",
    ],
    extraction_patterns=[
        r"\b\d{10}\b",
        r"\b0{6}\d{4}\b",
        r"(?i)CIK\s*:?\s*(\d{1,10})",
    ],
    examples=[
        "0000320193",
        "0001318605",
        "0001045810",
        "0000102909",
        # Unioned back in from the company/investment copies: examples feed
        # ToolFactory.generate_description, so the tool text an LLM reads
        # changes if they are dropped.
        "0000789019",
        "0001652044",
        "0000884560",
    ],
    context_clues=[
        "CIK",
        "central index key",
        "SEC identifier",
        "CIK number",
        "filing ID",
        "regulatory ID",
        "company id",
    ],
)

# Union of the former lc, intelligence, institutional and fundamental copies.
#
# CONFLICT (recorded): institutional/mapping.py carried ``p(\d+)``, which
# matches inside any word ending in "p" followed by digits -- "sp500" would
# yield page 500. Narrowed to ``\bp(\d+)\b`` rather than dropped, so the
# shorthand it was reaching for ("p2") still resolves.
#
# The main pattern is anchored for the same reason: the union of the four
# copies (``page\s+``, ``page[:\s]+``, ``page\s*``) was widest at ``page[:\s]*``,
# which matches inside a longer token -- "webpage3" would yield page 3.
PAGE_HINT = ParameterHint(
    natural_names=["page", "page number", "offset", "result page"],
    extraction_patterns=[
        r"(?i)\bpage[:\s]*(\d+)",
        r"(?i)page\s+number\s+(\d+)",
        r"(?:second|third|next)\s+page",
        r"(\d+)(?:st|nd|rd|th)\s+page",
        r"\bp(\d+)\b",
    ],
    examples=["0", "1", "2"],
    context_clues=[
        "page",
        "pagination",
        "offset",
        "next page",
        "next",
        "previous",
        "results",
    ],
)

SECTOR_HINT = ParameterHint(
    natural_names=["sector", "market sector", "industry sector"],
    extraction_patterns=[
        r"(?i)\b(technology|healthcare|financials?|energy|utilities|"
        r"industrials|materials|real estate|consumer\s+\w+)\b",
        r"(?i)(?:in|for)\s+the\s+(\w+)\s+sector",
    ],
    examples=["Technology", "Healthcare", "Energy", "Financial Services"],
    context_clues=["sector", "industry group", "market segment"],
)

INDUSTRY_HINT = ParameterHint(
    natural_names=["industry", "business line", "sub-industry"],
    extraction_patterns=[
        r"(?i)(?:in|for)\s+the\s+([\w\s]+)\s+industry",
        r"(?i)\b(software|biotechnology|semiconductors|banks|insurance)\b",
    ],
    examples=["Software", "Biotechnology", "Semiconductors", "Banks"],
    context_clues=["industry", "business line", "vertical"],
)

# Union of the former lc and investment copies.
#
# CONFLICT (recorded): the lc pattern was ``\b(19|20)\d{2}\b`` -- the group
# captures the century, so an extractor applying it would read "20" out of
# "2024". Corrected to capture the whole year. investment's ``\b(20\d{2})\b``
# is then subsumed and dropped.
YEAR_HINT = ParameterHint(
    natural_names=["year", "filing year", "reporting year", "fiscal year"],
    extraction_patterns=[
        r"\b((?:19|20)\d{2})\b",
        r"(?:in|for|during)\s+((?:19|20)\d{2})",
    ],
    examples=["2023", "2024"],
    context_clues=["year", "annual", "fiscal year", "fiscal", "in"],
)

# Union of the former lc and investment copies.
#
# CONFLICT (recorded): investment listed ``["Q1", "Q4"]`` as the example
# values while lc listed ``["1", "2", "3", "4"]``. The wire parameter is
# declared ``ParamType.INTEGER`` (investment/endpoints.py, "Disclosure quarter
# (1-4)"), so "Q1" is not a sendable value -- ``examples`` is rendered straight
# into the tool's parameter description, so shipping it would invite a 400.
# The numeric examples win; investment's *pattern* is unioned in.
QUARTER_HINT = ParameterHint(
    natural_names=["quarter", "fiscal quarter", "reporting quarter", "q"],
    extraction_patterns=[
        r"(?i)\bQ([1-4])\b",
        r"(?i)(first|second|third|fourth)\s+quarter",
        r"(?i)\bquarter\s+([1-4])\b",
    ],
    examples=["1", "2", "3", "4"],
    context_clues=["quarter", "Q1", "Q2", "Q3", "Q4", "quarterly", "q"],
)

# Intraday bar size. Union of the former alternative and company copies.
#
# CONFLICT (recorded): company/hints.py wrote ``examples=list(
# IntradayTimeInterval)``. Importing ``fmp_data.company.schema`` here would
# make the shared hints module depend on a domain schema, so the values are
# spelled out; they are exactly the enum's, and
# ``test_interval_hint_examples_track_the_intraday_interval_enum`` fails if the
# enum gains a member this list lacks.
INTERVAL_HINT = ParameterHint(
    natural_names=["interval", "timeframe", "period"],
    extraction_patterns=[
        r"(?i)(\d+)\s*(?:min|minute|hour|hr)",
        r"(?i)(one|five|fifteen|thirty)\s*(?:min|minute|hour|hr)",
        r"(?:1min|5min|15min|30min|1hour|4hour)",
    ],
    examples=["1min", "5min", "15min", "30min", "1hour", "4hour"],
    context_clues=[
        "interval",
        "timeframe",
        "period",
        "frequency",
        "minute",
        "hour",
    ],
)

# A single as-of day, not one end of a range. DATE_HINTS below covers ranges;
# reaching for its "start_date" entry here would tell the model the parameter
# means "from", which is exactly wrong for a one-day snapshot.
#
# Named AS_OF_DATE_HINT rather than DATE_HINT so it cannot be mistaken at a
# glance for the DATE_HINTS range mapping defined just below -- one character
# apart, opposite meanings. The former investment and institutional
# ``DATE_HINT`` constants were the same one-day concept and fold in here; the
# name collision with DATE_HINTS is resolved by keeping only this name.
#
# CONFLICT (recorded): institutional/mapping.py carried
# ``(\d{2}/\d{2}/\d{4})``. Every FMP date parameter takes ISO ``YYYY-MM-DD``
# and every example on every date hint is ISO, so unioning a US-order pattern
# in would advertise an unsendable format across every as-of-date parameter in
# the catalog. Dropped.
AS_OF_DATE_HINT = ParameterHint(
    natural_names=[
        "date",
        "as-of date",
        "trading day",
        "as of",
        "portfolio date",
        "filing date",
        "report date",
    ],
    extraction_patterns=[
        r"(\d{4}-\d{2}-\d{2})",
        r"(?:on|at|for)\s+(\d{4}-\d{2}-\d{2})",
    ],
    examples=[
        "2024-01-02",
        "2023-12-29",
        "2024-03-31",
        "2023-12-31",
        # Unioned back in from the investment/institutional copies.
        "2024-01-15",
        "2024-06-30",
    ],
    context_clues=[
        "on",
        "for",
        "date",
        "day",
        "as of",
        "holdings",
        "portfolio",
        "filed on",
        "reported",
        "for period",
    ],
)

# Union of the former lc, alternative, economics and intelligence copies. Only
# intelligence's differed -- it added the bare "from"/"to" natural names and
# dropped "beginning" from the start-date context clues. No conflict; the union
# is a strict superset of all four.
DATE_HINTS = {
    "start_date": ParameterHint(
        natural_names=["start date", "from date", "beginning", "since", "from"],
        extraction_patterns=[
            r"(\d{4}-\d{2}-\d{2})",
            r"(?:from|since|after)\s+(\d{4}-\d{2}-\d{2})",
        ],
        examples=["2023-01-01", "2022-12-31"],
        context_clues=["from", "since", "starting", "beginning", "after"],
    ),
    "end_date": ParameterHint(  # Changed from "to_date"
        natural_names=["end date", "to date", "until", "through", "to"],
        extraction_patterns=[
            r"(?:to|until|through)\s+(\d{4}-\d{2}-\d{2})",
            r"(\d{4}-\d{2}-\d{2})",
        ],
        examples=["2024-01-01", "2023-12-31"],
        context_clues=["to", "until", "through", "ending"],
    ),
}

# Same date semantics for endpoints whose query params are named from/to
FROM_TO_DATE_HINTS = {
    "from": DATE_HINTS["start_date"],
    "to": DATE_HINTS["end_date"],
}
