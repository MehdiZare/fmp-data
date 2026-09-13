# fmp_data/market/async_client.py
"""Async client for market data endpoints."""

from datetime import date as dt_date

from fmp_data.base import AsyncEndpointGroup
from fmp_data.helpers import deprecated
from fmp_data.market.endpoints import (
    ACTIVELY_TRADING_LIST,
    ALL_EXCHANGE_MARKET_HOURS,
    ALL_SHARES_FLOAT,
    AVAILABLE_COUNTRIES,
    AVAILABLE_EXCHANGES,
    AVAILABLE_INDEXES,
    AVAILABLE_INDUSTRIES,
    AVAILABLE_SECTORS,
    CIK_LIST,
    CIK_SEARCH,
    COMPANY_SCREENER,
    CUSIP_SEARCH,
    ETF_LIST,
    FINANCIAL_STATEMENT_SYMBOL_LIST,
    GAINERS,
    HISTORICAL_INDUSTRY_PE,
    HISTORICAL_INDUSTRY_PERFORMANCE,
    HISTORICAL_SECTOR_PE,
    HISTORICAL_SECTOR_PERFORMANCE,
    HOLIDAYS_BY_EXCHANGE,
    INDUSTRY_PE_SNAPSHOT,
    INDUSTRY_PERFORMANCE_SNAPSHOT,
    IPO_DISCLOSURE,
    IPO_PROSPECTUS,
    ISIN_SEARCH,
    LOSERS,
    MARKET_HOURS,
    MOST_ACTIVE,
    SEARCH_COMPANY,
    SEARCH_EXCHANGE_VARIANTS,
    SEARCH_SYMBOL,
    SECTOR_PE_SNAPSHOT,
    SECTOR_PERFORMANCE,
    STOCK_LIST,
)
from fmp_data.market.models import (
    AvailableIndex,
    CIKListEntry,
    CIKResult,
    CompanySearchResult,
    CUSIPResult,
    ExchangeSymbol,
    IndustryPerformance,
    IndustryPESnapshot,
    IPODisclosure,
    IPOProspectus,
    ISINResult,
    MarketHoliday,
    MarketHours,
    MarketMover,
    PrePostMarketQuote,
    SectorPerformance,
    SectorPESnapshot,
)
from fmp_data.models import CompanySymbol, ShareFloat


