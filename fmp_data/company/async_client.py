# fmp_data/company/async_client.py
"""Async client for company-related API endpoints.

This is the async counterpart to CompanyClient. All methods are async
and have the same names as their sync equivalents (no _async suffix).
"""
from __future__ import annotations

from typing import cast

from fmp_data.base import AsyncEndpointGroup
from fmp_data.company.endpoints import (
    AFTERMARKET_QUOTE,
    AFTERMARKET_TRADE,
    ANALYST_ESTIMATES,
    ANALYST_RECOMMENDATIONS,
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
    CORE_INFORMATION,
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
    HISTORICAL_SHARE_FLOAT,
    INCOME_STATEMENT_AS_REPORTED,
    INCOME_STATEMENT_GROWTH,
    INCOME_STATEMENT_TTM,
    INTRADAY_PRICE,
    KEY_EXECUTIVES,
    KEY_METRICS_TTM,
    MARKET_CAP,
    MERGERS_ACQUISITIONS_LATEST,
    MERGERS_ACQUISITIONS_SEARCH,
    PRICE_TARGET,
    PRICE_TARGET_CONSENSUS,
    PRICE_TARGET_SUMMARY,
    PRODUCT_REVENUE_SEGMENTATION,
    PROFILE,
    QUOTE,
    SHARE_FLOAT,
    SIMPLE_QUOTE,
    STOCK_PRICE_CHANGE,
    SYMBOL_CHANGES,
    UPGRADES_DOWNGRADES,
    UPGRADES_DOWNGRADES_CONSENSUS,
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
    EmployeeCount,
    ExecutiveCompensation,
    ExecutiveCompensationBenchmark,
    GeographicRevenueSegment,
    HistoricalData,
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
from fmp_data.exceptions import FMPError, ValidationError
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
from fmp_data.intelligence.models import DividendEvent, EarningEvent, StockSplitEvent
from fmp_data.models import MarketCapitalization


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
            raise FMPError(f"Symbol {symbol} not found")
        return profile

    async def get_core_information(self, symbol: str) -> CompanyCoreInformation | None:
        """Get core company information"""
        result = await self.client.request_async(CORE_INFORMATION, symbol=symbol)
        return self._unwrap_single(result, CompanyCoreInformation, allow_none=True)

    async def get_executives(self, symbol: str) -> list[CompanyExecutive]:
        """Get company executives information"""
        return await self.client.request_async(KEY_EXECUTIVES, symbol=symbol)

    async def get_employee_count(self, symbol: str) -> list[EmployeeCount]:
        """Get company employee count history"""
        return await self.client.request_async(EMPLOYEE_COUNT, symbol=symbol)

    async def get_company_notes(self, symbol: str) -> list[CompanyNote]:
        """Get company financial notes"""
        return await self.client.request_async(COMPANY_NOTES, symbol=symbol)

    def get_company_logo_url(self, symbol: str) -> str:
        """Get the company logo URL (sync, no API call needed)"""
        if not symbol or not symbol.strip():
            raise ValueError("Symbol is required for company logo URL")
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
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> HistoricalData:
        """Get historical daily price data

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date in YYYY-MM-DD format (optional)
            to_date: End date in YYYY-MM-DD format (optional)

        Returns:
            HistoricalData object containing the price history
        """
        params = {"symbol": symbol}
        if from_date:
            params["start_date"] = from_date
        if to_date:
            params["end_date"] = to_date

        result = await self.client.request_async(HISTORICAL_PRICE, **params)

        if isinstance(result, list):
            return HistoricalData(symbol=symbol, historical=result)
        else:
            return HistoricalData(symbol=symbol, historical=[result])

    async def get_intraday_prices(
        self, symbol: str, interval: str = "1min"
    ) -> list[IntradayPrice]:
        """Get intraday price data"""
        return await self.client.request_async(
            INTRADAY_PRICE, symbol=symbol, interval=interval
        )

    async def get_executive_compensation(
        self, symbol: str
    ) -> list[ExecutiveCompensation]:
        """Get executive compensation data for a company"""
        return await self.client.request_async(EXECUTIVE_COMPENSATION, symbol=symbol)

    async def get_historical_share_float(
        self, symbol: str
    ) -> list[HistoricalShareFloat]:
        """Get historical share float data for a company"""
        return await self.client.request_async(HISTORICAL_SHARE_FLOAT, symbol=symbol)

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
        return await self.client.request_async(
            PRODUCT_REVENUE_SEGMENTATION,
            symbol=symbol,
            structure="flat",
            period=period,
        )

    async def get_geographic_revenue_segmentation(
        self, symbol: str
    ) -> list[GeographicRevenueSegment]:
        """Get revenue segmentation by geographic region.

        Args:
            symbol: Company symbol

        Returns:
            List of geographic revenue segments by fiscal year
        """
        return await self.client.request_async(
            GEOGRAPHIC_REVENUE_SEGMENTATION,
            symbol=symbol,
            structure="flat",
        )

    async def get_symbol_changes(self) -> list[SymbolChange]:
        """Get symbol change history"""
        return await self.client.request_async(SYMBOL_CHANGES)

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
        return await self.client.request_async(HISTORICAL_MARKET_CAP, symbol=symbol)

    async def get_price_target(self, symbol: str) -> list[PriceTarget]:
        """Get price targets"""
        return await self.client.request_async(PRICE_TARGET, symbol=symbol)

    async def get_price_target_summary(self, symbol: str) -> PriceTargetSummary:
        """Get price target summary"""
        result = await self.client.request_async(PRICE_TARGET_SUMMARY, symbol=symbol)
        return self._unwrap_single(result, PriceTargetSummary)

    async def get_price_target_consensus(self, symbol: str) -> PriceTargetConsensus:
        """Get price target consensus"""
        result = await self.client.request_async(PRICE_TARGET_CONSENSUS, symbol=symbol)
        return self._unwrap_single(result, PriceTargetConsensus)

    async def get_analyst_estimates(self, symbol: str) -> list[AnalystEstimate]:
        """Get analyst estimates"""
        try:
            return await self.client.request_async(ANALYST_ESTIMATES, symbol=symbol)
        except ValidationError as exc:
            if "period" in str(exc):
                return []
            raise

    async def get_analyst_recommendations(
        self, symbol: str
    ) -> list[AnalystRecommendation]:
        """Get analyst recommendations"""
        return await self.client.request_async(ANALYST_RECOMMENDATIONS, symbol=symbol)

    async def get_upgrades_downgrades(self, symbol: str) -> list[UpgradeDowngrade]:
        """Get upgrades and downgrades"""
        return await self.client.request_async(UPGRADES_DOWNGRADES, symbol=symbol)

    async def get_upgrades_downgrades_consensus(
        self, symbol: str
    ) -> UpgradeDowngradeConsensus | None:
        """Get upgrades and downgrades consensus"""
        result = await self.client.request_async(
            UPGRADES_DOWNGRADES_CONSENSUS, symbol=symbol
        )
        if isinstance(result, list):
            if not result:
                return None
            return cast(UpgradeDowngradeConsensus, result[0])
        return cast(UpgradeDowngradeConsensus, result)

    async def get_company_peers(self, symbol: str) -> list[CompanyPeer]:
        """Get company peers"""
        return await self.client.request_async(COMPANY_PEERS, symbol=symbol)

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
        return await self.client.request_async(
            MERGERS_ACQUISITIONS_LATEST, page=page, limit=limit
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
        return await self.client.request_async(
            MERGERS_ACQUISITIONS_SEARCH, name=name, page=page, limit=limit
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
        return await self.client.request_async(
            EXECUTIVE_COMPENSATION_BENCHMARK, year=year
        )

    async def get_historical_prices_light(
        self,
        symbol: str,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> HistoricalData:
        """Get lightweight historical daily price data (open, high, low, close only)

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date in YYYY-MM-DD format (optional)
            to_date: End date in YYYY-MM-DD format (optional)

        Returns:
            HistoricalData object containing the price history
        """
        params = {"symbol": symbol}
        if from_date:
            params["start_date"] = from_date
        if to_date:
            params["end_date"] = to_date

        result = await self.client.request_async(HISTORICAL_PRICE_LIGHT, **params)

        if isinstance(result, list):
            return HistoricalData(symbol=symbol, historical=result)
        else:
            return HistoricalData(symbol=symbol, historical=[result])

    async def get_historical_prices_non_split_adjusted(
        self,
        symbol: str,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> HistoricalData:
        """Get historical daily price data without split adjustments

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date in YYYY-MM-DD format (optional)
            to_date: End date in YYYY-MM-DD format (optional)

        Returns:
            HistoricalData object containing the price history without split adjustments
        """
        params = {"symbol": symbol}
        if from_date:
            params["start_date"] = from_date
        if to_date:
            params["end_date"] = to_date

        result = await self.client.request_async(
            HISTORICAL_PRICE_NON_SPLIT_ADJUSTED, **params
        )

        if isinstance(result, list):
            return HistoricalData(symbol=symbol, historical=result)
        else:
            return HistoricalData(symbol=symbol, historical=[result])

    async def get_historical_prices_dividend_adjusted(
        self,
        symbol: str,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> HistoricalData:
        """Get historical daily price data adjusted for dividends

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date in YYYY-MM-DD format (optional)
            to_date: End date in YYYY-MM-DD format (optional)

        Returns:
            HistoricalData object containing the dividend-adjusted price history
        """
        params = {"symbol": symbol}
        if from_date:
            params["start_date"] = from_date
        if to_date:
            params["end_date"] = to_date

        result = await self.client.request_async(
            HISTORICAL_PRICE_DIVIDEND_ADJUSTED, **params
        )

        if isinstance(result, list):
            return HistoricalData(symbol=symbol, historical=result)
        else:
            return HistoricalData(symbol=symbol, historical=[result])

    async def get_dividends(
        self, symbol: str, from_date: str | None = None, to_date: str | None = None
    ) -> list[DividendEvent]:
        """Get historical dividend payments for a specific company

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date in YYYY-MM-DD format (optional)
            to_date: End date in YYYY-MM-DD format (optional)

        Returns:
            List of DividendEvent objects containing dividend history
        """
        params = {"symbol": symbol}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        return await self.client.request_async(COMPANY_DIVIDENDS, **params)

    async def get_earnings(self, symbol: str, limit: int = 20) -> list[EarningEvent]:
        """Get historical earnings reports for a specific company

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            limit: Number of earnings reports to return (default: 20)

        Returns:
            List of EarningEvent objects containing earnings history
        """
        return await self.client.request_async(
            COMPANY_EARNINGS, symbol=symbol, limit=limit
        )

    async def get_stock_splits(
        self, symbol: str, from_date: str | None = None, to_date: str | None = None
    ) -> list[StockSplitEvent]:
        """Get historical stock split information for a specific company

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date in YYYY-MM-DD format (optional)
            to_date: End date in YYYY-MM-DD format (optional)

        Returns:
            List of StockSplitEvent objects containing split history
        """
        params = {"symbol": symbol}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        return await self.client.request_async(COMPANY_SPLITS, **params)

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
        return await self.client.request_async(
            INCOME_STATEMENT_TTM, symbol=symbol, limit=limit
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
        return await self.client.request_async(
            BALANCE_SHEET_TTM, symbol=symbol, limit=limit
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
        return await self.client.request_async(
            CASH_FLOW_TTM, symbol=symbol, limit=limit
        )

    async def get_key_metrics_ttm(self, symbol: str) -> list[KeyMetricsTTM]:
        """Get trailing twelve months (TTM) key financial metrics

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            List of TTM key metrics
        """
        return await self.client.request_async(KEY_METRICS_TTM, symbol=symbol)

    async def get_financial_ratios_ttm(self, symbol: str) -> list[FinancialRatiosTTM]:
        """Get trailing twelve months (TTM) financial ratios

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            List of TTM financial ratios
        """
        return await self.client.request_async(FINANCIAL_RATIOS_TTM, symbol=symbol)

    async def get_financial_scores(self, symbol: str) -> list[FinancialScore]:
        """Get comprehensive financial health scores

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            List of financial scores including Altman Z-Score and Piotroski Score
        """
        return await self.client.request_async(FINANCIAL_SCORES, symbol=symbol)

    async def get_enterprise_values(
        self, symbol: str, period: str = "annual", limit: int = 20
    ) -> list[EnterpriseValue]:
        """Get historical enterprise value data

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual' or 'quarter' (default: 'annual')
            limit: Number of periods to return (default: 20)

        Returns:
            List of enterprise value data
        """
        return await self.client.request_async(
            ENTERPRISE_VALUES, symbol=symbol, period=period, limit=limit
        )

    async def get_income_statement_growth(
        self, symbol: str, period: str = "annual", limit: int = 20
    ) -> list[FinancialGrowth]:
        """Get year-over-year growth rates for income statement items

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual' or 'quarter' (default: 'annual')
            limit: Number of periods to return (default: 20)

        Returns:
            List of income statement growth data
        """
        return await self.client.request_async(
            INCOME_STATEMENT_GROWTH, symbol=symbol, period=period, limit=limit
        )

    async def get_balance_sheet_growth(
        self, symbol: str, period: str = "annual", limit: int = 20
    ) -> list[FinancialGrowth]:
        """Get year-over-year growth rates for balance sheet items

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual' or 'quarter' (default: 'annual')
            limit: Number of periods to return (default: 20)

        Returns:
            List of balance sheet growth data
        """
        return await self.client.request_async(
            BALANCE_SHEET_GROWTH, symbol=symbol, period=period, limit=limit
        )

    async def get_cash_flow_growth(
        self, symbol: str, period: str = "annual", limit: int = 20
    ) -> list[FinancialGrowth]:
        """Get year-over-year growth rates for cash flow items

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual' or 'quarter' (default: 'annual')
            limit: Number of periods to return (default: 20)

        Returns:
            List of cash flow growth data
        """
        return await self.client.request_async(
            CASH_FLOW_GROWTH, symbol=symbol, period=period, limit=limit
        )

    async def get_financial_growth(
        self, symbol: str, period: str = "annual", limit: int = 20
    ) -> list[FinancialGrowth]:
        """Get comprehensive financial growth metrics

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual' or 'quarter' (default: 'annual')
            limit: Number of periods to return (default: 20)

        Returns:
            List of comprehensive financial growth data
        """
        return await self.client.request_async(
            FINANCIAL_GROWTH, symbol=symbol, period=period, limit=limit
        )

    async def get_financial_reports_json(
        self, symbol: str, year: int | None = None, period: str = "FY"
    ) -> dict:
        """Get Form 10-K financial reports in JSON format

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            year: Report year (optional)
            period: Report period - 'FY' or 'Q1'-'Q4' (default: 'FY')

        Returns:
            Dictionary containing financial report data
        """
        params: dict[str, str | int] = {"symbol": symbol, "period": period}
        if year:
            params["year"] = year
        result = await self.client.request_async(FINANCIAL_REPORTS_JSON, **params)
        return cast(dict, result)

    async def get_financial_reports_xlsx(
        self, symbol: str, year: int | None = None, period: str = "FY"
    ) -> bytes:
        """Get Form 10-K financial reports in Excel format

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            year: Report year (optional)
            period: Report period - 'FY' or 'Q1'-'Q4' (default: 'FY')

        Returns:
            Binary data for XLSX file
        """
        params: dict[str, str | int] = {"symbol": symbol, "period": period}
        if year:
            params["year"] = year
        result = await self.client.request_async(FINANCIAL_REPORTS_XLSX, **params)
        return cast(bytes, result)

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
        return await self.client.request_async(
            INCOME_STATEMENT_AS_REPORTED, symbol=symbol, period=period, limit=limit
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
        return await self.client.request_async(
            BALANCE_SHEET_AS_REPORTED, symbol=symbol, period=period, limit=limit
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
        return await self.client.request_async(
            CASH_FLOW_AS_REPORTED, symbol=symbol, period=period, limit=limit
        )
