# fmp_data/institutional/async_client.py
"""Async client for institutional activity endpoints."""

from datetime import date
import warnings

from fmp_data.base import AsyncEndpointGroup
from fmp_data.exceptions import FMPError, ValidationError
from fmp_data.helpers import deprecated
from fmp_data.institutional.endpoints import (
    BENEFICIAL_OWNERSHIP,
    CIK_MAPPER,
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

    async def get_form_13f_by_quarter(
        self, cik: str | int, year: int, quarter: int
    ) -> list[Form13F]:
        """
        Get Form 13F filing data for a calendar quarter.

        The wire shape of ``/stable/institutional-ownership/extract``: ``year``
        and ``quarter`` are mandatory query parameters and there is no date
        parameter. See the sync
        :meth:`~fmp_data.institutional.client.InstitutionalClient.get_form_13f_by_quarter`.

        Args:
            cik: Central Index Key (CIK)
            year: Filing year (e.g., 2023)
            quarter: Calendar quarter, 1-4

        Returns:
            List of Form13F objects. Empty list if no records found.

        Note:
            **Empty on error**, matching the sync client — see
            :meth:`~fmp_data.institutional.client.InstitutionalClient.get_form_13f_by_quarter`
            for why, and for what is deliberately *not* swallowed (#193).
        """
        try:
            result = await self.client.request_async(
                FORM_13F, cik=cik, year=year, quarter=quarter
            )
        except (FMPError, ValidationError) as exc:
            # Narrowed from bare ``Exception`` in #193, to match the sync
            # client. "No 13F data" is a claim about the *API's* answer; a
            # TypeError or AttributeError in our own code is not that, and
            # swallowing one reported an empty portfolio for what was really
            # a bug here.
            self.client.logger.warning(
                f"No Form 13F data found for CIK {cik} in {year} Q{quarter}: {exc!s}"
            )
            return []

        if isinstance(result, list):
            if not result:
                self.client.logger.warning(
                    "No Form 13F data found for CIK %s in %s Q%s.",
                    cik,
                    year,
                    quarter,
                )
            return result
        return [result]

    async def get_form_13f(self, cik: str | int, report_date: date) -> list[Form13F]:
        """
        Get Form 13F filing data for the quarter containing ``report_date``.

        Args:
            cik: Central Index Key (CIK)
            report_date: Any date inside the report period (e.g., 2023-09-30).
                Only its year and calendar quarter reach the API.

        Returns:
            List of Form13F objects. Empty list if no records found.
        """
        year, quarter = self._date_to_year_quarter(report_date)
        return await self.get_form_13f_by_quarter(cik, year, quarter)

    async def get_form_13f_dates(self, cik: str | int) -> list[Form13FDate]:
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
        except (FMPError, ValidationError) as e:
            # API errors (404, validation, etc.) return empty list for
            # convenience; narrowed from bare ``Exception`` in #193 to match
            # the sync client, so a bug in our own code still surfaces.
            self.client.logger.warning(
                f"No Form 13F filings found for CIK {cik}: {e!s}"
            )
            return []

    @deprecated(
        "The FMP API no longer serves 13F asset allocation, and no stable "
        "endpoint replaces it -- hyphen, slash and plural variants all 404. "
        "The nearest live data is per-filer holdings via "
        "get_institutional_holdings(), which must be aggregated by hand."
    )
    async def get_asset_allocation(self, report_date: date) -> list[AssetAllocation]:
        """Get 13F asset allocation data for a report period end date

        .. deprecated::
            This endpoint 404s on the FMP API and will be removed in a future
            version. It currently returns an empty list. FMP publishes no
            stable replacement for the pre-aggregated allocation breakdown;
            the closest live source is per-filer 13F holdings, which you
            would have to aggregate yourself.
        """
        return []

    async def get_institutional_holders(
        self, page: int = 0, limit: int = 100
    ) -> list[InstitutionalHolder]:
        """Get list of institutional holders"""
        return await self.client.request_async(
            INSTITUTIONAL_HOLDERS, page=page, limit=limit
        )

    async def get_institutional_holdings_by_quarter(
        self, symbol: str, year: int, quarter: int
    ) -> list[InstitutionalHolding]:
        """Get institutional holdings for a symbol in a calendar quarter.

        The wire shape of ``/stable/institutional-ownership/
        symbol-positions-summary``: ``year`` and ``quarter`` are mandatory and
        the API rejects a request without them (#188).

        Args:
            symbol: Stock symbol
            year: Filing year (e.g., 2023)
            quarter: Calendar quarter, 1-4
        """
        return await self.client.request_async(
            INSTITUTIONAL_HOLDINGS, symbol=symbol, year=year, quarter=quarter
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
        return await self.get_institutional_holdings_by_quarter(symbol, year, quarter)

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

    @deprecated(
        "The FMP API no longer serves fail-to-deliver data and publishes no "
        "stable replacement. The underlying data is still available directly "
        "from the SEC's own fails-to-deliver files."
    )
    async def get_fail_to_deliver(
        self, symbol: str, page: int = 0
    ) -> list[FailToDeliver]:
        """Get fail to deliver data for a symbol

        .. deprecated::
            This endpoint 404s on the FMP API and will be removed in a future
            version. It currently returns an empty list. No stable FMP
            endpoint replaces it; the SEC publishes the same fails-to-deliver
            data itself, which is the only remaining source.
        """
        return []

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
        self, cik: str | int | None = None, page: int = 0, limit: int = 100
    ) -> list[InstitutionalOwnershipLatest]:
        """Get latest institutional ownership filings"""
        params: dict[str, str | int] = {"page": page, "limit": limit}
        if cik:
            params["cik"] = cik
        return await self.client.request_async(INSTITUTIONAL_OWNERSHIP_LATEST, **params)

    async def get_institutional_ownership_extract_by_quarter(
        self, cik: str | int, year: int, quarter: int
    ) -> list[InstitutionalOwnershipExtract]:
        """Get filings extract data for a calendar quarter (#192).

        Wire shape of ``/institutional-ownership/extract``; ``year`` and
        ``quarter`` are mandatory and there is no date parameter.
        """
        return await self.client.request_async(
            INSTITUTIONAL_OWNERSHIP_EXTRACT, cik=cik, year=year, quarter=quarter
        )

    async def get_institutional_ownership_extract(
        self, cik: str | int, report_date: date
    ) -> list[InstitutionalOwnershipExtract]:
        """Get filings extract data for the quarter containing ``report_date``"""
        year, quarter = self._date_to_year_quarter(report_date)
        return await self.get_institutional_ownership_extract_by_quarter(
            cik, year, quarter
        )

    async def get_institutional_ownership_dates(
        self, cik: str | int
    ) -> list[InstitutionalOwnershipDates]:
        """Get Form 13F filing dates"""
        return await self.client.request_async(INSTITUTIONAL_OWNERSHIP_DATES, cik=cik)

    async def get_institutional_ownership_analytics_by_quarter(
        self,
        symbol: str,
        year: int,
        quarter: int,
        page: int = 0,
        limit: int = 100,
    ) -> list[InstitutionalOwnershipAnalytics]:
        """Get filings extract with analytics by holder, for a calendar quarter."""
        return await self.client.request_async(
            INSTITUTIONAL_OWNERSHIP_ANALYTICS,
            symbol=symbol,
            year=year,
            quarter=quarter,
            page=page,
            limit=limit,
        )

    async def get_institutional_ownership_analytics(
        self, symbol: str, report_date: date, page: int = 0, limit: int = 100
    ) -> list[InstitutionalOwnershipAnalytics]:
        """Analytics by holder for the quarter containing ``report_date``"""
        year, quarter = self._date_to_year_quarter(report_date)
        return await self.get_institutional_ownership_analytics_by_quarter(
            symbol, year, quarter, page=page, limit=limit
        )

    async def get_holder_performance_summary(
        self, cik: str | int, report_date: date | None = None, page: int = 0
    ) -> list[HolderPerformanceSummary]:
        """Get holder performance summary -- full history, *not* one quarter.

        Warning:
            ``report_date`` has **no effect**; see the sync
            :meth:`~fmp_data.institutional.client.InstitutionalClient.get_holder_performance_summary`
            for the live-API evidence. Passing it emits a
            :class:`UserWarning` (#192).
        """
        params: dict[str, str | int] = {"cik": cik, "page": page}
        if report_date:
            warnings.warn(
                "institutional.get_holder_performance_summary(report_date=...) "
                "has no effect: the FMP endpoint accepts year/quarter but "
                "returns the holder's full history regardless. You are "
                "getting every period, not the one you asked for; filter the "
                "result by its 'date' field instead.",
                UserWarning,
                stacklevel=2,
            )
            year, quarter = self._date_to_year_quarter(report_date)
            params["year"] = year
            params["quarter"] = quarter
        return await self.client.request_async(HOLDER_PERFORMANCE_SUMMARY, **params)

    async def get_holder_industry_breakdown_by_quarter(
        self, cik: str | int, year: int, quarter: int
    ) -> list[HolderIndustryBreakdown]:
        """Get holders industry breakdown for a calendar quarter."""
        return await self.client.request_async(
            HOLDER_INDUSTRY_BREAKDOWN, cik=cik, year=year, quarter=quarter
        )

    async def get_holder_industry_breakdown(
        self, cik: str | int, report_date: date
    ) -> list[HolderIndustryBreakdown]:
        """Holders industry breakdown for the quarter containing ``report_date``"""
        year, quarter = self._date_to_year_quarter(report_date)
        return await self.get_holder_industry_breakdown_by_quarter(cik, year, quarter)

    async def get_symbol_positions_summary_by_quarter(
        self, symbol: str, year: int, quarter: int
    ) -> list[SymbolPositionsSummary]:
        """Get positions summary by symbol for a calendar quarter."""
        return await self.client.request_async(
            SYMBOL_POSITIONS_SUMMARY, symbol=symbol, year=year, quarter=quarter
        )

    async def get_symbol_positions_summary(
        self, symbol: str, report_date: date
    ) -> list[SymbolPositionsSummary]:
        """Positions summary for the quarter containing ``report_date``"""
        year, quarter = self._date_to_year_quarter(report_date)
        return await self.get_symbol_positions_summary_by_quarter(symbol, year, quarter)

    async def get_industry_performance_summary_by_quarter(
        self, year: int, quarter: int
    ) -> list[IndustryPerformanceSummary]:
        """Get industry performance summary for a calendar quarter."""
        return await self.client.request_async(
            INDUSTRY_PERFORMANCE_SUMMARY, year=year, quarter=quarter
        )

    async def get_industry_performance_summary(
        self, report_date: date
    ) -> list[IndustryPerformanceSummary]:
        """Industry performance summary for the quarter containing ``report_date``"""
        year, quarter = self._date_to_year_quarter(report_date)
        return await self.get_industry_performance_summary_by_quarter(year, quarter)
