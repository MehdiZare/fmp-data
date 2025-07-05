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
