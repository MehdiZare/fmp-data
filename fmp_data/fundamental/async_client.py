# fmp_data/fundamental/async_client.py
"""Async client for fundamental analysis endpoints."""

from fmp_data.base import AsyncEndpointGroup
from fmp_data.fundamental import endpoints
from fmp_data.fundamental.models import (
    DCF,
    BalanceSheet,
    CashFlowStatement,
    CustomDCF,
    CustomLeveredDCF,
    FinancialRatios,
    FinancialReportDate,
    FinancialStatementFull,
    HistoricalRating,
    IncomeStatement,
    KeyMetrics,
    LatestFinancialStatement,
    LeveredDCF,
    OwnerEarnings,
)
from fmp_data.helpers import deprecated
from fmp_data.schema import Period


class AsyncFundamentalClient(AsyncEndpointGroup):
    """Async client for fundamental analysis endpoints."""

    async def get_income_statement(
        self, symbol: str, period: Period = "annual", limit: int | None = None
    ) -> list[IncomeStatement]:
        """Get income statements"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.INCOME_STATEMENT, symbol=symbol, period=period, limit=limit
            ),
            IncomeStatement,
        )

    async def get_balance_sheet(
        self, symbol: str, period: Period = "annual", limit: int | None = None
    ) -> list[BalanceSheet]:
        """Get balance sheets"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.BALANCE_SHEET, symbol=symbol, period=period, limit=limit
            ),
            BalanceSheet,
        )

    async def get_cash_flow(
        self, symbol: str, period: Period = "annual", limit: int | None = None
    ) -> list[CashFlowStatement]:
        """Get cash flow statements"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.CASH_FLOW, symbol=symbol, period=period, limit=limit
            ),
            CashFlowStatement,
        )

    async def get_latest_financial_statements(
        self, page: int = 0, limit: int = 250
    ) -> list[LatestFinancialStatement]:
        """Get latest financial statement metadata across symbols"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.LATEST_FINANCIAL_STATEMENTS, page=page, limit=limit
            ),
            LatestFinancialStatement,
        )

    async def get_key_metrics(
        self, symbol: str, period: Period = "annual", limit: int | None = None
    ) -> list[KeyMetrics]:
        """Get key financial metrics"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.KEY_METRICS, symbol=symbol, period=period, limit=limit
            ),
            KeyMetrics,
        )

    async def get_financial_ratios(
        self, symbol: str, period: Period = "annual", limit: int | None = None
    ) -> list[FinancialRatios]:
        """Get financial ratios"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.FINANCIAL_RATIOS, symbol=symbol, period=period, limit=limit
            ),
            FinancialRatios,
        )

    async def get_full_financial_statement(
        self, symbol: str, period: Period = "annual", limit: int | None = None
    ) -> list[FinancialStatementFull]:
        """Get full financial statements as reported"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.FULL_FINANCIAL_STATEMENT,
                symbol=symbol,
                period=period,
                limit=limit,
            ),
            FinancialStatementFull,
        )

    async def get_financial_reports_dates(
        self, symbol: str
    ) -> list[FinancialReportDate]:
        """Get list of financial reports dates"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.FINANCIAL_REPORTS_DATES, symbol=symbol
            ),
            FinancialReportDate,
        )

    async def get_owner_earnings(
        self, symbol: str, limit: int | None = None
    ) -> list[OwnerEarnings]:
        """Get owner earnings metrics"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.OWNER_EARNINGS, symbol=symbol, limit=limit
            ),
            OwnerEarnings,
        )

    async def get_levered_dcf(self, symbol: str) -> list[LeveredDCF]:
        """Get levered DCF valuation"""
        return self._unwrap_list(
            await self.client.request_async(endpoints.LEVERED_DCF, symbol=symbol),
            LeveredDCF,
        )

    @deprecated(
        "historical-rating is dead. The live path ratings-historical is "
        "already shipped as FMPDataClient.intelligence.get_ratings_historical"
        "(symbol); this method is a leftover declaration. The scoring fields "
        "differ -- overallScore and per-metric scores, not ratingScore."
    )
    async def get_historical_rating(self, symbol: str) -> list[HistoricalRating]:
        """Get historical company ratings

        .. deprecated::
            ``historical-rating`` 404s and will be removed in a future
            version. It currently returns an empty list. Use
            ``client.intelligence.get_ratings_historical(symbol)``, which
            serves the live ``ratings-historical``. It is not a drop-in: that
            payload carries ``overallScore`` plus per-metric scores
            (``discountedCashFlowScore``, ``returnOnEquityScore``, …) where
            this model declared ``ratingScore``, ``ratingDetails`` and
            ``ratingRecommendation``.
        """
        return []

    async def get_discounted_cash_flow(self, symbol: str) -> list[DCF]:
        """Get discounted cash flow valuation"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.DISCOUNTED_CASH_FLOW, symbol=symbol
            ),
            DCF,
        )

    async def get_custom_discounted_cash_flow(
        self,
        symbol: str,
        *,
        revenue_growth_pct: float | None = None,
        ebitda_pct: float | None = None,
        depreciation_and_amortization_pct: float | None = None,
        cash_and_short_term_investments_pct: float | None = None,
        receivables_pct: float | None = None,
        inventories_pct: float | None = None,
        payable_pct: float | None = None,
        ebit_pct: float | None = None,
        capital_expenditure_pct: float | None = None,
        operating_cash_flow_pct: float | None = None,
        selling_general_and_administrative_expenses_pct: float | None = None,
        tax_rate: float | None = None,
        long_term_growth_rate: float | None = None,
        cost_of_debt: float | None = None,
        cost_of_equity: float | None = None,
        market_risk_premium: float | None = None,
        beta: float | None = None,
        risk_free_rate: float | None = None,
    ) -> list[CustomDCF]:
        """Get advanced DCF analysis with detailed projections

        New keyword-only filters are omitted when None, preserving the existing
        request.

        Args:
            symbol: Ticker symbol identifying the requested instrument.
            revenue_growth_pct: Revenue growth pct assumption passed to FMP for the
                custom DCF calculation.
            ebitda_pct: Ebitda pct assumption passed to FMP for the custom DCF
                calculation.
            depreciation_and_amortization_pct: Depreciation and amortization pct
                assumption passed to FMP for the custom DCF calculation.
            cash_and_short_term_investments_pct: Cash and short term investments pct
                assumption passed to FMP for the custom DCF calculation.
            receivables_pct: Receivables pct assumption passed to FMP for the custom
                DCF calculation.
            inventories_pct: Inventories pct assumption passed to FMP for the custom
                DCF calculation.
            payable_pct: Payable pct assumption passed to FMP for the custom DCF
                calculation.
            ebit_pct: Ebit pct assumption passed to FMP for the custom DCF
                calculation.
            capital_expenditure_pct: Capital expenditure pct assumption passed to
                FMP for the custom DCF calculation.
            operating_cash_flow_pct: Operating cash flow pct assumption passed to
                FMP for the custom DCF calculation.
            selling_general_and_administrative_expenses_pct: Selling general and
                administrative expenses pct assumption passed to FMP for the custom
                DCF calculation.
            tax_rate: Tax rate assumption passed to FMP for the custom DCF
                calculation.
            long_term_growth_rate: Long term growth rate assumption passed to FMP
                for the custom DCF calculation.
            cost_of_debt: Cost of debt assumption passed to FMP for the custom DCF
                calculation.
            cost_of_equity: Cost of equity assumption passed to FMP for the custom
                DCF calculation.
            market_risk_premium: Market risk premium assumption passed to FMP for
                the custom DCF calculation.
            beta: Beta assumption passed to FMP for the custom DCF calculation.
            risk_free_rate: Risk free rate assumption passed to FMP for the custom
                DCF calculation.

        Returns:
            list[CustomDCF]: Parsed provider records.

        Example:
            records = await client.fundamental.get_custom_discounted_cash_flow(
                'MSFT', risk_free_rate=3.5
            )
        """
        optional_params = {
            "revenue_growth_pct": revenue_growth_pct,
            "ebitda_pct": ebitda_pct,
            "depreciation_and_amortization_pct": depreciation_and_amortization_pct,
            "cash_and_short_term_investments_pct": cash_and_short_term_investments_pct,
            "receivables_pct": receivables_pct,
            "inventories_pct": inventories_pct,
            "payable_pct": payable_pct,
            "ebit_pct": ebit_pct,
            "capital_expenditure_pct": capital_expenditure_pct,
            "operating_cash_flow_pct": operating_cash_flow_pct,
            "selling_general_and_administrative_expenses_pct": (
                selling_general_and_administrative_expenses_pct
            ),
            "tax_rate": tax_rate,
            "long_term_growth_rate": long_term_growth_rate,
            "cost_of_debt": cost_of_debt,
            "cost_of_equity": cost_of_equity,
            "market_risk_premium": market_risk_premium,
            "beta": beta,
            "risk_free_rate": risk_free_rate,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.CUSTOM_DISCOUNTED_CASH_FLOW, symbol=symbol, **optional_params
            ),
            CustomDCF,
        )

    async def get_custom_levered_dcf(
        self,
        symbol: str,
        *,
        revenue_growth_pct: float | None = None,
        ebitda_pct: float | None = None,
        depreciation_and_amortization_pct: float | None = None,
        cash_and_short_term_investments_pct: float | None = None,
        receivables_pct: float | None = None,
        inventories_pct: float | None = None,
        payable_pct: float | None = None,
        ebit_pct: float | None = None,
        capital_expenditure_pct: float | None = None,
        operating_cash_flow_pct: float | None = None,
        selling_general_and_administrative_expenses_pct: float | None = None,
        tax_rate: float | None = None,
        long_term_growth_rate: float | None = None,
        cost_of_debt: float | None = None,
        cost_of_equity: float | None = None,
        market_risk_premium: float | None = None,
        beta: float | None = None,
        risk_free_rate: float | None = None,
    ) -> list[CustomLeveredDCF]:
        """Get levered DCF analysis using FCFE

        New keyword-only filters are omitted when None, preserving the existing
        request.

        Args:
            symbol: Ticker symbol identifying the requested instrument.
            revenue_growth_pct: Revenue growth pct assumption passed to FMP for the
                custom DCF calculation.
            ebitda_pct: Ebitda pct assumption passed to FMP for the custom DCF
                calculation.
            depreciation_and_amortization_pct: Depreciation and amortization pct
                assumption passed to FMP for the custom DCF calculation.
            cash_and_short_term_investments_pct: Cash and short term investments pct
                assumption passed to FMP for the custom DCF calculation.
            receivables_pct: Receivables pct assumption passed to FMP for the custom
                DCF calculation.
            inventories_pct: Inventories pct assumption passed to FMP for the custom
                DCF calculation.
            payable_pct: Payable pct assumption passed to FMP for the custom DCF
                calculation.
            ebit_pct: Ebit pct assumption passed to FMP for the custom DCF
                calculation.
            capital_expenditure_pct: Capital expenditure pct assumption passed to
                FMP for the custom DCF calculation.
            operating_cash_flow_pct: Operating cash flow pct assumption passed to
                FMP for the custom DCF calculation.
            selling_general_and_administrative_expenses_pct: Selling general and
                administrative expenses pct assumption passed to FMP for the custom
                DCF calculation.
            tax_rate: Tax rate assumption passed to FMP for the custom DCF
                calculation.
            long_term_growth_rate: Long term growth rate assumption passed to FMP
                for the custom DCF calculation.
            cost_of_debt: Cost of debt assumption passed to FMP for the custom DCF
                calculation.
            cost_of_equity: Cost of equity assumption passed to FMP for the custom
                DCF calculation.
            market_risk_premium: Market risk premium assumption passed to FMP for
                the custom DCF calculation.
            beta: Beta assumption passed to FMP for the custom DCF calculation.
            risk_free_rate: Risk free rate assumption passed to FMP for the custom
                DCF calculation.

        Returns:
            list[CustomLeveredDCF]: Parsed provider records.

        Example:
            records = await client.fundamental.get_custom_levered_dcf(
                'MSFT', risk_free_rate=3.5
            )
        """
        optional_params = {
            "revenue_growth_pct": revenue_growth_pct,
            "ebitda_pct": ebitda_pct,
            "depreciation_and_amortization_pct": depreciation_and_amortization_pct,
            "cash_and_short_term_investments_pct": cash_and_short_term_investments_pct,
            "receivables_pct": receivables_pct,
            "inventories_pct": inventories_pct,
            "payable_pct": payable_pct,
            "ebit_pct": ebit_pct,
            "capital_expenditure_pct": capital_expenditure_pct,
            "operating_cash_flow_pct": operating_cash_flow_pct,
            "selling_general_and_administrative_expenses_pct": (
                selling_general_and_administrative_expenses_pct
            ),
            "tax_rate": tax_rate,
            "long_term_growth_rate": long_term_growth_rate,
            "cost_of_debt": cost_of_debt,
            "cost_of_equity": cost_of_equity,
            "market_risk_premium": market_risk_premium,
            "beta": beta,
            "risk_free_rate": risk_free_rate,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.CUSTOM_LEVERED_DCF, symbol=symbol, **optional_params
            ),
            CustomLeveredDCF,
        )
