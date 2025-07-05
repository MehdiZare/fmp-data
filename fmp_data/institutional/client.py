# fmp_data/institutional/client.py
from datetime import date
from typing import cast

from fmp_data.base import EndpointGroup
from fmp_data.institutional.endpoints import (
    ASSET_ALLOCATION,
    BENEFICIAL_OWNERSHIP,
    CIK_MAPPER,
    CIK_MAPPER_BY_NAME,
    CIK_MAPPER_BY_SYMBOL,
    FAIL_TO_DELIVER,
    FORM_13F,
    FORM_13F_DATES,
    INSIDER_ROSTER,
    INSIDER_STATISTICS,
    INSIDER_TRADES,
    INSTITUTIONAL_HOLDERS,
    INSTITUTIONAL_HOLDINGS,
    TRANSACTION_TYPES,
)
from fmp_data.institutional.models import (
    AssetAllocation,
    BeneficialOwnership,
    CIKCompanyMap,
    CIKMapping,
    FailToDeliver,
    Form13F,
    InsiderRoster,
    InsiderStatistic,
    InsiderTrade,
    InsiderTransactionType,
    InstitutionalHolder,
    InstitutionalHolding,
)


class InstitutionalClient(EndpointGroup):
    """Client for institutional activity endpoints"""

    def get_form_13f(self, cik: str, filing_date: date) -> list[Form13F]:
        """
        Get Form 13F filing data

        Args:
            cik: Central Index Key (CIK)
            filing_date: Filing date

        Returns:
            List of Form13F objects. Empty list if no records found.
        """
        try:
            result = self.client.request(
                FORM_13F, cik=cik, date=filing_date.strftime("%Y-%m-%d")
            )
            # Ensure we always return a list
            return result if isinstance(result, list) else [result]
        except Exception as e:
            # Log the error but return empty list instead of raising
            self.client.logger.warning(
                f"No Form 13F data found for CIK {cik} on {filing_date}: {e!s}"
            )
            return []

    def get_form_13f_dates(self, cik: str) -> list[Form13F]:
        """
        Get Form 13F filing dates

        Args:
            cik: Central Index Key (CIK)

        Returns:
            List of Form13F objects with filing dates. Empty list if no records found.
        """
        try:
            result = self.client.request(FORM_13F_DATES, cik=cik)
            # Ensure we always return a list
            return result if isinstance(result, list) else [result]
        except Exception as e:
            # Log the error but return empty list instead of raising
            self.client.logger.warning(
                f"No Form 13F filings found for CIK {cik}: {e!s}"
            )
            return []

    def get_asset_allocation(self, filing_date: date) -> list[AssetAllocation]:
        """Get 13F asset allocation data"""
        return self.client.request(
            ASSET_ALLOCATION, date=filing_date.strftime("%Y-%m-%d")
        )

    def get_institutional_holders(self) -> list[InstitutionalHolder]:
        """Get list of institutional holders"""
        return self.client.request(INSTITUTIONAL_HOLDERS)

    def get_institutional_holdings(
        self, symbol: str, include_current_quarter: bool = False
    ) -> list[InstitutionalHolding]:
        """Get institutional holdings by symbol"""
        return self.client.request(
            INSTITUTIONAL_HOLDINGS,
            symbol=symbol,
            includeCurrentQuarter=include_current_quarter,
        )

    def get_insider_trades(self, symbol: str, page: int = 0) -> list[InsiderTrade]:
        """Get insider trades"""
        return self.client.request(INSIDER_TRADES, symbol=symbol, page=page)

    def get_transaction_types(self) -> list[InsiderTransactionType]:
        """Get insider transaction types"""
        return self.client.request(TRANSACTION_TYPES)

    def get_insider_roster(self, symbol: str) -> list[InsiderRoster]:
        """Get insider roster"""
        return self.client.request(INSIDER_ROSTER, symbol=symbol)

    def get_insider_statistics(self, symbol: str) -> InsiderStatistic:
        """Get insider trading statistics"""
        result = self.client.request(INSIDER_STATISTICS, symbol=symbol)
        return cast(InsiderStatistic, result[0] if isinstance(result, list) else result)

    def get_cik_mappings(self, page: int = 0) -> list[CIKMapping]:
        """Get CIK to name mappings"""
        return self.client.request(CIK_MAPPER, page=page)

    def search_cik_by_name(self, name: str, page: int = 0) -> list[CIKMapping]:
        """Search CIK mappings by name"""
        return self.client.request(CIK_MAPPER_BY_NAME, name=name, page=page)

    def get_cik_by_symbol(self, symbol: str) -> list[CIKCompanyMap]:
        """Get CIK mapping for symbol"""
        return self.client.request(CIK_MAPPER_BY_SYMBOL, symbol=symbol)

    def get_beneficial_ownership(self, symbol: str) -> list[BeneficialOwnership]:
        """Get beneficial ownership data for a symbol"""
        return self.client.request(BENEFICIAL_OWNERSHIP, symbol=symbol)

    def get_fail_to_deliver(self, symbol: str, page: int = 0) -> list[FailToDeliver]:
        """Get fail to deliver data for a symbol"""
        return self.client.request(FAIL_TO_DELIVER, symbol=symbol, page=page)
