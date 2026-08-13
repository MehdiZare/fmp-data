# fmp_data/company/async_client.py
"""Async client for company-related API endpoints.

This is the async counterpart to CompanyClient. All methods are async
and have the same names as their sync equivalents (no _async suffix).
"""

from __future__ import annotations

from datetime import date

from fmp_data.base import AsyncEndpointGroup
from fmp_data.company.endpoints import (
    AFTERMARKET_QUOTE,
    AFTERMARKET_TRADE,
    ANALYST_ESTIMATES,
    BALANCE_SHEET_AS_REPORTED,
    BALANCE_SHEET_GROWTH,
    BALANCE_SHEET_TTM,
    CASH_FLOW_AS_REPORTED,
    CASH_FLOW_GROWTH,
    CASH_FLOW_TTM,
    COMPANY_DIVIDENDS,
    COMPANY_EARNINGS,
    COMPANY_NOTES,
    COMPANY_PEERS,
    COMPANY_SPLITS,
    DELISTED_COMPANIES,
    EMPLOYEE_COUNT,
    ENTERPRISE_VALUES,
    EXECUTIVE_COMPENSATION,
    EXECUTIVE_COMPENSATION_BENCHMARK,
    FINANCIAL_GROWTH,
    FINANCIAL_RATIOS_TTM,
    FINANCIAL_REPORTS_JSON,
    FINANCIAL_REPORTS_XLSX,
    FINANCIAL_SCORES,
    GEOGRAPHIC_REVENUE_SEGMENTATION,
    HISTORICAL_MARKET_CAP,
    HISTORICAL_PRICE,
    HISTORICAL_PRICE_DIVIDEND_ADJUSTED,
    HISTORICAL_PRICE_LIGHT,
    HISTORICAL_PRICE_NON_SPLIT_ADJUSTED,
    INCOME_STATEMENT_AS_REPORTED,
    INCOME_STATEMENT_GROWTH,
    INCOME_STATEMENT_TTM,
    INTRADAY_PRICE,
    KEY_EXECUTIVES,
    KEY_METRICS_TTM,
    MARKET_CAP,
    MERGERS_ACQUISITIONS_LATEST,
    MERGERS_ACQUISITIONS_SEARCH,
    PRICE_TARGET_CONSENSUS,
    PRICE_TARGET_SUMMARY,
    PRODUCT_REVENUE_SEGMENTATION,
    PROFILE,
    PROFILE_CIK,
    QUOTE,
    SHARE_FLOAT,
    SIMPLE_QUOTE,
    STOCK_PRICE_CHANGE,
    SYMBOL_CHANGES,
)
from fmp_data.company.models import (
    AftermarketQuote,
    AftermarketTrade,
    AnalystEstimate,
    AnalystRecommendation,
    CompanyCoreInformation,
    CompanyExecutive,
    CompanyNote,
    CompanyPeer,
    CompanyProfile,
    DelistedCompany,
    EmployeeCount,
    ExecutiveCompensation,
    ExecutiveCompensationBenchmark,
    FinancialReportJSON,
    GeographicRevenueSegment,
    HistoricalData,
    HistoricalPrice,
    HistoricalShareFloat,
    IntradayPrice,
    MergerAcquisition,
    PriceTarget,
    PriceTargetConsensus,
    PriceTargetSummary,
    ProductRevenueSegment,
    Quote,
    ShareFloat,
    SimpleQuote,
    StockPriceChange,
    SymbolChange,
    UpgradeDowngrade,
    UpgradeDowngradeConsensus,
)
from fmp_data.exceptions import (
    FMPNotFound,
    InvalidResponseTypeError,
    InvalidSymbolError,
)
from fmp_data.fundamental.models import (
    AsReportedBalanceSheet,
    AsReportedCashFlowStatement,
    AsReportedIncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    EnterpriseValue,
    FinancialGrowth,
    FinancialRatiosTTM,
    FinancialScore,
    IncomeStatement,
    KeyMetricsTTM,
)
from fmp_data.helpers import deprecated
from fmp_data.intelligence.models import DividendEvent, EarningEvent, StockSplitEvent
from fmp_data.models import MarketCapitalization


