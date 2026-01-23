# fmp_data/transcripts/mapping.py
from __future__ import annotations

from fmp_data.lc.hints import SYMBOL_HINT
from fmp_data.lc.models import EndpointSemantics, SemanticCategory
from fmp_data.transcripts.endpoints import (
    EARNINGS_TRANSCRIPT,
    LATEST_TRANSCRIPTS,
    TRANSCRIPT_DATES,
    TRANSCRIPT_SYMBOLS,
)

# Transcripts endpoints mapping
TRANSCRIPTS_ENDPOINT_MAP = {
    "get_latest": LATEST_TRANSCRIPTS,
    "get_transcript": EARNINGS_TRANSCRIPT,
    "get_available_dates": TRANSCRIPT_DATES,
    "get_available_symbols": TRANSCRIPT_SYMBOLS,
}

# Complete semantic definitions for all endpoints
TRANSCRIPTS_ENDPOINTS_SEMANTICS = {
    "latest_transcripts": EndpointSemantics(
        client_name="transcripts",
        method_name="get_latest",
        natural_description=(
            "Get the most recent earnings call transcripts across all companies. "
            "Returns latest conference call transcripts with full text content."
        ),
        example_queries=[
            "Get latest earnings call transcripts",
            "Show me recent company earnings calls",
            "What are the newest earnings transcripts?",
            "Latest conference call transcripts",
            "Recent earnings call releases",
        ],
        related_terms=[
            "earnings call",
            "conference call",
            "earnings transcript",
            "earnings call text",
            "latest transcripts",
            "recent earnings",
        ],
        category=SemanticCategory.INTELLIGENCE,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "transcript": EndpointSemantics(
        client_name="transcripts",
        method_name="get_transcript",
        natural_description=(
            "Get earnings call transcript for a specific company and quarter. "
            "Returns full text of earnings conference call for specified fiscal period."
        ),
        example_queries=[
            "Get AAPL Q4 2024 earnings transcript",
            "Show me Apple's Q1 earnings call text",
            "Get Tesla Q3 2023 earnings transcript",
            "Microsoft quarterly earnings call transcript",
            "What did the CEO say in NVDA earnings call?",
        ],
        related_terms=[
            "earnings call",
            "conference call",
            "quarterly results",
            "earnings transcript",
            "call transcript",
            "earnings text",
        ],
        category=SemanticCategory.INTELLIGENCE,
        parameter_hints={},
        response_hints={},
        use_cases=["Market data analysis", "Financial research"],
    ),
    "transcript_dates": EndpointSemantics(
        client_name="transcripts",
        method_name="get_available_dates",
        natural_description=(
            "Get available transcript dates for a specific company. "
            "Returns list of dates when earnings call transcripts are available."
        ),
        example_queries=[
            "Get available transcript dates for AAPL",
            "When are MSFT earnings transcripts available?",
            "List Tesla earnings call dates",
            "Show me available earnings transcript dates",
            "What quarters have transcripts for Apple?",
        ],
        related_terms=[
            "transcript dates",
            "available transcripts",
            "earnings call dates",
            "transcript schedule",
            "transcript availability",
        ],
        category=SemanticCategory.INTELLIGENCE,
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={},
        use_cases=["Financial analysis", "Investment research"],
    ),
    "transcript_symbols": EndpointSemantics(
        client_name="transcripts",
        method_name="get_available_symbols",
        natural_description=(
            "Get list of all symbols with available earnings transcripts. "
            "Returns companies that have earnings call transcripts available."
        ),
        example_queries=[
            "Get symbols with earnings transcripts",
            "Which companies have earnings call transcripts?",
            "List companies with available transcripts",
            "Show me all transcript symbols",
            "Companies with conference call transcripts",
        ],
        related_terms=[
            "transcript symbols",
            "available companies",
            "transcript coverage",
            "companies with transcripts",
            "transcript list",
        ],
        category=SemanticCategory.INTELLIGENCE,
        parameter_hints={},
        response_hints={},
        use_cases=["Financial analysis", "Investment research"],
    ),
}
