# fmp_data/institutional/async_client.py
"""Async client for institutional activity endpoints."""

from datetime import date

from fmp_data.base import AsyncEndpointGroup
from fmp_data.institutional.endpoints import (
    ASSET_ALLOCATION,
    BENEFICIAL_OWNERSHIP,
    CIK_MAPPER,
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
    Form13FDate,
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


class AsyncInstitutionalClient(AsyncEndpointGroup):
    """Async client for institutional activity endpoints."""

    @staticmethod
    def _date_to_year_quarter(report_date: date) -> tuple[int, int]:
        quarter = (report_date.month - 1) // 3 + 1
        return report_date.year, quarter

    async def get_form_13f(self, cik: str, report_date: date) -> list[Form13F]:
        """
        Get Form 13F filing data

        Args:
            cik: Central Index Key (CIK)
            report_date: Report period end date (e.g., 2023-09-30)

        Returns:
            List of Form13F objects. Empty list if no records found.
        """
        year, quarter = self._date_to_year_quarter(report_date)
        try:
            result = await self.client.request_async(
                FORM_13F, cik=cik, year=year, quarter=quarter
            )
        except Exception as exc:
            self.client.logger.warning(
                f"No Form 13F data found for CIK {cik} on {report_date}: {exc!s}"
            )
            return []

        if isinstance(result, list):
            if not result:
                self.client.logger.warning(
                    "No Form 13F data found for CIK %s on %s.",
                    cik,
                    report_date,
                )
            return result
        return [result]

    async def get_form_13f_dates(self, cik: str) -> list[Form13FDate]:
        """
        Get Form 13F filing dates

        Args:
            cik: Central Index Key (CIK)

        Returns:
            List of Form13FDate objects with filing dates. Empty list if no
            records found.
        """
        try:
            result = await self.client.request_async(FORM_13F_DATES, cik=cik)
            # Ensure we always return a list
            return result if isinstance(result, list) else [result]
        except Exception as e:
            # Log the error but return empty list instead of raising
            self.client.logger.warning(
                f"No Form 13F filings found for CIK {cik}: {e!s}"
            )
            return []

    async def get_asset_allocation(self, report_date: date) -> list[AssetAllocation]:
        """Get 13F asset allocation data for a report period end date"""
        return await self.client.request_async(
            ASSET_ALLOCATION, date=report_date.strftime("%Y-%m-%d")
        )

    async def get_institutional_holders(
        self, page: int = 0, limit: int = 100
    ) -> list[InstitutionalHolder]:
        """Get list of institutional holders"""
        return await self.client.request_async(
            INSTITUTIONAL_HOLDERS, page=page, limit=limit
        )

    async def get_institutional_holdings(
        self,
        symbol: str,
        report_date: date,
        year: int | None = None,
        quarter: int | None = None,
    ) -> list[InstitutionalHolding]:
        """Get institutional holdings by symbol for a report period end date"""
        inferred_year, inferred_quarter = self._date_to_year_quarter(report_date)
        if year is not None and year != inferred_year:
            self.client.logger.warning(
                "Provided year %s does not match report_date %s (derived %s).",
                year,
                report_date,
                inferred_year,
            )
        if quarter is not None and quarter != inferred_quarter:
            self.client.logger.warning(
                "Provided quarter %s does not match report_date %s (derived %s).",
                quarter,
                report_date,
                inferred_quarter,
            )
        if year is None:
            year = inferred_year
        if quarter is None:
            quarter = inferred_quarter
        return await self.client.request_async(
            INSTITUTIONAL_HOLDINGS, symbol=symbol, year=year, quarter=quarter
        )

    async def get_insider_trades(
        self, symbol: str, page: int = 0, limit: int = 100
    ) -> list[InsiderTrade]:
        """Get insider trades"""
        return await self.client.request_async(
            INSIDER_TRADES, symbol=symbol, page=page, limit=limit
        )

    async def get_transaction_types(self) -> list[InsiderTransactionType]:
        """Get insider transaction types"""
        return await self.client.request_async(TRANSACTION_TYPES)

    async def get_insider_roster(self, symbol: str) -> list[InsiderRoster]:
        """Get insider roster"""
        return await self.client.request_async(INSIDER_ROSTER, symbol=symbol)

    async def get_insider_statistics(self, symbol: str) -> InsiderStatistic:
        """Get insider trading statistics"""
        result = await self.client.request_async(INSIDER_STATISTICS, symbol=symbol)
        return self._unwrap_single(result, InsiderStatistic)

    async def get_cik_mappings(
        self, page: int = 0, limit: int = 1000
    ) -> list[CIKMapping]:
        """Get CIK to name mappings"""
        return await self.client.request_async(CIK_MAPPER, page=page, limit=limit)

    async def search_cik_by_name(self, name: str, page: int = 0) -> list[CIKMapping]:
        """
        Search CIK mappings by name using client-side filtering.

        Note: The FMP API does not support server-side name filtering for CIK lookups.
        This method fetches a large batch of records (10,000) and filters them locally,
        which may impact performance for frequent searches.

        Args:
            name: Company name to search for (case-insensitive substring match)
            page: Page number for pagination (default: 0)

        Returns:
            List of CIK mappings matching the name
        """
        results = await self.client.request_async(CIK_MAPPER, page=page, limit=10000)
        if not isinstance(results, list):
            results = [results]
        name_upper = name.strip().upper()
        return [
            item
            for item in results
            if isinstance(item, CIKMapping)
            and name_upper in item.reporting_name.upper()
        ]

    async def get_beneficial_ownership(self, symbol: str) -> list[BeneficialOwnership]:
        """Get beneficial ownership data for a symbol"""
        return await self.client.request_async(BENEFICIAL_OWNERSHIP, symbol=symbol)

    async def get_fail_to_deliver(
        self, symbol: str, page: int = 0
    ) -> list[FailToDeliver]:
        """Get fail to deliver data for a symbol"""
        return await self.client.request_async(
            FAIL_TO_DELIVER, symbol=symbol, page=page
        )

    # Insider Trading Methods
    async def get_insider_trading_latest(
        self, page: int = 0, limit: int = 100, trade_date: date | None = None
    ) -> list[InsiderTradingLatest]:
        """Get latest insider trading activity"""
        params: dict[str, int | str | date] = {"page": page, "limit": limit}
        if trade_date is not None:
            params["date"] = trade_date
        return await self.client.request_async(INSIDER_TRADING_LATEST, **params)

    async def search_insider_trading(
        self,
        symbol: str | None = None,
        page: int = 0,
        limit: int = 100,
        reporting_cik: str | None = None,
        company_cik: str | None = None,
        transaction_type: str | None = None,
    ) -> list[InsiderTradingSearch]:
        """Search insider trades with optional filters"""
        params: dict[str, str | int] = {"page": page, "limit": limit}
        if symbol:
            params["symbol"] = symbol
        if reporting_cik:
            params["reportingCik"] = reporting_cik
        if company_cik:
            params["companyCik"] = company_cik
        if transaction_type:
            params["transactionType"] = transaction_type
        return await self.client.request_async(INSIDER_TRADING_SEARCH, **params)

    async def get_insider_trading_by_name(
        self, reporting_name: str, page: int = 0
    ) -> list[InsiderTradingByName]:
        """Search insider trades by reporting name"""
        return await self.client.request_async(
            INSIDER_TRADING_BY_NAME, name=reporting_name, page=page
        )

    async def get_insider_trading_statistics_enhanced(
        self, symbol: str
    ) -> InsiderTradingStatistics:
        """Get enhanced insider trading statistics"""
        result = await self.client.request_async(
            INSIDER_TRADING_STATISTICS_ENHANCED, symbol=symbol
        )
        return self._unwrap_single(result, InsiderTradingStatistics)

    # Form 13F Methods
    async def get_institutional_ownership_latest(
        self, cik: str | None = None, page: int = 0, limit: int = 100
    ) -> list[InstitutionalOwnershipLatest]:
        """Get latest institutional ownership filings"""
        params: dict[str, str | int] = {"page": page, "limit": limit}
        if cik:
            params["cik"] = cik
        return await self.client.request_async(INSTITUTIONAL_OWNERSHIP_LATEST, **params)

    async def get_institutional_ownership_extract(
        self, cik: str, report_date: date
    ) -> list[InstitutionalOwnershipExtract]:
        """Get filings extract data for a report period end date"""
        year, quarter = self._date_to_year_quarter(report_date)
        return await self.client.request_async(
            INSTITUTIONAL_OWNERSHIP_EXTRACT, cik=cik, year=year, quarter=quarter
        )

    async def get_institutional_ownership_dates(
        self, cik: str
    ) -> list[InstitutionalOwnershipDates]:
        """Get Form 13F filing dates"""
        return await self.client.request_async(INSTITUTIONAL_OWNERSHIP_DATES, cik=cik)

    async def get_institutional_ownership_analytics(
        self, symbol: str, report_date: date, page: int = 0, limit: int = 100
    ) -> list[InstitutionalOwnershipAnalytics]:
        """Get filings extract with analytics by holder for a report period end date"""
        year, quarter = self._date_to_year_quarter(report_date)
        return await self.client.request_async(
            INSTITUTIONAL_OWNERSHIP_ANALYTICS,
            symbol=symbol,
            year=year,
            quarter=quarter,
            page=page,
            limit=limit,
        )

    async def get_holder_performance_summary(
        self, cik: str, report_date: date | None = None, page: int = 0
    ) -> list[HolderPerformanceSummary]:
        """Get holder performance summary for a report period end date"""
        params: dict[str, str | int] = {"cik": cik, "page": page}
        if report_date:
            year, quarter = self._date_to_year_quarter(report_date)
            params["year"] = year
            params["quarter"] = quarter
        return await self.client.request_async(HOLDER_PERFORMANCE_SUMMARY, **params)

    async def get_holder_industry_breakdown(
        self, cik: str, report_date: date
    ) -> list[HolderIndustryBreakdown]:
        """Get holders industry breakdown for a report period end date"""
        year, quarter = self._date_to_year_quarter(report_date)
        params: dict[str, str | int] = {
            "cik": cik,
            "year": year,
            "quarter": quarter,
        }
        return await self.client.request_async(HOLDER_INDUSTRY_BREAKDOWN, **params)

    async def get_symbol_positions_summary(
        self, symbol: str, report_date: date
    ) -> list[SymbolPositionsSummary]:
        """Get positions summary by symbol for a report period end date"""
        year, quarter = self._date_to_year_quarter(report_date)
        params: dict[str, str | int] = {
            "symbol": symbol,
            "year": year,
            "quarter": quarter,
        }
        return await self.client.request_async(SYMBOL_POSITIONS_SUMMARY, **params)

    async def get_industry_performance_summary(
        self, report_date: date
    ) -> list[IndustryPerformanceSummary]:
        """Get industry performance summary for a report period end date"""
        year, quarter = self._date_to_year_quarter(report_date)
        params: dict[str, str | int] = {"year": year, "quarter": quarter}
        return await self.client.request_async(INDUSTRY_PERFORMANCE_SUMMARY, **params)
