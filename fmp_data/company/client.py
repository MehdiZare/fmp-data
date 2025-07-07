# fmp_data/company/client.py
from __future__ import annotations

from typing import cast

from fmp_data.base import EndpointGroup
from fmp_data.company.endpoints import (
    ANALYST_ESTIMATES,
    ANALYST_RECOMMENDATIONS,
    COMPANY_NOTES,
    CORE_INFORMATION,
    EMPLOYEE_COUNT,
    EXECUTIVE_COMPENSATION,
    GEOGRAPHIC_REVENUE_SEGMENTATION,
    HISTORICAL_MARKET_CAP,
    HISTORICAL_PRICE,
    HISTORICAL_SHARE_FLOAT,
    INTRADAY_PRICE,
    KEY_EXECUTIVES,
    MARKET_CAP,
    PRICE_TARGET,
    PRICE_TARGET_CONSENSUS,
    PRICE_TARGET_SUMMARY,
    PRODUCT_REVENUE_SEGMENTATION,
    PROFILE,
    QUOTE,
    SHARE_FLOAT,
    SIMPLE_QUOTE,
    SYMBOL_CHANGES,
    UPGRADES_DOWNGRADES,
    UPGRADES_DOWNGRADES_CONSENSUS,
)
from fmp_data.company.models import (
    AnalystEstimate,
    AnalystRecommendation,
    CompanyCoreInformation,
    CompanyExecutive,
    CompanyNote,
    CompanyProfile,
    EmployeeCount,
    ExecutiveCompensation,
    GeographicRevenueSegment,
    HistoricalData,
    HistoricalShareFloat,
    IntradayPrice,
    PriceTarget,
    PriceTargetConsensus,
    PriceTargetSummary,
    ProductRevenueSegment,
    Quote,
    ShareFloat,
    SimpleQuote,
    SymbolChange,
    UpgradeDowngrade,
    UpgradeDowngradeConsensus,
)
from fmp_data.exceptions import FMPError
from fmp_data.models import MarketCapitalization


