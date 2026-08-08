from fmp_data.lc.models import ParameterHint

LIMIT_HINT = ParameterHint(
    natural_names=["limit", "max results", "number of results"],
    extraction_patterns=[
        r"(?:limit|show|get|return)\s+(\d+)",
        r"top\s+(\d+)",
        r"first\s+(\d+)",
    ],
    examples=["10", "25", "50"],
    context_clues=["limit", "maximum", "top", "first", "up to"],
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

PERIOD_HINT = ParameterHint(
    natural_names=["period", "timeframe", "frequency"],
    extraction_patterns=[
        r"\b(annual|quarterly)\b",
        r"(?:by|per)\s+(year|quarter)",
    ],
    examples=["annual", "quarter"],
    context_clues=["annual", "quarterly", "year", "quarter"],
)
SYMBOL_HINT = ParameterHint(
    natural_names=["ticker", "symbol", "stock", "company"],
    extraction_patterns=[
        r"\b[A-Z]{1,5}\b",
        r"(?:for|of)\s+([A-Z]{1,5})",
        r"([A-Z]{1,5})(?:'s|')",
        r"(?i)for\s+([A-Z]{1,5})",
        r"(?i)([A-Z]{1,5})(?:'s|'|\s+)",
        r"\b[A-Z]{1,5}\b",
    ],
    examples=["AAPL", "MSFT", "GOOG", "TSLA", "AMZN"],
    context_clues=["for", "about", "'s", "of", "company", "stock"],
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

CIK_HINT = ParameterHint(
    natural_names=["CIK", "central index key", "SEC identifier"],
    extraction_patterns=[
        r"\b\d{10}\b",
        r"\b0{6}\d{4}\b",
        r"CIK\s*:?\s*(\d{10})",
    ],
    examples=["0000320193", "0001318605", "0001045810"],
    context_clues=["CIK", "central index key", "SEC identifier", "CIK number"],
)

PAGE_HINT = ParameterHint(
    natural_names=["page", "page number", "offset"],
    extraction_patterns=[
        r"page\s+(\d+)",
        r"(?:second|third|next)\s+page",
    ],
    examples=["0", "1", "2"],
    context_clues=["page", "pagination", "offset", "next page"],
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

YEAR_HINT = ParameterHint(
    natural_names=["year", "filing year", "reporting year"],
    extraction_patterns=[
        r"\b(19|20)\d{2}\b",
        r"(?:in|for|during)\s+((?:19|20)\d{2})",
    ],
    examples=["2023", "2024"],
    context_clues=["year", "annual", "fiscal year", "in"],
)

QUARTER_HINT = ParameterHint(
    natural_names=["quarter", "fiscal quarter", "reporting quarter"],
    extraction_patterns=[
        r"(?i)\bQ([1-4])\b",
        r"(?i)(first|second|third|fourth)\s+quarter",
    ],
    examples=["1", "2", "3", "4"],
    context_clues=["quarter", "Q1", "Q2", "Q3", "Q4", "quarterly"],
)

# A single as-of day, not one end of a range. DATE_HINTS below covers ranges;
# reaching for its "start_date" entry here would tell the model the parameter
# means "from", which is exactly wrong for a one-day snapshot.
DATE_HINT = ParameterHint(
    natural_names=["date", "as-of date", "trading day"],
    extraction_patterns=[
        r"(\d{4}-\d{2}-\d{2})",
        r"(?:on|for)\s+(\d{4}-\d{2}-\d{2})",
    ],
    examples=["2024-01-02", "2023-12-29"],
    context_clues=["on", "for", "date", "day", "as of"],
)

DATE_HINTS = {
    "start_date": ParameterHint(
        natural_names=["start date", "from date", "beginning", "since"],
        extraction_patterns=[
            r"(\d{4}-\d{2}-\d{2})",
            r"(?:from|since|after)\s+(\d{4}-\d{2}-\d{2})",
        ],
        examples=["2023-01-01", "2022-12-31"],
        context_clues=["from", "since", "starting", "beginning", "after"],
    ),
    "end_date": ParameterHint(  # Changed from "to_date"
        natural_names=["end date", "to date", "until", "through"],
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
