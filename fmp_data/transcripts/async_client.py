# fmp_data/transcripts/async_client.py
"""Async client for earnings transcript endpoints."""

from fmp_data.base import AsyncEndpointGroup
from fmp_data.transcripts.endpoints import (
    EARNINGS_TRANSCRIPT,
    LATEST_TRANSCRIPTS,
    TRANSCRIPT_DATES,
    TRANSCRIPT_SYMBOLS,
)
from fmp_data.transcripts.models import (
    EarningsTranscript,
    TranscriptDate,
    TranscriptSymbol,
)


class AsyncTranscriptsClient(AsyncEndpointGroup):
    """Async client for earnings transcript endpoints.

    Provides async methods to retrieve earnings call transcripts and related data.
    """

    async def get_latest(
        self, page: int = 0, limit: int = 100
    ) -> list[EarningsTranscript]:
        """Get the most recent earnings call transcripts

        Args:
            page: Page number for pagination (default: 0)
            limit: Number of results per page (default: 100)

        Returns:
            List of recent earnings transcripts
        """
        return await self.client.request_async(
            LATEST_TRANSCRIPTS, page=page, limit=limit
        )

    async def get_transcript(
        self,
        symbol: str,
        year: int,
        quarter: int,
        limit: int | None = None,
    ) -> list[EarningsTranscript]:
        """Get earnings call transcript for a specific company

        Args:
            symbol: Stock symbol
            year: Fiscal year
            quarter: Fiscal quarter 1-4
            limit: Number of transcripts to return (optional)

        Returns:
            List of matching earnings transcripts
        """
        params: dict[str, str | int] = {
            "symbol": symbol,
            "year": year,
            "quarter": quarter,
        }
        if limit is not None:
            params["limit"] = limit
        return await self.client.request_async(EARNINGS_TRANSCRIPT, **params)

    async def get_available_dates(self, symbol: str) -> list[TranscriptDate]:
        """Get available transcript dates for a specific company

        Args:
            symbol: Stock symbol

        Returns:
            List of available transcript dates
        """
        return await self.client.request_async(TRANSCRIPT_DATES, symbol=symbol)

    async def get_available_symbols(self) -> list[TranscriptSymbol]:
        """Get list of all symbols with available earnings transcripts

        Returns:
            List of symbols with transcripts
        """
        return await self.client.request_async(TRANSCRIPT_SYMBOLS)
