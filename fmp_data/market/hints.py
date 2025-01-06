from fmp_data.lc.models import ParameterHint

COMPANY_SEARCH_HINT = ParameterHint(
    natural_names=["search term", "query", "keyword"],
    extraction_patterns=[
        r"(?:search|find|look up)\s+(.+?)(?:\s+in|\s+on|\s*$)",
        r"(?:about|related to)\s+(.+?)(?:\s+in|\s+on|\s*$)",
    ],
    examples=["tech companies", "renewable energy", "artificial intelligence"],
    context_clues=["search", "find", "look up", "about", "related to"],
)

IDENTIFIER_HINT = ParameterHint(
    natural_names=["identifier", "ID", "number"],
    extraction_patterns=[
        r"\b\d{6,10}\b",  # CIK numbers
        r"\b[0-9A-Z]{9}\b",  # CUSIP
        r"\b[A-Z]{2}[A-Z0-9]{9}\d\b",  # ISIN
    ],
    examples=["320193", "037833100", "US0378331005"],
    context_clues=["number", "identifier", "ID", "code"],
)
