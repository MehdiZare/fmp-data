# fmp_data/institutional/client.py
from datetime import date

from fmp_data.base import EndpointGroup

from . import endpoints, models


class InstitutionalClient(EndpointGroup):
    """Client for institutional activity endpoints"""

    def get_form_13f(self, cik: str, filing_date: date) -> models.Form13F:
        """Get Form 13F filing data"""
        return self.client.request(
            endpoints.FORM_13F, cik=cik, date=filing_date.strftime("%Y-%m-%d")
        )

    def get_form_13f_dates(self, cik: str) -> models.Form13F:
        """Get Form 13F filing data"""
        return self.client.request(endpoints.FORM_13F_DATES, cik=cik)

    def get_asset_allocation(self, filing_date: date) -> list[models.AssetAllocation]:
        """Get 13F asset allocation data"""
        return self.client.request(
            endpoints.ASSET_ALLOCATION, date=filing_date.strftime("%Y-%m-%d")
        )

    def get_institutional_holders(self) -> list[models.InstitutionalHolder]:
        """Get list of institutional holders"""
        return self.client.request(endpoints.INSTITUTIONAL_HOLDERS)

    def get_institutional_holdings(
        self, symbol: str, include_current_quarter: bool = False
    ) -> list[models.InstitutionalHolding]:
        """Get institutional holdings by symbol"""
        return self.client.request(
            endpoints.INSTITUTIONAL_HOLDINGS,
            symbol=symbol,
            includeCurrentQuarter=include_current_quarter,
        )

    def get_insider_trades(
        self, symbol: str, page: int = 0
    ) -> list[models.InsiderTrade]:
        """Get insider trades"""
        return self.client.request(endpoints.INSIDER_TRADES, symbol=symbol, page=page)

    def get_transaction_types(self) -> list[models.InsiderTransactionType]:
        """Get insider transaction types"""
        return self.client.request(endpoints.TRANSACTION_TYPES)

    def get_insider_roster(self, symbol: str) -> list[models.InsiderRoster]:
        """Get insider roster"""
        return self.client.request(endpoints.INSIDER_ROSTER, symbol=symbol)

    def get_insider_statistics(self, symbol: str) -> models.InsiderStatistic:
        """Get insider trading statistics"""
        result = self.client.request(endpoints.INSIDER_STATISTICS, symbol=symbol)
        return result[0] if isinstance(result, list) else result
