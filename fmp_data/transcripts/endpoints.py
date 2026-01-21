# fmp_data/transcripts/endpoints.py
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    HTTPMethod,
    ParamLocation,
    ParamType,
    URLType,
)
from fmp_data.transcripts.models import (
    EarningsTranscript,
    TranscriptDate,
    TranscriptSymbol,
)

LATEST_TRANSCRIPTS: Endpoint = Endpoint(
    name="latest_transcripts",
    path="earning-call-transcript-latest",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get the most recent earnings call transcripts across all companies",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number for pagination",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of results per page",
            default=100,
        ),
    ],
    response_model=EarningsTranscript,
    example_queries=[
        "Get latest earnings call transcripts",
        "Recent company earnings calls",
        "Newest transcript releases",
    ],
)

EARNINGS_TRANSCRIPT: Endpoint = Endpoint(
    name="earnings_transcript",
    path="earning-call-transcript",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get earnings call transcript for a specific company and quarter",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        ),
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Fiscal year",
        ),
        EndpointParam(
            name="quarter",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Fiscal quarter (1-4)",
            valid_values=[1, 2, 3, 4],
        ),
    ],
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of transcripts to return",
        ),
    ],
    response_model=EarningsTranscript,
    example_queries=[
        "Get AAPL Q4 2024 earnings transcript",
        "Apple earnings call transcript",
        "Company earnings call Q1 2024",
    ],
)

TRANSCRIPT_DATES: Endpoint = Endpoint(
    name="transcript_dates",
    path="earning-call-transcript-dates",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get available transcript dates for a specific company",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        ),
    ],
    optional_params=[],
    response_model=TranscriptDate,
    example_queries=[
        "Get available transcript dates for AAPL",
        "When are MSFT transcripts available",
        "List of earnings call dates",
    ],
)

TRANSCRIPT_SYMBOLS: Endpoint = Endpoint(
    name="transcript_symbols",
    path="earnings-transcript-list",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get list of all symbols with available earnings transcripts",
    mandatory_params=[],
    optional_params=[],
    response_model=TranscriptSymbol,
    example_queries=[
        "Get symbols with earnings transcripts",
        "List companies with transcripts",
        "Available transcript symbols",
    ],
)
