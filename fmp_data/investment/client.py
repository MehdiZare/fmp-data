# fmp_data/investment/client.py
from datetime import date
import warnings

from fmp_data.base import EndpointGroup
from fmp_data.investment.endpoints import (
    ETF_COUNTRY_WEIGHTINGS,
    ETF_EXPOSURE,
    ETF_HOLDER,
    ETF_HOLDING_DATES,
    ETF_HOLDINGS,
    ETF_INFO,
    ETF_SECTOR_WEIGHTINGS,
    MUTUAL_FUND_BY_NAME,
    MUTUAL_FUND_DATES,
    MUTUAL_FUND_HOLDER,
    MUTUAL_FUND_HOLDINGS,
)
from fmp_data.investment.models import (
    ETFCountryWeighting,
    ETFExposure,
    ETFHolder,
    ETFHolding,
    ETFInfo,
    ETFSectorWeighting,
    MutualFundHolder,
    MutualFundHolding,
)


class InvestmentClient(EndpointGroup):
    """Client for investment products endpoints"""

    # ETF methods
    def get_etf_holdings(self, symbol: str, holdings_date: date) -> list[ETFHolding]:
        """Get ETF holdings"""
        return self.client.request(
            ETF_HOLDINGS, symbol=symbol, date=holdings_date.strftime("%Y-%m-%d")
        )

    def get_etf_holding_dates(self, symbol: str) -> list[date]:
        """Get ETF holding dates"""
        return self.client.request(ETF_HOLDING_DATES, symbol=symbol)

    def get_etf_info(self, symbol: str) -> ETFInfo | None:
        """
        Get ETF information

        Args:
            symbol: ETF symbol

        Returns:
            ETFInfo object if found, or None if no data/error occurs
        """
        try:
            result = self.client.request(ETF_INFO, symbol=symbol)
            if isinstance(result, list):
                return result[0] if result else None
            if isinstance(result, ETFInfo):
                return result
            warnings.warn(
                f"Unexpected result type from ETF_INFO: {type(result)}", stacklevel=2
            )
            return None
        except Exception as e:
            warnings.warn(f"Error in get_etf_info: {e!s}", stacklevel=2)
            return None

    def get_etf_sector_weightings(self, symbol: str) -> list[ETFSectorWeighting]:
        """Get ETF sector weightings"""
        return self.client.request(ETF_SECTOR_WEIGHTINGS, symbol=symbol)

    def get_etf_country_weightings(self, symbol: str) -> list[ETFCountryWeighting]:
        """Get ETF country weightings"""
        return self.client.request(ETF_COUNTRY_WEIGHTINGS, symbol=symbol)

    def get_etf_exposure(self, symbol: str) -> list[ETFExposure]:
        """Get ETF stock exposure"""
        return self.client.request(ETF_EXPOSURE, symbol=symbol)

    def get_etf_holder(self, symbol: str) -> list[ETFHolder]:
        """Get ETF holder information"""
        return self.client.request(ETF_HOLDER, symbol=symbol)

    # Mutual Fund methods
    def get_mutual_fund_dates(self, symbol: str, cik: str) -> list[date]:
        """Get mutual fund dates"""
        return self.client.request(MUTUAL_FUND_DATES, symbol=symbol, cik=cik)

    def get_mutual_fund_holdings(
        self, symbol: str, holdings_date: date
    ) -> list[MutualFundHolding]:
        """Get mutual fund holdings"""
        return self.client.request(
            MUTUAL_FUND_HOLDINGS, symbol=symbol, date=holdings_date.strftime("%Y-%m-%d")
        )

    def get_mutual_fund_by_name(self, name: str) -> list[MutualFundHolding]:
        """Get mutual funds by name"""
        return self.client.request(MUTUAL_FUND_BY_NAME, name=name)

    def get_mutual_fund_holder(self, symbol: str) -> list[MutualFundHolder]:
        """Get mutual fund holder information"""
        return self.client.request(MUTUAL_FUND_HOLDER, symbol=symbol)
