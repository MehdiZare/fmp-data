# fmp_data/institutional/client.py
from datetime import date
from typing import cast

from fmp_data.base import EndpointGroup
from fmp_data.institutional.endpoints import (
    ASSET_ALLOCATION,
    BENEFICIAL_OWNERSHIP,
    CIK_MAPPER,
    CIK_MAPPER_BY_NAME,
    FAIL_TO_DELIVER,
    FORM_13F,
    FORM_13F_DATES,
    HOLDER_INDUSTRY_BREAKDOWN,
    HOLDER_PERFORMANCE_SUMMARY,
    INDUSTRY_PERFORMANCE_SUMMARY,
    INSIDER_ROSTER,
    INSIDER_STATISTICS,
    INSIDER_TRADES,
    INSIDER_TRADING_BY_NAME,
    INSIDER_TRADING_LATEST,
    INSIDER_TRADING_SEARCH,
    INSIDER_TRADING_STATISTICS_ENHANCED,
    INSTITUTIONAL_HOLDERS,
    INSTITUTIONAL_HOLDINGS,
    INSTITUTIONAL_OWNERSHIP_ANALYTICS,
    INSTITUTIONAL_OWNERSHIP_DATES,
    INSTITUTIONAL_OWNERSHIP_EXTRACT,
    INSTITUTIONAL_OWNERSHIP_LATEST,
    SYMBOL_POSITIONS_SUMMARY,
    TRANSACTION_TYPES,
)
from fmp_data.institutional.models import (
    AssetAllocation,
    BeneficialOwnership,
    CIKMapping,
    FailToDeliver,
    Form13F,
    HolderIndustryBreakdown,
    HolderPerformanceSummary,
    IndustryPerformanceSummary,
    InsiderRoster,
    InsiderStatistic,
    InsiderTrade,
    InsiderTradingByName,
    InsiderTradingLatest,
    InsiderTradingSearch,
    InsiderTradingStatistics,
    InsiderTransactionType,
    InstitutionalHolder,
    InstitutionalHolding,
    InstitutionalOwnershipAnalytics,
    InstitutionalOwnershipDates,
    InstitutionalOwnershipExtract,
    InstitutionalOwnershipLatest,
    SymbolPositionsSummary,
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

    def get_beneficial_ownership(self, symbol: str) -> list[BeneficialOwnership]:
        """Get beneficial ownership data for a symbol"""
        return self.client.request(BENEFICIAL_OWNERSHIP, symbol=symbol)

    def get_fail_to_deliver(self, symbol: str, page: int = 0) -> list[FailToDeliver]:
        """Get fail to deliver data for a symbol"""
        return self.client.request(FAIL_TO_DELIVER, symbol=symbol, page=page)

    # Insider Trading Methods
    def get_insider_trading_latest(self, page: int = 0) -> list[InsiderTradingLatest]:
        """Get latest insider trading activity"""
        return self.client.request(INSIDER_TRADING_LATEST, page=page)

    def search_insider_trading(
        self, symbol: str | None = None, page: int = 0, limit: int = 100
    ) -> list[InsiderTradingSearch]:
        """Search insider trades with optional filters"""
        params: dict[str, str | int] = {"page": page, "limit": limit}
        if symbol:
            params["symbol"] = symbol
        return self.client.request(INSIDER_TRADING_SEARCH, **params)

    def get_insider_trading_by_name(
        self, reporting_name: str, page: int = 0
    ) -> list[InsiderTradingByName]:
        """Search insider trades by reporting name"""
        return self.client.request(
            INSIDER_TRADING_BY_NAME, reportingName=reporting_name, page=page
        )

    def get_insider_trading_statistics_enhanced(
        self, symbol: str
    ) -> InsiderTradingStatistics:
        """Get enhanced insider trading statistics"""
        result = self.client.request(INSIDER_TRADING_STATISTICS_ENHANCED, symbol=symbol)
        return cast(
            InsiderTradingStatistics, result[0] if isinstance(result, list) else result
        )

    # Form 13F Methods
    def get_institutional_ownership_latest(
        self, cik: str | None = None, page: int = 0
    ) -> list[InstitutionalOwnershipLatest]:
        """Get latest institutional ownership filings"""
        params: dict[str, str | int] = {"page": page}
        if cik:
            params["cik"] = cik
        return self.client.request(INSTITUTIONAL_OWNERSHIP_LATEST, **params)

    def get_institutional_ownership_extract(
        self, cik: str, filing_date: date
    ) -> list[InstitutionalOwnershipExtract]:
        """Get filings extract data"""
        return self.client.request(
            INSTITUTIONAL_OWNERSHIP_EXTRACT,
            cik=cik,
            date=filing_date.strftime("%Y-%m-%d"),
        )

    def get_institutional_ownership_dates(
        self, cik: str
    ) -> list[InstitutionalOwnershipDates]:
        """Get Form 13F filing dates"""
        return self.client.request(INSTITUTIONAL_OWNERSHIP_DATES, cik=cik)

    def get_institutional_ownership_analytics(
        self, cik: str, filing_date: date
    ) -> list[InstitutionalOwnershipAnalytics]:
        """Get filings extract with analytics by holder"""
        return self.client.request(
            INSTITUTIONAL_OWNERSHIP_ANALYTICS,
            cik=cik,
            date=filing_date.strftime("%Y-%m-%d"),
        )

    def get_holder_performance_summary(
        self, cik: str, filing_date: date | None = None
    ) -> list[HolderPerformanceSummary]:
        """Get holder performance summary"""
        params: dict[str, str] = {"cik": cik}
        if filing_date:
            params["date"] = filing_date.strftime("%Y-%m-%d")
        return self.client.request(HOLDER_PERFORMANCE_SUMMARY, **params)

    def get_holder_industry_breakdown(
        self, cik: str, filing_date: date | None = None
    ) -> list[HolderIndustryBreakdown]:
        """Get holders industry breakdown"""
        params: dict[str, str] = {"cik": cik}
        if filing_date:
            params["date"] = filing_date.strftime("%Y-%m-%d")
        return self.client.request(HOLDER_INDUSTRY_BREAKDOWN, **params)

    def get_symbol_positions_summary(
        self, symbol: str, filing_date: date | None = None
    ) -> list[SymbolPositionsSummary]:
        """Get positions summary by symbol"""
        params: dict[str, str] = {"symbol": symbol}
        if filing_date:
            params["date"] = filing_date.strftime("%Y-%m-%d")
        return self.client.request(SYMBOL_POSITIONS_SUMMARY, **params)

    def get_industry_performance_summary(
        self, industry: str, filing_date: date | None = None
    ) -> list[IndustryPerformanceSummary]:
        """Get industry performance summary"""
        params: dict[str, str] = {"industry": industry}
        if filing_date:
            params["date"] = filing_date.strftime("%Y-%m-%d")
        return self.client.request(INDUSTRY_PERFORMANCE_SUMMARY, **params)