class AsyncMarketClient(AsyncEndpointGroup):
    """Async client for market data endpoints."""

    async def search_company(
        self, query: str, limit: int | None = None, exchange: str | None = None
    ) -> list[CompanySearchResult]:
        """Search for companies"""
        params: dict[str, str | int] = {"query": query}
        if limit is not None:
            params["limit"] = limit
        if exchange is not None:
            params["exchange"] = exchange
        return self._unwrap_list(
            await self.client.request_async(SEARCH_COMPANY, **params),
            CompanySearchResult,
        )

    async def search_symbol(
        self, query: str, limit: int | None = None, exchange: str | None = None
    ) -> list[CompanySearchResult]:
        """Search for security symbols across all asset types"""
        params: dict[str, str | int] = {"query": query}
        if limit is not None:
            params["limit"] = limit
        if exchange is not None:
            params["exchange"] = exchange
        return self._unwrap_list(
            await self.client.request_async(SEARCH_SYMBOL, **params),
            CompanySearchResult,
        )

    async def search_exchange_variants(self, query: str) -> list[CompanySearchResult]:
        """Search exchange variants by ticker (for example ``query="MSFT"``).

        The public ``query`` argument is sent as FMP's ``symbol`` parameter.

        Args:
            query: Ticker symbol, for example "MSFT".

        Returns:
            list[CompanySearchResult]: Parsed provider records.

        Example:
            records = await client.market.search_exchange_variants(
                'MSFT'
            )
        """
        return self._unwrap_list(
            await self.client.request_async(SEARCH_EXCHANGE_VARIANTS, query=query),
            CompanySearchResult,
        )

    async def get_stock_list(self) -> list[CompanySymbol]:
        """Get list of all available stocks"""
        return self._unwrap_list(
            await self.client.request_async(STOCK_LIST), CompanySymbol
        )

    async def get_financial_statement_symbol_list(self) -> list[CompanySymbol]:
        """Get list of symbols with financial statements available"""
        return self._unwrap_list(
            await self.client.request_async(FINANCIAL_STATEMENT_SYMBOL_LIST),
            CompanySymbol,
        )

    async def get_etf_list(self) -> list[CompanySymbol]:
        """Get list of all available ETFs"""
        return self._unwrap_list(
            await self.client.request_async(ETF_LIST), CompanySymbol
        )

    async def get_actively_trading_list(self) -> list[CompanySymbol]:
        """Get list of actively trading stocks"""
        return self._unwrap_list(
            await self.client.request_async(ACTIVELY_TRADING_LIST), CompanySymbol
        )

    @deprecated(
        "tradable-list is dead and FMP publishes no drop-in replacement: "
        "available-traded/list, symbol-list, tradable-symbol-list and "
        "symbol/all all 404 too. get_stock_list(), get_etf_list() and "
        "get_actively_trading_list() are partial substitutes with different "
        "membership -- 'tradable' is not the same set as 'all stocks'."
    )
    async def get_tradable_list(
        self, limit: int | None = None, offset: int | None = None
    ) -> list[CompanySymbol]:
        """Get list of tradable securities

        .. deprecated::
            ``tradable-list`` 404s and will be removed in a future version. It
            currently returns an empty list. There is **no drop-in
            replacement** — every path variant probed also 404s. The closest
            live sources are :meth:`get_stock_list`, :meth:`get_etf_list` and
            :meth:`get_actively_trading_list`, but each defines a different
            universe: "tradable" is not the same set as "every listed stock",
            so choosing one is a decision about which universe you want, not a
            mechanical substitution.
        """
        return []

    async def get_available_indexes(self) -> list[AvailableIndex]:
        """Get list of all available indexes"""
        return self._unwrap_list(
            await self.client.request_async(AVAILABLE_INDEXES), AvailableIndex
        )

    async def search_by_cik(
        self,
        query: str,
        *,
        limit: int | None = None,
    ) -> list[CIKResult]:
        """Search companies by CIK number.

        New keyword-only filters are omitted when None, preserving the existing
        request.

        Args:
            query: The CIK number, e.g. ``"320193"`` or ``"0000320193"``. Despite
                the parameter name this is not a free-text search: the API matches a
                CIK only and rejects a company name with 400 ``Invalid or missing
                query parameter - cik``. A numeric value is zero-padded to the
                canonical 10 digits before it is sent.
            limit: Maximum number of results requested from FMP.

        Returns:
            List of matching CIK records.

        Example:
            records = await client.market.search_by_cik(
                '320193', limit=20
            )
        """
        optional_params = {
            "limit": limit,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        return self._unwrap_list(
            await self.client.request_async(CIK_SEARCH, query=query, **optional_params),
            CIKResult,
        )

    async def get_cik_list(
        self, page: int = 0, limit: int = 1000
    ) -> list[CIKListEntry]:
        """Get complete list of all CIK numbers"""
        return self._unwrap_list(
            await self.client.request_async(CIK_LIST, page=page, limit=limit),
            CIKListEntry,
        )

    async def search_by_cusip(self, query: str) -> list[CUSIPResult]:
        """Search companies by CUSIP"""
        return self._unwrap_list(
            await self.client.request_async(CUSIP_SEARCH, query=query), CUSIPResult
        )

    async def search_by_isin(self, query: str) -> list[ISINResult]:
        """Search companies by ISIN"""
        return self._unwrap_list(
            await self.client.request_async(ISIN_SEARCH, query=query), ISINResult
        )

    async def get_company_screener(
        self,
        market_cap_more_than: float | None = None,
        market_cap_less_than: float | None = None,
        price_more_than: float | None = None,
        price_less_than: float | None = None,
        beta_more_than: float | None = None,
        beta_less_than: float | None = None,
        volume_more_than: int | None = None,
        volume_less_than: int | None = None,
        dividend_more_than: float | None = None,
        dividend_less_than: float | None = None,
        is_etf: bool | None = None,
        is_fund: bool | None = None,
        is_actively_trading: bool | None = None,
        sector: str | None = None,
        industry: str | None = None,
        country: str | None = None,
        exchange: str | None = None,
        limit: int | None = None,
        page: int | None = None,
        include_all_share_classes: bool | None = None,
        *,
        avg_volume_more_than: int | None = None,
        avg_volume_less_than: int | None = None,
    ) -> list[CompanySearchResult]:
        """Screen companies based on various criteria.

        ``page`` is omitted from the request when unset so existing callers
        keep the same wire shape. Pass ``0`` or a later page to paginate.

        New keyword-only filters are omitted when None, preserving the existing
        request.

        Args:
            market_cap_more_than: Minimum market capitalization filter; omitted when
                None.
            market_cap_less_than: Maximum market capitalization filter; omitted when
                None.
            price_more_than: Minimum share price filter; omitted when None.
            price_less_than: Maximum share price filter; omitted when None.
            beta_more_than: Minimum beta filter; omitted when None.
            beta_less_than: Maximum beta filter; omitted when None.
            volume_more_than: Minimum trading volume filter; omitted when None.
            volume_less_than: Maximum trading volume filter; omitted when None.
            dividend_more_than: Minimum dividend yield filter; omitted when None.
            dividend_less_than: Maximum dividend yield filter; omitted when None.
            is_etf: Filter for ETFs; omitted when None.
            is_fund: Filter for funds; omitted when None.
            is_actively_trading: Filter by active trading status; omitted when None.
            sector: Sector filter; omitted when None.
            industry: Industry filter; omitted when None.
            country: Provider country code filter; omitted when None.
            exchange: Exchange code filter; omitted when None.
            limit: Maximum result count; omitted when None.
            page: Zero-based page number; omitted when None.
            include_all_share_classes: Include all share classes when True; omitted
                when None.
            avg_volume_more_than: Minimum average trading volume filter.
            avg_volume_less_than: Maximum average trading volume filter.

        Returns:
            list[CompanySearchResult]: Parsed provider records.

        Example:
            records = await client.market.get_company_screener(
                avg_volume_more_than=0
            )
        """
        optional_params = {
            "avg_volume_more_than": avg_volume_more_than,
            "avg_volume_less_than": avg_volume_less_than,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        params = {
            "market_cap_more_than": market_cap_more_than,
            "market_cap_less_than": market_cap_less_than,
            "price_more_than": price_more_than,
            "price_less_than": price_less_than,
            "beta_more_than": beta_more_than,
            "beta_less_than": beta_less_than,
            "volume_more_than": volume_more_than,
            "volume_less_than": volume_less_than,
            "dividend_more_than": dividend_more_than,
            "dividend_less_than": dividend_less_than,
            "is_etf": is_etf,
            "is_fund": is_fund,
            "is_actively_trading": is_actively_trading,
            "sector": sector,
            "industry": industry,
            "country": country,
            "exchange": exchange,
            "limit": limit,
            "page": page,
            "include_all_share_classes": include_all_share_classes,
        }
        params = {key: value for key, value in params.items() if value is not None}
        return self._unwrap_list(
            await self.client.request_async(
                COMPANY_SCREENER, **params, **optional_params
            ),
            CompanySearchResult,
        )

    async def get_market_hours(
        self,
        exchange: str = "NYSE",
        *,
        timestamp: int | None = None,
    ) -> MarketHours:
        """Get market trading hours information for a specific exchange

        New keyword-only filters are omitted when None, preserving the existing
        request.

        Args:
            exchange: Exchange code (e.g., "NYSE", "NASDAQ"). Defaults to "NYSE".
            timestamp: Unix timestamp in seconds at which to evaluate market hours.

        Returns:
            MarketHours: Exchange trading hours object

        Raises:
            ValueError: If the API returns an empty list

        Example:
            records = await client.market.get_market_hours(
                timestamp=0
            )
        """
        optional_params = {
            "timestamp": timestamp,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        result = await self.client.request_async(
            MARKET_HOURS, exchange=exchange, **optional_params
        )
        return self._unwrap_single(result, MarketHours)

    async def get_all_exchange_market_hours(
        self,
        *,
        timestamp: int | None = None,
    ) -> list[MarketHours]:
        """Get market trading hours information for all exchanges

        New keyword-only filters are omitted when None, preserving the existing
        request.

        Args:
            timestamp: Unix timestamp in seconds at which to evaluate market hours.

        Returns:
            list[MarketHours]: Parsed provider records.

        Example:
            records = await client.market.get_all_exchange_market_hours(
                timestamp=0
            )
        """
        optional_params = {
            "timestamp": timestamp,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        return self._unwrap_list(
            await self.client.request_async(
                ALL_EXCHANGE_MARKET_HOURS, **optional_params
            ),
            MarketHours,
        )

    async def get_holidays_by_exchange(
        self,
        exchange: str = "NYSE",
        *,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
    ) -> list[MarketHoliday]:
        """Get market holidays for a specific exchange

        New keyword-only filters are omitted when None, preserving the existing
        request.

        FMP was observed to use (from_date, to_date] bounds. Returned rows and
        empty responses do not establish complete calendar coverage.

        Args:
            exchange: Exchange code, for example "NYSE"; defaults to "NYSE".
            from_date: Start date passed to FMP; boundary semantics depend on the
                endpoint.
            to_date: End date passed to FMP; boundary semantics depend on the
                endpoint.

        Returns:
            list[MarketHoliday]: Parsed provider records.

        Example:
            from datetime import date
            records = await client.market.get_holidays_by_exchange(
                from_date=date(2026, 9, 10)
            )
        """
        optional_params = {
            "from_date": from_date,
            "to_date": to_date,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        return self._unwrap_list(
            await self.client.request_async(
                HOLIDAYS_BY_EXCHANGE, exchange=exchange, **optional_params
            ),
            MarketHoliday,
        )

    async def get_gainers(self) -> list[MarketMover]:
        """Get market gainers"""
        return self._unwrap_list(await self.client.request_async(GAINERS), MarketMover)

    async def get_losers(self) -> list[MarketMover]:
        """Get market losers"""
        return self._unwrap_list(await self.client.request_async(LOSERS), MarketMover)

    async def get_most_active(self) -> list[MarketMover]:
        """Get most active stocks"""
        return self._unwrap_list(
            await self.client.request_async(MOST_ACTIVE), MarketMover
        )

    async def get_sector_performance(
        self,
        sector: str | None = None,
        date: dt_date | None = None,
        exchange: str | None = None,
    ) -> list[SectorPerformance]:
        """Get sector performance data"""
        params: dict[str, str] = {}
        if sector is not None:
            params["sector"] = sector
        if exchange is not None:
            params["exchange"] = exchange
        snapshot_date = date or dt_date.today()
        params["date"] = snapshot_date.strftime("%Y-%m-%d")
        return self._unwrap_list(
            await self.client.request_async(SECTOR_PERFORMANCE, **params),
            SectorPerformance,
        )

    async def get_industry_performance_snapshot(
        self,
        industry: str | None = None,
        date: dt_date | None = None,
        exchange: str | None = None,
    ) -> list[IndustryPerformance]:
        """Get industry performance snapshot data"""
        params: dict[str, str] = {}
        if industry is not None:
            params["industry"] = industry
        if exchange is not None:
            params["exchange"] = exchange
        snapshot_date = date or dt_date.today()
        params["date"] = snapshot_date.strftime("%Y-%m-%d")
        return self._unwrap_list(
            await self.client.request_async(INDUSTRY_PERFORMANCE_SNAPSHOT, **params),
            IndustryPerformance,
        )

    async def get_historical_sector_performance(
        self,
        sector: str,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
        exchange: str | None = None,
    ) -> list[SectorPerformance]:
        """Get historical sector performance data"""
        params: dict[str, str] = {"sector": sector}
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        if exchange:
            params["exchange"] = exchange
        return self._unwrap_list(
            await self.client.request_async(HISTORICAL_SECTOR_PERFORMANCE, **params),
            SectorPerformance,
        )

    async def get_historical_industry_performance(
        self,
        industry: str,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
        exchange: str | None = None,
    ) -> list[IndustryPerformance]:
        """Get historical industry performance data"""
        params: dict[str, str] = {"industry": industry}
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        if exchange:
            params["exchange"] = exchange
        return self._unwrap_list(
            await self.client.request_async(HISTORICAL_INDUSTRY_PERFORMANCE, **params),
            IndustryPerformance,
        )

    async def get_sector_pe_snapshot(
        self,
        date: dt_date | None = None,
        sector: str | None = None,
        exchange: str | None = None,
    ) -> list[SectorPESnapshot]:
        """Get sector price-to-earnings snapshot data"""
        params: dict[str, str] = {}
        if sector is not None:
            params["sector"] = sector
        if exchange is not None:
            params["exchange"] = exchange
        snapshot_date = date or dt_date.today()
        params["date"] = snapshot_date.strftime("%Y-%m-%d")
        return self._unwrap_list(
            await self.client.request_async(SECTOR_PE_SNAPSHOT, **params),
            SectorPESnapshot,
        )

    async def get_industry_pe_snapshot(
        self,
        date: dt_date | None = None,
        industry: str | None = None,
        exchange: str | None = None,
    ) -> list[IndustryPESnapshot]:
        """Get industry price-to-earnings snapshot data"""
        params: dict[str, str] = {}
        if industry is not None:
            params["industry"] = industry
        if exchange is not None:
            params["exchange"] = exchange
        snapshot_date = date or dt_date.today()
        params["date"] = snapshot_date.strftime("%Y-%m-%d")
        return self._unwrap_list(
            await self.client.request_async(INDUSTRY_PE_SNAPSHOT, **params),
            IndustryPESnapshot,
        )

    async def get_historical_sector_pe(
        self,
        sector: str,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
        exchange: str | None = None,
    ) -> list[SectorPESnapshot]:
        """Get historical sector price-to-earnings data"""
        params: dict[str, str] = {"sector": sector}
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        if exchange:
            params["exchange"] = exchange
        return self._unwrap_list(
            await self.client.request_async(HISTORICAL_SECTOR_PE, **params),
            SectorPESnapshot,
        )

    async def get_historical_industry_pe(
        self,
        industry: str,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
        exchange: str | None = None,
    ) -> list[IndustryPESnapshot]:
        """Get historical industry price-to-earnings data"""
        params: dict[str, str] = {"industry": industry}
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        if exchange:
            params["exchange"] = exchange
        return self._unwrap_list(
            await self.client.request_async(HISTORICAL_INDUSTRY_PE, **params),
            IndustryPESnapshot,
        )

    @deprecated(
        "pre-post-market is dead, and the market-wide shape no longer exists. "
        "Live extended-hours data is per symbol: "
        "FMPDataClient.company.get_aftermarket_quote(symbol), or the "
        "batch-aftermarket-quote endpoint, which requires a symbols parameter."
    )
    async def get_pre_post_market(self) -> list[PrePostMarketQuote]:
        """Get pre/post market data

        .. deprecated::
            ``pre-post-market`` 404s and will be removed in a future version.
            It currently returns an empty list. **The no-argument, market-wide
            call no longer exists at FMP** — extended-hours data is per-symbol
            now, so there is no signature-compatible replacement. Use
            ``client.company.get_aftermarket_quote(symbol)``, or
            ``batch-aftermarket-quote``/``batch-aftermarket-trade`` with a
            mandatory ``symbols`` parameter for several at once. The payload
            differs too: bid/ask price and size, not this model's ``price``
            and ``session``.
        """
        return []

    async def get_all_shares_float(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
    ) -> list[ShareFloat]:
        """Get share float data for all companies

        New keyword-only filters are omitted when None, preserving the existing
        request.

        Args:
            page: Zero-based page number; pagination is controlled by the caller.
            limit: Maximum number of results requested from FMP.

        Returns:
            list[ShareFloat]: Parsed provider records.

        Example:
            records = await client.market.get_all_shares_float(
                page=0
            )
        """
        optional_params = {
            "page": page,
            "limit": limit,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        return self._unwrap_list(
            await self.client.request_async(ALL_SHARES_FLOAT, **optional_params),
            ShareFloat,
        )

    async def get_available_exchanges(
        self,
        *,
        extended: bool | None = None,
    ) -> list[ExchangeSymbol]:
        """Get a complete list of supported stock exchanges

        New keyword-only filters are omitted when None, preserving the existing
        request.

        Args:
            extended: Include extended exchange listings.

        Returns:
            list[ExchangeSymbol]: Parsed provider records.

        Example:
            records = await client.market.get_available_exchanges(
                extended=False
            )
        """
        optional_params = {
            "extended": extended,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        return self._unwrap_list(
            await self.client.request_async(AVAILABLE_EXCHANGES, **optional_params),
            ExchangeSymbol,
        )

    async def get_available_sectors(self) -> list[str]:
        """Get a complete list of industry sectors"""
        return self._unwrap_list(
            await self.client.request_async(AVAILABLE_SECTORS), str
        )

    async def get_available_industries(self) -> list[str]:
        """Get a comprehensive list of industries where stock symbols are available"""
        return self._unwrap_list(
            await self.client.request_async(AVAILABLE_INDUSTRIES), str
        )

    async def get_available_countries(self) -> list[str]:
        """Get a comprehensive list of countries where stock symbols are available"""
        return self._unwrap_list(
            await self.client.request_async(AVAILABLE_COUNTRIES), str
        )

    async def get_ipo_disclosure(
        self,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
        limit: int = 100,
    ) -> list[IPODisclosure]:
        """Get IPO disclosure documents

        Args:
            from_date: Start date for IPO search (YYYY-MM-DD)
            to_date: End date for IPO search (YYYY-MM-DD)
            limit: Number of results to return (default: 100)

        Returns:
            List of IPO disclosure information
        """
        params: dict[str, str | int] = {"limit": limit}
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        return self._unwrap_list(
            await self.client.request_async(IPO_DISCLOSURE, **params), IPODisclosure
        )

    async def get_ipo_prospectus(
        self,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
        limit: int = 100,
    ) -> list[IPOProspectus]:
        """Get IPO prospectus documents

        Args:
            from_date: Start date for IPO search (YYYY-MM-DD)
            to_date: End date for IPO search (YYYY-MM-DD)
            limit: Number of results to return (default: 100)

        Returns:
            List of IPO prospectus information
        """
        params: dict[str, str | int] = {"limit": limit}
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")
        return self._unwrap_list(
            await self.client.request_async(IPO_PROSPECTUS, **params), IPOProspectus
        )
