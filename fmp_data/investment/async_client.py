# fmp_data/investment/async_client.py
"""Async client for investment products endpoints."""

from datetime import date
from typing import cast
import warnings

from fmp_data.base import AsyncEndpointGroup
from fmp_data.exceptions import FMPError, ValidationError
from fmp_data.helpers import deprecated
from fmp_data.investment.endpoints import (
    ETF_COUNTRY_WEIGHTINGS,
    ETF_EXPOSURE,
    ETF_HOLDINGS,
    ETF_INFO,
    ETF_SECTOR_WEIGHTINGS,
    FUNDS_DISCLOSURE,
    FUNDS_DISCLOSURE_HOLDERS_LATEST,
    FUNDS_DISCLOSURE_HOLDERS_SEARCH,
    MUTUAL_FUND_DATES,
)
from fmp_data.investment.models import (
    ETFCountryWeighting,
    ETFExposure,
    ETFHolder,
    ETFHolding,
    ETFInfo,
    ETFSectorWeighting,
    FundDisclosureHolderLatest,
    FundDisclosureHolding,
    FundDisclosureSearchResult,
    MutualFundHolder,
    MutualFundHolding,
    PortfolioDate,
)
from fmp_data.logger import FMPLogger

logger = FMPLogger().get_logger(__name__)