class CompanyClient(EndpointGroup):
    """Client for company-related API endpoints"""

    def get_profile(self, symbol: str) -> CompanyProfile:
        result = self.client.request(PROFILE, symbol=symbol)
        if not result:
            raise FMPError(f"Symbol {symbol} not found")
        return cast(CompanyProfile, result[0] if isinstance(result, list) else result)

    def get_core_information(self, symbol: str) -> CompanyCoreInformation:
        """Get core company information"""
        result = self.client.request(CORE_INFORMATION, symbol=symbol)
        return cast(
            CompanyCoreInformation, result[0] if isinstance(result, list) else result
        )

    def get_executives(self, symbol: str) -> list[CompanyExecutive]:
        """Get company executives information"""
        return self.client.request(KEY_EXECUTIVES, symbol=symbol)

    def get_employee_count(self, symbol: str) -> list[EmployeeCount]:
        """Get company employee count history"""
        return self.client.request(EMPLOYEE_COUNT, symbol=symbol)

    def get_company_notes(self, symbol: str) -> list[CompanyNote]:
        """Get company financial notes"""
        return self.client.request(COMPANY_NOTES, symbol=symbol)

    def get_company_logo_url(self, symbol: str) -> str:
        """
        Get company logo URL

        Args:
            symbol: Stock symbol (e.g., AAPL)

        Returns:
            str: URL to company logo
        """
        if not symbol:
            raise ValueError("Symbol is required")

        # Strip any leading/trailing whitespace and convert to uppercase
        symbol = symbol.strip().upper()

        # Remove /api from base URL and construct logo URL
        base_url = self.client.config.base_url.replace("/api", "").replace("site.", "")
        return f"{base_url}/image-stock/{symbol}.png"

    def get_quote(self, symbol: str) -> Quote:
        """Get real-time stock quote"""
        result = self.client.request(QUOTE, symbol=symbol)
        return cast(Quote, result[0] if isinstance(result, list) else result)

    def get_simple_quote(self, symbol: str) -> SimpleQuote:
        """Get simple stock quote"""
        result = self.client.request(SIMPLE_QUOTE, symbol=symbol)
        return cast(SimpleQuote, result[0] if isinstance(result, list) else result)

    def get_historical_prices(
        self,
        symbol: str,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> HistoricalData:
        """Get historical daily price data"""
        result = self.client.request(
            HISTORICAL_PRICE, symbol=symbol, from_=from_date, to=to_date
        )
        return cast(HistoricalData, result)

    def get_intraday_prices(
        self, symbol: str, interval: str = "1min"
    ) -> list[IntradayPrice]:
        """Get intraday price data"""
        return self.client.request(INTRADAY_PRICE, symbol=symbol, interval=interval)

    def get_executive_compensation(self, symbol: str) -> list[ExecutiveCompensation]:
        """Get executive compensation data for a company"""
        return self.client.request(EXECUTIVE_COMPENSATION, symbol=symbol)

    def get_historical_share_float(self, symbol: str) -> list[HistoricalShareFloat]:
        """Get historical share float data for a company"""
        return self.client.request(HISTORICAL_SHARE_FLOAT, symbol=symbol)

    def get_product_revenue_segmentation(
        self, symbol: str, period: str = "annual"
    ) -> list[ProductRevenueSegment]:
        """Get revenue segmentation by product.

        Args:
            symbol: Company symbol
            period: Data period ('annual' or 'quarter')

        Returns:
            List of product revenue segments by fiscal year
        """
        return self.client.request(
            PRODUCT_REVENUE_SEGMENTATION,
            symbol=symbol,
            structure="flat",
            period=period,
        )

    def get_geographic_revenue_segmentation(
        self, symbol: str
    ) -> list[GeographicRevenueSegment]:
        """Get revenue segmentation by geographic region.

        Args:
            symbol: Company symbol

        Returns:
            List of geographic revenue segments by fiscal year
        """
        return self.client.request(
            GEOGRAPHIC_REVENUE_SEGMENTATION,
            symbol=symbol,
            structure="flat",
        )

    def get_symbol_changes(self) -> list[SymbolChange]:
        """Get symbol change history"""
        return self.client.request(SYMBOL_CHANGES)

    def get_share_float(self, symbol: str) -> ShareFloat:
        """Get current share float data for a company"""
        result = self.client.request(SHARE_FLOAT, symbol=symbol)
        return cast(ShareFloat, result[0] if isinstance(result, list) else result)

    def get_market_cap(self, symbol: str) -> MarketCapitalization:
        """Get market capitalization data"""
        result = self.client.request(MARKET_CAP, symbol=symbol)
        return cast(
            MarketCapitalization, result[0] if isinstance(result, list) else result
        )

    def get_historical_market_cap(self, symbol: str) -> list[MarketCapitalization]:
        """Get historical market capitalization data"""
        return self.client.request(HISTORICAL_MARKET_CAP, symbol=symbol)

    def get_price_target(self, symbol: str) -> list[PriceTarget]:
        """Get price targets"""
        return self.client.request(PRICE_TARGET, symbol=symbol)

    def get_price_target_summary(self, symbol: str) -> PriceTargetSummary:
        """Get price target summary"""
        result = self.client.request(PRICE_TARGET_SUMMARY, symbol=symbol)
        return cast(
            PriceTargetSummary, result[0] if isinstance(result, list) else result
        )

    def get_price_target_consensus(self, symbol: str) -> PriceTargetConsensus:
        """Get price target consensus"""
        result = self.client.request(PRICE_TARGET_CONSENSUS, symbol=symbol)
        return cast(
            PriceTargetConsensus, result[0] if isinstance(result, list) else result
        )

    def get_analyst_estimates(self, symbol: str) -> list[AnalystEstimate]:
        """Get analyst estimates"""
        return self.client.request(ANALYST_ESTIMATES, symbol=symbol)

    def get_analyst_recommendations(self, symbol: str) -> list[AnalystRecommendation]:
        """Get analyst recommendations"""
        return self.client.request(ANALYST_RECOMMENDATIONS, symbol=symbol)

    def get_upgrades_downgrades(self, symbol: str) -> list[UpgradeDowngrade]:
        """Get upgrades and downgrades"""
        return self.client.request(UPGRADES_DOWNGRADES, symbol=symbol)

    def get_upgrades_downgrades_consensus(
        self, symbol: str
    ) -> UpgradeDowngradeConsensus:
        """Get upgrades and downgrades consensus"""
        result = self.client.request(UPGRADES_DOWNGRADES_CONSENSUS, symbol=symbol)
        return cast(
            UpgradeDowngradeConsensus, result[0] if isinstance(result, list) else result
        )
