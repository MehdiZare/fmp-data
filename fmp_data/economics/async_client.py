# fmp_data/economics/async_client.py
"""Async client for economics data endpoints."""

from datetime import date

from fmp_data.base import AsyncEndpointGroup
from fmp_data.economics.endpoints import (
    COMMITMENT_OF_TRADERS_ANALYSIS,
    COMMITMENT_OF_TRADERS_LIST,
    COMMITMENT_OF_TRADERS_REPORT,
    ECONOMIC_CALENDAR,
    ECONOMIC_INDICATORS,
    MARKET_RISK_PREMIUM,
    TREASURY_RATES,
)
from fmp_data.economics.models import (
    CommitmentOfTradersAnalysis,
    CommitmentOfTradersListItem,
    CommitmentOfTradersReport,
    EconomicEvent,
    EconomicIndicator,
    MarketRiskPremium,
    TreasuryRate,
)
from fmp_data.economics.schema import EconomicIndicatorType


class AsyncEconomicsClient(AsyncEndpointGroup):
    """Async client for economics data endpoints."""

    async def get_treasury_rates(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[TreasuryRate]:
        """Get treasury rates"""
        params: dict[str, str] = {}
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y-%m-%d")

        return self._unwrap_list(
            await self.client.request_async(TREASURY_RATES, **params), TreasuryRate
        )

    async def get_economic_indicators(
        self,
        indicator_name: EconomicIndicatorType | str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[EconomicIndicator]:
        """Get economic indicator data

        New keyword-only filters are omitted when None, preserving the existing
        request.

        Args:
            indicator_name: FMP economic indicator name, for example "GDP".
            start_date: Start date passed to FMP; boundary semantics depend on the
                endpoint.
            end_date: End date passed to FMP; boundary semantics depend on the
                endpoint.

        Returns:
            list[EconomicIndicator]: Parsed provider records.

        Example:
            from datetime import date
            records = await client.economics.get_economic_indicators(
                'GDP', start_date=date(2026, 9, 10)
            )
        """
        optional_params = {
            "start_date": start_date,
            "end_date": end_date,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        return self._unwrap_list(
            await self.client.request_async(
                ECONOMIC_INDICATORS, name=indicator_name, **optional_params
            ),
            EconomicIndicator,
        )

    async def get_economic_calendar(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        *,
        country: str | None = None,
    ) -> list[EconomicEvent]:
        """Get economic calendar events

        New keyword-only filters are omitted when None, preserving the existing
        request.

        Args:
            start_date: Start date passed to FMP; omitted when None.
            end_date: End date passed to FMP; omitted when None.
            country: Country filter using the provider country code (for example US
                or UK).

        Returns:
            list[EconomicEvent]: Parsed provider records.

        Example:
            records = await client.economics.get_economic_calendar(
                country='US'
            )
        """
        optional_params = {
            "country": country,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        params: dict[str, str] = {}
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y-%m-%d")

        return self._unwrap_list(
            await self.client.request_async(
                ECONOMIC_CALENDAR, **params, **optional_params
            ),
            EconomicEvent,
        )

    async def get_market_risk_premium(self) -> list[MarketRiskPremium]:
        """Get market risk premium data"""
        return self._unwrap_list(
            await self.client.request_async(MARKET_RISK_PREMIUM), MarketRiskPremium
        )

    async def get_commitment_of_traders_report(
        self, symbol: str, start_date: date, end_date: date
    ) -> list[CommitmentOfTradersReport]:
        """Get Commitment of Traders (COT) report data"""
        params = {
            "symbol": symbol,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }
        return self._unwrap_list(
            await self.client.request_async(COMMITMENT_OF_TRADERS_REPORT, **params),
            CommitmentOfTradersReport,
        )

    async def get_commitment_of_traders_analysis(
        self, symbol: str, start_date: date, end_date: date
    ) -> list[CommitmentOfTradersAnalysis]:
        """Get Commitment of Traders (COT) analysis data"""
        params = {
            "symbol": symbol,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }
        return self._unwrap_list(
            await self.client.request_async(COMMITMENT_OF_TRADERS_ANALYSIS, **params),
            CommitmentOfTradersAnalysis,
        )

    async def get_commitment_of_traders_list(
        self,
    ) -> list[CommitmentOfTradersListItem]:
        """Get list of available Commitment of Traders (COT) symbols"""
        return self._unwrap_list(
            await self.client.request_async(COMMITMENT_OF_TRADERS_LIST),
            CommitmentOfTradersListItem,
        )