class AsyncInvestmentClient(AsyncEndpointGroup):
    """Async client for investment products endpoints."""

    # ETF methods
    async def get_etf_holdings(
        self, symbol: str, holdings_date: date | None = None
    ) -> list[ETFHolding]:
        """Get ETF holdings"""
        params: dict[str, str] = {"symbol": symbol}
        if holdings_date is not None:
            params["date"] = holdings_date.strftime("%Y-%m-%d")
        return self._unwrap_list(
            await self.client.request_async(ETF_HOLDINGS, **params), ETFHolding
        )

    @deprecated(
        "etf/portfolio-dates is dead. The live path funds/disclosure-dates is "
        "already shipped as get_mutual_fund_dates() / "
        "get_fund_disclosure_dates(); this method is a leftover declaration. "
        "Those return a date/year/quarter record rather than a bare date."
    )
    async def get_etf_holding_dates(self, symbol: str) -> list[date]:
        """Get ETF holding dates

        .. deprecated::
            ``etf/portfolio-dates`` 404s and will be removed in a future
            version. It currently returns an empty list. Use
            :meth:`get_mutual_fund_dates` or :meth:`get_fund_disclosure_dates`,
            which serve the live ``funds/disclosure-dates``. Not a drop-in:
            they yield a ``date``/``year``/``quarter`` record per period, where
            this returned a bare :class:`datetime.date`.
        """
        return []

    async def get_etf_info(self, symbol: str) -> ETFInfo | None:
        """
        Get ETF information

        Args:
            symbol: ETF symbol

        Returns:
            ETFInfo object if found, or None if no data/error occurs
        """
        try:
            result = cast(
                object, await self.client.request_async(ETF_INFO, symbol=symbol)
            )
            if isinstance(result, ETFInfo):
                return result
            if isinstance(result, list):
                return cast(
                    ETFInfo | None,
                    self._unwrap_single(result, ETFInfo, allow_none=True),
                )
            warnings.warn(
                f"Unexpected result type from ETF_INFO: {type(result)}", stacklevel=2
            )
            return None
        except (FMPError, ValidationError) as e:
            warnings.warn(f"Error in get_etf_info: {e!s}", stacklevel=2)
            return None
        except Exception:
            logger.exception("Unexpected error in get_etf_info for symbol %s", symbol)
            raise

    async def get_etf_sector_weightings(self, symbol: str) -> list[ETFSectorWeighting]:
        """Get ETF sector weightings"""
        return self._unwrap_list(
            await self.client.request_async(ETF_SECTOR_WEIGHTINGS, symbol=symbol),
            ETFSectorWeighting,
        )

    async def get_etf_country_weightings(
        self, symbol: str
    ) -> list[ETFCountryWeighting]:
        """Get ETF country weightings"""
        return self._unwrap_list(
            await self.client.request_async(ETF_COUNTRY_WEIGHTINGS, symbol=symbol),
            ETFCountryWeighting,
        )

    async def get_etf_exposure(self, symbol: str) -> list[ETFExposure]:
        """Get ETF stock exposure"""
        return self._unwrap_list(
            await self.client.request_async(ETF_EXPOSURE, symbol=symbol), ETFExposure
        )

    @deprecated(
        "etf/holder is dead and FMP publishes nothing with this shape. "
        "get_fund_disclosure_holders_latest() is the closest live successor: "
        "it answers 'who holds this fund', but returns holder/shares/change/"
        "dateReported/weightPercent, not the asset-level columns here. Note "
        "get_mutual_fund_holder() declared the same dead path."
    )
    async def get_etf_holder(self, symbol: str) -> list[ETFHolder]:
        """Get ETF holder information

        .. deprecated::
            ``etf/holder`` 404s and will be removed in a future version. It
            currently returns an empty list. The nearest live endpoint is
            :meth:`get_fund_disclosure_holders_latest`
            (``funds/disclosure-holders-latest``), but the payload differs:
            it carries ``holder``, ``shares``, ``change``, ``dateReported``
            and ``weightPercent``, where
            :class:`~fmp_data.investment.models.ETFHolder` declares ``asset``,
            ``cusip``, ``isin``, ``marketValue`` and ``sharesNumber``.
            ``funds/disclosure-holders-search`` is *not* the replacement — it
            returns fund entity records (address, city, entityName).
        """
        return []

    # Mutual Fund methods
    async def get_mutual_fund_dates(
        self, symbol: str, cik: str | int | None = None
    ) -> list[PortfolioDate]:
        """Get mutual fund/ETF disclosure dates

        Args:
            symbol: Fund or ETF symbol
            cik: Optional fund CIK

        Returns:
            List of disclosure date records
        """
        params: dict[str, str | int] = {"symbol": symbol}
        if cik is not None:
            params["cik"] = cik
        return self._unwrap_list(
            await self.client.request_async(MUTUAL_FUND_DATES, **params),
            PortfolioDate,
        )

    async def get_fund_disclosure_dates(
        self, symbol: str, cik: str | int | None = None
    ) -> list[PortfolioDate]:
        """Get mutual fund/ETF disclosure dates"""
        return await self.get_mutual_fund_dates(symbol=symbol, cik=cik)

    @deprecated(
        "mutual-fund-holdings is dead. Use get_etf_holdings(symbol), which "
        "serves the live etf/holdings and accepts mutual fund symbols too. "
        "For full N-PORT regulatory detail use get_fund_disclosure()."
    )
    async def get_mutual_fund_holdings(
        self, symbol: str, holdings_date: date
    ) -> list[MutualFundHolding]:
        """Get mutual fund holdings

        .. deprecated::
            ``mutual-fund-holdings`` 404s and will be removed in a future
            version. It currently returns an empty list. Use
            :meth:`get_etf_holdings`, which serves the live ``etf/holdings``
            and answers for mutual fund symbols as well. Field names differ
            (``securityCusip``/``sharesNumber`` rather than ``cusip``/
            ``shares``) and ``cik``/``reportedDate`` are absent. If you need
            the full N-PORT record — ``assetCat``, ``fairValLevel``,
            ``payoffProfile``, ``valUsd`` — use :meth:`get_fund_disclosure`.
        """
        return []

    @deprecated(
        "mutual-fund-holdings/name is dead and has no replacement: every "
        "path variant 404s. stable/search-name is live but is a generic "
        "ticker search returning a different shape, not fund holdings."
    )
    async def get_mutual_fund_by_name(self, name: str) -> list[MutualFundHolding]:
        """Get mutual funds by name

        .. deprecated::
            ``mutual-fund-holdings/name`` 404s and will be removed in a future
            version. It currently returns an empty list. FMP publishes no
            replacement — a dozen path variants were probed and all 404.
            ``search-name`` is live but is a generic symbol search, not a
            holdings lookup, so it is not offered as a migration target.
        """
        return []

    @deprecated(
        "etf/holder is dead. This method declared the same path as "
        "get_etf_holder() -- the two were duplicates. "
        "get_fund_disclosure_holders_latest() is the closest live successor, "
        "with a different payload."
    )
    async def get_mutual_fund_holder(self, symbol: str) -> list[MutualFundHolder]:
        """Get mutual fund holder information

        .. deprecated::
            ``etf/holder`` 404s and will be removed in a future version. It
            currently returns an empty list. This method and
            :meth:`get_etf_holder` declared the *same* dead path, so only one
            successor is needed: :meth:`get_fund_disclosure_holders_latest`
            (``funds/disclosure-holders-latest``). Its
            ``holder``/``shares``/``change``/``dateReported``/``weightPercent``
            shape happens to be close to
            :class:`~fmp_data.investment.models.MutualFundHolder`, but it is
            not guaranteed identical — check the fields you rely on.
        """
        return []

    async def get_fund_disclosure_holders_latest(
        self, symbol: str
    ) -> list[FundDisclosureHolderLatest]:
        """Get latest mutual fund/ETF disclosure holders"""
        return self._unwrap_list(
            await self.client.request_async(
                FUNDS_DISCLOSURE_HOLDERS_LATEST, symbol=symbol
            ),
            FundDisclosureHolderLatest,
        )

    async def get_fund_disclosure(
        self, symbol: str, year: int, quarter: int, cik: str | int | None = None
    ) -> list[FundDisclosureHolding]:
        """Get mutual fund/ETF disclosure holdings"""
        params: dict[str, str | int] = {
            "symbol": symbol,
            "year": year,
            "quarter": quarter,
        }
        if cik is not None:
            params["cik"] = cik
        return self._unwrap_list(
            await self.client.request_async(FUNDS_DISCLOSURE, **params),
            FundDisclosureHolding,
        )

    async def search_fund_disclosure_holders(
        self, name: str
    ) -> list[FundDisclosureSearchResult]:
        """Search mutual fund/ETF disclosure holders by name"""
        return self._unwrap_list(
            await self.client.request_async(FUNDS_DISCLOSURE_HOLDERS_SEARCH, name=name),
            FundDisclosureSearchResult,
        )
