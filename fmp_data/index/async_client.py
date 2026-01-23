# fmp_data/index/async_client.py
"""Async client for market index endpoints."""

from fmp_data.base import AsyncEndpointGroup
from fmp_data.index.endpoints import (
    DOWJONES_CONSTITUENTS,
    HISTORICAL_DOWJONES,
    HISTORICAL_NASDAQ,
    HISTORICAL_SP500,
    NASDAQ_CONSTITUENTS,
    SP500_CONSTITUENTS,
)
from fmp_data.index.models import HistoricalIndexConstituent, IndexConstituent


class AsyncIndexClient(AsyncEndpointGroup):
    """Async client for market index endpoints.

    Provides async methods to retrieve index constituents and historical changes.
    """

    async def get_sp500_constituents(self) -> list[IndexConstituent]:
        """Get current S&P 500 index constituents

        Returns:
            List of S&P 500 constituent companies
        """
        return await self.client.request_async(SP500_CONSTITUENTS)

    async def get_nasdaq_constituents(self) -> list[IndexConstituent]:
        """Get current NASDAQ index constituents

        Returns:
            List of NASDAQ constituent companies
        """
        return await self.client.request_async(NASDAQ_CONSTITUENTS)

    async def get_dowjones_constituents(self) -> list[IndexConstituent]:
        """Get current Dow Jones Industrial Average constituents

        Returns:
            List of Dow Jones constituent companies
        """
        return await self.client.request_async(DOWJONES_CONSTITUENTS)

    async def get_historical_sp500(self) -> list[HistoricalIndexConstituent]:
        """Get historical S&P 500 constituent changes

        Returns:
            List of historical constituent additions and removals
        """
        return await self.client.request_async(HISTORICAL_SP500)

    async def get_historical_nasdaq(self) -> list[HistoricalIndexConstituent]:
        """Get historical NASDAQ constituent changes

        Returns:
            List of historical constituent additions and removals
        """
        return await self.client.request_async(HISTORICAL_NASDAQ)

    async def get_historical_dowjones(self) -> list[HistoricalIndexConstituent]:
        """Get historical Dow Jones constituent changes

        Returns:
            List of historical constituent additions and removals
        """
        return await self.client.request_async(HISTORICAL_DOWJONES)
