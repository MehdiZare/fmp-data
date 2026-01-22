# fmp_data/index/client.py
from fmp_data.base import EndpointGroup
from fmp_data.index.endpoints import (
    DOWJONES_CONSTITUENTS,
    HISTORICAL_DOWJONES,
    HISTORICAL_NASDAQ,
    HISTORICAL_SP500,
    NASDAQ_CONSTITUENTS,
    SP500_CONSTITUENTS,
)
from fmp_data.index.models import HistoricalIndexConstituent, IndexConstituent


class IndexClient(EndpointGroup):
    """Client for market index endpoints

    Provides methods to retrieve index constituents and historical changes.
    """

    def get_sp500_constituents(self) -> list[IndexConstituent]:
        """Get current S&P 500 index constituents

        Returns:
            List of S&P 500 constituent companies
        """
        return self.client.request(SP500_CONSTITUENTS)

    def get_nasdaq_constituents(self) -> list[IndexConstituent]:
        """Get current NASDAQ index constituents

        Returns:
            List of NASDAQ constituent companies
        """
        return self.client.request(NASDAQ_CONSTITUENTS)

    def get_dowjones_constituents(self) -> list[IndexConstituent]:
        """Get current Dow Jones Industrial Average constituents

        Returns:
            List of Dow Jones constituent companies
        """
        return self.client.request(DOWJONES_CONSTITUENTS)

    def get_historical_sp500(self) -> list[HistoricalIndexConstituent]:
        """Get historical S&P 500 constituent changes

        Returns:
            List of historical constituent additions and removals
        """
        return self.client.request(HISTORICAL_SP500)

    def get_historical_nasdaq(self) -> list[HistoricalIndexConstituent]:
        """Get historical NASDAQ constituent changes

        Returns:
            List of historical constituent additions and removals
        """
        return self.client.request(HISTORICAL_NASDAQ)

    def get_historical_dowjones(self) -> list[HistoricalIndexConstituent]:
        """Get historical Dow Jones constituent changes

        Returns:
            List of historical constituent additions and removals
        """
        return self.client.request(HISTORICAL_DOWJONES)