def _format_date(value: date | None) -> str | None:
    if value is None:
        return None
    return value.strftime("%Y-%m-%d")


class AsyncCompanyClient(AsyncEndpointGroup):
    """Async client for company-related API endpoints.

    All methods are async and use the same names as the sync CompanyClient.

    Example:
        async with AsyncFMPDataClient.from_env() as client:
            profile = await client.company.get_profile("AAPL")
    """

    async def get_profile(self, symbol: str) -> CompanyProfile:
        """Get company profile"""
        result = await self.client.request_async(PROFILE, symbol=symbol)
        profile = self._unwrap_single(result, CompanyProfile, allow_none=True)
        if profile is None:
            raise FMPNotFound(symbol)
        return profile

    async def get_profile_cik(self, cik: str) -> CompanyProfile:
        """Get company profile by CIK number"""
        result = await self.client.request_async(PROFILE_CIK, cik=cik)
        profile = self._unwrap_single(result, CompanyProfile, allow_none=True)
        if profile is None:
            raise FMPNotFound(cik)
        return profile

    @deprecated(
        "The FMP API no longer serves company-core-information. Use "
        "get_profile(symbol), which is live but returns a flatter payload -- "
        "it carries cik, exchange, industry and sector, and does not carry "
        "the registration fields such as the SIC and state of incorporation."
    )
    async def get_core_information(self, symbol: str) -> CompanyCoreInformation | None:
        """Get core company information

        .. deprecated::
            ``company-core-information`` 404s on the FMP API and will be
            removed in a future version. It currently returns ``None``.
            Use :meth:`get_profile` instead. It is not a drop-in: ``profile``
            is a flatter record and does not carry the registration-detail
            fields this model declares, so read the fields you need from
            :class:`~fmp_data.company.models.CompanyProfile` directly.
        """
        return None

    async def get_executives(self, symbol: str) -> list[CompanyExecutive]:
        """Get company executives information"""
        return self._unwrap_list(
            await self.client.request_async(KEY_EXECUTIVES, symbol=symbol),
            CompanyExecutive,
        )

    async def get_employee_count(self, symbol: str) -> list[EmployeeCount]:
        """Get company employee count history"""
        return self._unwrap_list(
            await self.client.request_async(EMPLOYEE_COUNT, symbol=symbol),
            EmployeeCount,
        )

    async def get_company_notes(self, symbol: str) -> list[CompanyNote]:
        """Get company financial notes"""
        return self._unwrap_list(
            await self.client.request_async(COMPANY_NOTES, symbol=symbol), CompanyNote
        )

    def get_company_logo_url(self, symbol: str) -> str:
        """Get the company logo URL (sync, no API call needed)"""
        if not symbol or not symbol.strip():
            raise InvalidSymbolError()
        base_url = self.client.config.base_url.rstrip("/")
        return f"{base_url}/image-stock/{symbol}.png"

    async def get_quote(self, symbol: str) -> Quote:
        """Get real-time stock quote"""
        result = await self.client.request_async(QUOTE, symbol=symbol)
        return self._unwrap_single(result, Quote)

    async def get_simple_quote(self, symbol: str) -> SimpleQuote:
        """Get simple stock quote"""
        result = await self.client.request_async(SIMPLE_QUOTE, symbol=symbol)
        return self._unwrap_single(result, SimpleQuote)

    async def get_aftermarket_trade(self, symbol: str) -> AftermarketTrade:
        """Get aftermarket trade data"""
        result = await self.client.request_async(AFTERMARKET_TRADE, symbol=symbol)
        return self._unwrap_single(result, AftermarketTrade)

    async def get_aftermarket_quote(self, symbol: str) -> AftermarketQuote:
        """Get aftermarket quote data"""
        result = await self.client.request_async(AFTERMARKET_QUOTE, symbol=symbol)
        return self._unwrap_single(result, AftermarketQuote)

    async def get_stock_price_change(self, symbol: str) -> StockPriceChange:
        """Get stock price change percentages across time horizons"""
        result = await self.client.request_async(STOCK_PRICE_CHANGE, symbol=symbol)
        return self._unwrap_single(result, StockPriceChange)

    async def get_historical_prices(
        self,
        symbol: str,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> HistoricalData:
        """Get historical daily price data

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            HistoricalData object containing the price history
        """
        params: dict[str, str | int] = {"symbol": symbol}
        start_date = _format_date(from_date)
        end_date = _format_date(to_date)
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        rows = self._unwrap_list(
            await self.client.request_async(HISTORICAL_PRICE, **params),
            HistoricalPrice,
        )
        return HistoricalData(symbol=symbol, historical=rows)

    async def get_intraday_prices(
        self,
        symbol: str,
        interval: str = "1min",
        from_date: date | None = None,
        to_date: date | None = None,
        nonadjusted: bool | None = None,
    ) -> list[IntradayPrice]:
        """Get intraday price data

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            interval: Time interval (1min, 5min, 15min, 30min, 1hour, 4hour)
            from_date: Start date (optional)
            to_date: End date (optional)
            nonadjusted: Use non-adjusted data (optional)
        """
        start_date = _format_date(from_date)
        end_date = _format_date(to_date)
        return self._unwrap_list(
            await self.client.request_async(
                INTRADAY_PRICE,
                symbol=symbol,
                interval=interval,
                start_date=start_date,
                end_date=end_date,
                nonadjusted=nonadjusted,
            ),
            IntradayPrice,
        )

    async def get_executive_compensation(
        self, symbol: str
    ) -> list[ExecutiveCompensation]:
        """Get executive compensation data for a company"""
        return self._unwrap_list(
            await self.client.request_async(EXECUTIVE_COMPENSATION, symbol=symbol),
            ExecutiveCompensation,
        )

    @deprecated(
        "historical/shares-float is dead. The live path shares-float is "
        "already shipped as get_share_float(symbol); this method is a "
        "leftover declaration, not a second data source. It returns the "
        "current snapshot, not a time series."
    )
    async def get_historical_share_float(
        self, symbol: str
    ) -> list[HistoricalShareFloat]:
        """Get historical share float data for a company

        .. deprecated::
            ``historical/shares-float`` 404s and will be removed in a future
            version. It currently returns an empty list. Use
            :meth:`get_share_float`, which serves the live ``shares-float``
            with the same fields (``date``, ``floatShares``, ``freeFloat``,
            ``outstandingShares``, ``source``, ``symbol``). It is not a
            drop-in: it answers with the current snapshot rather than a
            history, so back-fill is no longer available from FMP.
        """
        return []

    async def get_product_revenue_segmentation(
        self, symbol: str, period: str = "annual"
    ) -> list[ProductRevenueSegment]:
        """Get revenue segmentation by product.

        Args:
            symbol: Company symbol
            period: Data period ('annual' or 'quarter')

        Returns:
            List of product revenue segments by fiscal year
        """
        return self._unwrap_list(
            await self.client.request_async(
                PRODUCT_REVENUE_SEGMENTATION,
                symbol=symbol,
                structure="flat",
                period=period,
            ),
            ProductRevenueSegment,
        )

    async def get_geographic_revenue_segmentation(
        self, symbol: str, period: str = "annual"
    ) -> list[GeographicRevenueSegment]:
        """Get revenue segmentation by geographic region.

        Args:
            symbol: Company symbol
            period: Data period ('annual' or 'quarter')

        Returns:
            List of geographic revenue segments by fiscal year
        """
        return self._unwrap_list(
            await self.client.request_async(
                GEOGRAPHIC_REVENUE_SEGMENTATION,
                symbol=symbol,
                structure="flat",
                period=period,
            ),
            GeographicRevenueSegment,
        )

    async def get_symbol_changes(self) -> list[SymbolChange]:
        """Get symbol change history"""
        return self._unwrap_list(
            await self.client.request_async(SYMBOL_CHANGES), SymbolChange
        )

    async def get_delisted_companies(
        self, page: int = 0, limit: int = 100
    ) -> list[DelistedCompany]:
        """Get companies FMP reports as delisted.

        Args:
            page: Page number for pagination (default 0)
            limit: Number of results per page (default 100)

        Returns:
            List of slim delisted rows (symbol, companyName, exchange,
            IPO and delist dates).
        """
        return self._unwrap_list(
            await self.client.request_async(DELISTED_COMPANIES, page=page, limit=limit),
            DelistedCompany,
        )

    async def get_share_float(self, symbol: str) -> ShareFloat:
        """Get current share float data for a company"""
        result = await self.client.request_async(SHARE_FLOAT, symbol=symbol)
        return self._unwrap_single(result, ShareFloat)

    async def get_market_cap(self, symbol: str) -> MarketCapitalization:
        """Get market capitalization data"""
        result = await self.client.request_async(MARKET_CAP, symbol=symbol)
        return self._unwrap_single(result, MarketCapitalization)

    async def get_historical_market_cap(
        self, symbol: str
    ) -> list[MarketCapitalization]:
        """Get historical market capitalization data"""
        return self._unwrap_list(
            await self.client.request_async(HISTORICAL_MARKET_CAP, symbol=symbol),
            MarketCapitalization,
        )

    @deprecated(
        "The FMP API no longer serves the price-target series. Use "
        "get_price_target_summary(symbol) or get_price_target_consensus"
        "(symbol) -- both are live, but they are aggregates, not the "
        "per-analyst time series this method returned."
    )
    async def get_price_target(self, symbol: str) -> list[PriceTarget]:
        """Get price targets

        .. deprecated::
            ``price-target`` 404s on the FMP API and will be removed in a
            future version. It currently returns an empty list.
            Use :meth:`get_price_target_summary` or
            :meth:`get_price_target_consensus`. Neither is a drop-in: this
            method yielded one row per analyst target, and both replacements
            return a single aggregated record with no per-analyst detail.
        """
        return []

    async def get_price_target_summary(self, symbol: str) -> PriceTargetSummary:
        """Get price target summary"""
        result = await self.client.request_async(PRICE_TARGET_SUMMARY, symbol=symbol)
        return self._unwrap_single(result, PriceTargetSummary)

    async def get_price_target_consensus(self, symbol: str) -> PriceTargetConsensus:
        """Get price target consensus"""
        result = await self.client.request_async(PRICE_TARGET_CONSENSUS, symbol=symbol)
        return self._unwrap_single(result, PriceTargetConsensus)

    async def get_analyst_estimates(
        self,
        symbol: str,
        period: str = "annual",
        page: int = 0,
        limit: int = 10,
    ) -> list[AnalystEstimate]:
        """Get analyst estimates"""
        return self._unwrap_list(
            await self.client.request_async(
                ANALYST_ESTIMATES,
                symbol=symbol,
                period=period,
                page=page,
                limit=limit,
            ),
            AnalystEstimate,
        )

    @deprecated(
        "The FMP API no longer serves analyst-stock-recommendations. Use "
        "FMPDataClient.intelligence.get_grades_consensus(symbol), which is "
        "live but returns a single consensus tally (strongBuy/buy/hold/sell/"
        "strongSell counts), not the monthly recommendation series."
    )
    async def get_analyst_recommendations(
        self, symbol: str
    ) -> list[AnalystRecommendation]:
        """Get analyst recommendations

        .. deprecated::
            ``analyst-stock-recommendations`` 404s on the FMP API and will be
            removed in a future version. It currently returns an empty list.
            Use ``client.intelligence.get_grades_consensus(symbol)``. It is
            not a drop-in: this method returned one row per month with
            rolling counts, and the replacement returns one current consensus
            record.
        """
        return []

    @deprecated(
        "The FMP API no longer serves upgrades-downgrades. Use "
        "FMPDataClient.intelligence.get_grades(symbol), which is live and "
        "carries the same grade changes under different field names "
        "(gradingCompany/previousGrade/newGrade rather than "
        "gradingCompany/previousGrade/newGrade plus action and priceTarget)."
    )
    async def get_upgrades_downgrades(self, symbol: str) -> list[UpgradeDowngrade]:
        """Get upgrades and downgrades

        .. deprecated::
            ``upgrades-downgrades`` 404s on the FMP API and will be removed in
            a future version. It currently returns an empty list.
            Use ``client.intelligence.get_grades(symbol)``, which returns the
            same class of grade-change rows via
            :class:`~fmp_data.intelligence.models.StockGrade`. It is not a
            drop-in: the field names differ and the action/price-target
            columns this model declared are absent.
        """
        return []

    @deprecated(
        "The FMP API no longer serves upgrades-downgrades-consensus. Use "
        "FMPDataClient.intelligence.get_grades_consensus(symbol), which is "
        "live and returns the equivalent consensus tally."
    )
    async def get_upgrades_downgrades_consensus(
        self, symbol: str
    ) -> UpgradeDowngradeConsensus | None:
        """Get upgrades and downgrades consensus

        .. deprecated::
            ``upgrades-downgrades-consensus`` 404s on the FMP API and will be
            removed in a future version. It currently returns ``None``.
            Use ``client.intelligence.get_grades_consensus(symbol)``, which
            returns :class:`
            ~fmp_data.intelligence.models.StockGradesConsensus` --  the same
            strongBuy/buy/hold/sell/strongSell tally under a different model,
            without this model's derived ``consensus`` label.
        """
        return None

    async def get_company_peers(self, symbol: str) -> list[CompanyPeer]:
        """Get company peers"""
        return self._unwrap_list(
            await self.client.request_async(COMPANY_PEERS, symbol=symbol), CompanyPeer
        )

    async def get_mergers_acquisitions_latest(
        self, page: int = 0, limit: int = 100
    ) -> list[MergerAcquisition]:
        """Get latest mergers and acquisitions transactions

        Args:
            page: Page number for pagination (default 0)
            limit: Number of results per page (default 100)

        Returns:
            List of recent M&A transactions
        """
        return self._unwrap_list(
            await self.client.request_async(
                MERGERS_ACQUISITIONS_LATEST, page=page, limit=limit
            ),
            MergerAcquisition,
        )

    async def get_mergers_acquisitions_search(
        self, name: str, page: int = 0, limit: int = 100
    ) -> list[MergerAcquisition]:
        """Search mergers and acquisitions transactions by company name

        Args:
            name: Company name to search for
            page: Page number for pagination (default 0)
            limit: Number of results per page (default 100)

        Returns:
            List of M&A transactions matching the search
        """
        return self._unwrap_list(
            await self.client.request_async(
                MERGERS_ACQUISITIONS_SEARCH, name=name, page=page, limit=limit
            ),
            MergerAcquisition,
        )

    async def get_executive_compensation_benchmark(
        self, year: int
    ) -> list[ExecutiveCompensationBenchmark]:
        """Get executive compensation benchmark data by industry and year

        Args:
            year: Year for compensation data

        Returns:
            List of executive compensation benchmarks by industry
        """
        return self._unwrap_list(
            await self.client.request_async(
                EXECUTIVE_COMPENSATION_BENCHMARK, year=year
            ),
            ExecutiveCompensationBenchmark,
        )

    async def get_historical_prices_light(
        self,
        symbol: str,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> HistoricalData:
        """Get lightweight historical daily price data (open, high, low, close only)

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            HistoricalData object containing the price history
        """
        params: dict[str, str | int] = {"symbol": symbol}
        start_date = _format_date(from_date)
        end_date = _format_date(to_date)
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        rows = self._unwrap_list(
            await self.client.request_async(HISTORICAL_PRICE_LIGHT, **params),
            HistoricalPrice,
        )
        return HistoricalData(symbol=symbol, historical=rows)

    async def get_historical_prices_non_split_adjusted(
        self,
        symbol: str,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> HistoricalData:
        """Get historical daily price data without split adjustments

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            HistoricalData object containing the price history without split adjustments
        """
        params: dict[str, str | int] = {"symbol": symbol}
        start_date = _format_date(from_date)
        end_date = _format_date(to_date)
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        rows = self._unwrap_list(
            await self.client.request_async(
                HISTORICAL_PRICE_NON_SPLIT_ADJUSTED, **params
            ),
            HistoricalPrice,
        )
        return HistoricalData(symbol=symbol, historical=rows)

    async def get_historical_prices_dividend_adjusted(
        self,
        symbol: str,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> HistoricalData:
        """Get historical daily price data adjusted for dividends

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            HistoricalData object containing the dividend-adjusted price history
        """
        params: dict[str, str | int] = {"symbol": symbol}
        start_date = _format_date(from_date)
        end_date = _format_date(to_date)
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        rows = self._unwrap_list(
            await self.client.request_async(
                HISTORICAL_PRICE_DIVIDEND_ADJUSTED, **params
            ),
            HistoricalPrice,
        )
        return HistoricalData(symbol=symbol, historical=rows)

    async def get_dividends(
        self,
        symbol: str,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int | None = None,
    ) -> list[DividendEvent]:
        """Get historical dividend payments for a specific company

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date (optional)
            to_date: End date (optional)
            limit: Number of dividend records to return (optional)

        Returns:
            List of DividendEvent objects containing dividend history
        """
        params: dict[str, str | int] = {"symbol": symbol}
        start_date = _format_date(from_date)
        end_date = _format_date(to_date)
        if start_date:
            params["from_date"] = start_date
        if end_date:
            params["to_date"] = end_date
        if limit is not None:
            params["limit"] = limit
        return self._unwrap_list(
            await self.client.request_async(COMPANY_DIVIDENDS, **params), DividendEvent
        )

    async def get_earnings(self, symbol: str, limit: int = 20) -> list[EarningEvent]:
        """Get historical earnings reports for a specific company

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            limit: Number of earnings reports to return (default: 20)

        Returns:
            List of EarningEvent objects containing earnings history
        """
        return self._unwrap_list(
            await self.client.request_async(
                COMPANY_EARNINGS, symbol=symbol, limit=limit
            ),
            EarningEvent,
        )

    async def get_stock_splits(
        self,
        symbol: str,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int | None = None,
    ) -> list[StockSplitEvent]:
        """Get historical stock split information for a specific company

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date (optional)
            to_date: End date (optional)
            limit: Number of split records to return (optional)

        Returns:
            List of StockSplitEvent objects containing split history
        """
        params: dict[str, str | int] = {"symbol": symbol}
        start_date = _format_date(from_date)
        end_date = _format_date(to_date)
        if start_date:
            params["from_date"] = start_date
        if end_date:
            params["to_date"] = end_date
        if limit is not None:
            params["limit"] = limit
        return self._unwrap_list(
            await self.client.request_async(COMPANY_SPLITS, **params), StockSplitEvent
        )

    # Financial Statement Methods
    async def get_income_statement_ttm(
        self, symbol: str, limit: int | None = None
    ) -> list[IncomeStatement]:
        """Get trailing twelve months (TTM) income statement

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            limit: Number of periods to return

        Returns:
            List of TTM income statement data
        """
        return self._unwrap_list(
            await self.client.request_async(
                INCOME_STATEMENT_TTM, symbol=symbol, limit=limit
            ),
            IncomeStatement,
        )

    async def get_balance_sheet_ttm(
        self, symbol: str, limit: int | None = None
    ) -> list[BalanceSheet]:
        """Get trailing twelve months (TTM) balance sheet

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            limit: Number of periods to return

        Returns:
            List of TTM balance sheet data
        """
        return self._unwrap_list(
            await self.client.request_async(
                BALANCE_SHEET_TTM, symbol=symbol, limit=limit
            ),
            BalanceSheet,
        )

    async def get_cash_flow_ttm(
        self, symbol: str, limit: int | None = None
    ) -> list[CashFlowStatement]:
        """Get trailing twelve months (TTM) cash flow statement

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            limit: Number of periods to return

        Returns:
            List of TTM cash flow data
        """
        return self._unwrap_list(
            await self.client.request_async(CASH_FLOW_TTM, symbol=symbol, limit=limit),
            CashFlowStatement,
        )

    async def get_key_metrics_ttm(self, symbol: str) -> list[KeyMetricsTTM]:
        """Get trailing twelve months (TTM) key financial metrics

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            List of TTM key metrics
        """
        return self._unwrap_list(
            await self.client.request_async(KEY_METRICS_TTM, symbol=symbol),
            KeyMetricsTTM,
        )

    async def get_financial_ratios_ttm(self, symbol: str) -> list[FinancialRatiosTTM]:
        """Get trailing twelve months (TTM) financial ratios

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            List of TTM financial ratios
        """
        return self._unwrap_list(
            await self.client.request_async(FINANCIAL_RATIOS_TTM, symbol=symbol),
            FinancialRatiosTTM,
        )

    async def get_financial_scores(self, symbol: str) -> list[FinancialScore]:
        """Get comprehensive financial health scores

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            List of financial scores including Altman Z-Score and Piotroski Score
        """
        return self._unwrap_list(
            await self.client.request_async(FINANCIAL_SCORES, symbol=symbol),
            FinancialScore,
        )

    async def get_enterprise_values(
        self, symbol: str, period: str = "annual", limit: int = 20
    ) -> list[EnterpriseValue]:
        """Get historical enterprise value data

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual', 'quarter', 'FY', or 'Q1'-'Q4' (default: 'annual')
            limit: Number of periods to return (default: 20)

        Returns:
            List of enterprise value data
        """
        return self._unwrap_list(
            await self.client.request_async(
                ENTERPRISE_VALUES, symbol=symbol, period=period, limit=limit
            ),
            EnterpriseValue,
        )

    async def get_income_statement_growth(
        self, symbol: str, period: str = "annual", limit: int = 20
    ) -> list[FinancialGrowth]:
        """Get year-over-year growth rates for income statement items

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual', 'quarter', 'FY', or 'Q1'-'Q4' (default: 'annual')
            limit: Number of periods to return (default: 20)

        Returns:
            List of income statement growth data
        """
        return self._unwrap_list(
            await self.client.request_async(
                INCOME_STATEMENT_GROWTH, symbol=symbol, period=period, limit=limit
            ),
            FinancialGrowth,
        )

    async def get_balance_sheet_growth(
        self, symbol: str, period: str = "annual", limit: int = 20
    ) -> list[FinancialGrowth]:
        """Get year-over-year growth rates for balance sheet items

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual', 'quarter', 'FY', or 'Q1'-'Q4' (default: 'annual')
            limit: Number of periods to return (default: 20)

        Returns:
            List of balance sheet growth data
        """
        return self._unwrap_list(
            await self.client.request_async(
                BALANCE_SHEET_GROWTH, symbol=symbol, period=period, limit=limit
            ),
            FinancialGrowth,
        )

    async def get_cash_flow_growth(
        self, symbol: str, period: str = "annual", limit: int = 20
    ) -> list[FinancialGrowth]:
        """Get year-over-year growth rates for cash flow items

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual', 'quarter', 'FY', or 'Q1'-'Q4' (default: 'annual')
            limit: Number of periods to return (default: 20)

        Returns:
            List of cash flow growth data
        """
        return self._unwrap_list(
            await self.client.request_async(
                CASH_FLOW_GROWTH, symbol=symbol, period=period, limit=limit
            ),
            FinancialGrowth,
        )

    async def get_financial_growth(
        self, symbol: str, period: str = "annual", limit: int = 20
    ) -> list[FinancialGrowth]:
        """Get comprehensive financial growth metrics

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual', 'quarter', 'FY', or 'Q1'-'Q4' (default: 'annual')
            limit: Number of periods to return (default: 20)

        Returns:
            List of comprehensive financial growth data
        """
        return self._unwrap_list(
            await self.client.request_async(
                FINANCIAL_GROWTH, symbol=symbol, period=period, limit=limit
            ),
            FinancialGrowth,
        )

    async def get_financial_reports_json(
        self, symbol: str, year: int, period: str = "FY"
    ) -> dict:
        """Get Form 10-K financial reports in JSON format

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            year: Report year
            period: Report period - 'FY' or 'Q1'-'Q4' (default: 'FY')

        Returns:
            Dictionary containing financial report data
        """
        params: dict[str, str | int] = {
            "symbol": symbol,
            "year": year,
            "period": period,
        }
        result = await self.client.request_async(FINANCIAL_REPORTS_JSON, **params)
        if isinstance(result, FinancialReportJSON):
            return result.model_dump(mode="json")
        if not isinstance(result, dict):
            raise InvalidResponseTypeError(
                endpoint_name="financial_reports_json",
                expected_type="dict or FinancialReportJSON",
                actual_type=type(result).__name__,
            )
        return result

    async def get_financial_reports_xlsx(
        self, symbol: str, year: int, period: str = "FY"
    ) -> bytes:
        """Get Form 10-K financial reports in Excel format

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            year: Report year
            period: Report period - 'FY' or 'Q1'-'Q4' (default: 'FY')

        Returns:
            Binary data for XLSX file
        """
        params: dict[str, str | int] = {
            "symbol": symbol,
            "year": year,
            "period": period,
        }
        result = await self.client.request_async(FINANCIAL_REPORTS_XLSX, **params)
        if not isinstance(result, bytes | bytearray):
            raise InvalidResponseTypeError(
                endpoint_name="financial_reports_xlsx",
                expected_type="bytes",
                actual_type=type(result).__name__,
            )
        return bytes(result)

    async def get_income_statement_as_reported(
        self, symbol: str, period: str = "annual", limit: int = 10
    ) -> list[AsReportedIncomeStatement]:
        """Get income statement as originally reported

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual' or 'quarter' (default: 'annual')
            limit: Number of periods to return (default: 10)

        Returns:
            List of as-reported income statements
        """
        return self._unwrap_list(
            await self.client.request_async(
                INCOME_STATEMENT_AS_REPORTED, symbol=symbol, period=period, limit=limit
            ),
            AsReportedIncomeStatement,
        )

    async def get_balance_sheet_as_reported(
        self, symbol: str, period: str = "annual", limit: int = 10
    ) -> list[AsReportedBalanceSheet]:
        """Get balance sheet as originally reported

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual' or 'quarter' (default: 'annual')
            limit: Number of periods to return (default: 10)

        Returns:
            List of as-reported balance sheets
        """
        return self._unwrap_list(
            await self.client.request_async(
                BALANCE_SHEET_AS_REPORTED, symbol=symbol, period=period, limit=limit
            ),
            AsReportedBalanceSheet,
        )

    async def get_cash_flow_as_reported(
        self, symbol: str, period: str = "annual", limit: int = 10
    ) -> list[AsReportedCashFlowStatement]:
        """Get cash flow statement as originally reported

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual' or 'quarter' (default: 'annual')
            limit: Number of periods to return (default: 10)

        Returns:
            List of as-reported cash flow statements
        """
        return self._unwrap_list(
            await self.client.request_async(
                CASH_FLOW_AS_REPORTED, symbol=symbol, period=period, limit=limit
            ),
            AsReportedCashFlowStatement,
        )
