# fmp_data/market/client.py
from datetime import date as dt_date

from fmp_data.base import EndpointGroup
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


class MarketClient(EndpointGroup):
    """Client for market data endpoints"""

    def search_company(
        self, query: str, limit: int | None = None, exchange: str | None = None
    ) -> list[CompanySearchResult]:
        """Search for companies"""
        params = {"query": query}
        if limit is not None:
            params["limit"] = str(limit)
        if exchange is not None:
            params["exchange"] = exchange
        return self._unwrap_list(
            self.client.request(SEARCH_COMPANY, **params), CompanySearchResult
        )

    def search_symbol(
        self, query: str, limit: int | None = None, exchange: str | None = None
    ) -> list[CompanySearchResult]:
        """Search for security symbols across all asset types"""
        params = {"query": query}
        if limit is not None:
            params["limit"] = str(limit)
        if exchange is not None:
            params["exchange"] = exchange
        return self._unwrap_list(
            self.client.request(SEARCH_SYMBOL, **params), CompanySearchResult
        )

    def search_exchange_variants(self, query: str) -> list[CompanySearchResult]:
        """Search exchange variants by ticker (for example ``query="MSFT"``).

        The public ``query`` argument is sent as FMP's ``symbol`` parameter.
        """
        return self._unwrap_list(
            self.client.request(SEARCH_EXCHANGE_VARIANTS, query=query),
            CompanySearchResult,
        )

    def get_stock_list(self) -> list[CompanySymbol]:
        """Get list of all available stocks"""
        return self._unwrap_list(self.client.request(STOCK_LIST), CompanySymbol)

    def get_financial_statement_symbol_list(self) -> list[CompanySymbol]:
        """Get list of symbols with financial statements available"""
        return self._unwrap_list(
            self.client.request(FINANCIAL_STATEMENT_SYMBOL_LIST), CompanySymbol
        )

    def get_etf_list(self) -> list[CompanySymbol]:
        """Get list of all available ETFs"""
        return self._unwrap_list(self.client.request(ETF_LIST), CompanySymbol)

    def get_actively_trading_list(self) -> list[CompanySymbol]:
        """Get list of actively trading stocks"""
        return self._unwrap_list(
            self.client.request(ACTIVELY_TRADING_LIST), CompanySymbol
        )

    @deprecated(
        "tradable-list is dead and FMP publishes no drop-in replacement: "
        "available-traded/list, symbol-list, tradable-symbol-list and "
        "symbol/all all 404 too. get_stock_list(), get_etf_list() and "
        "get_actively_trading_list() are partial substitutes with different "
        "membership -- 'tradable' is not the same set as 'all stocks'."
    )
    def get_tradable_list(
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

    def get_available_indexes(self) -> list[AvailableIndex]:
        """Get list of all available indexes"""
        return self._unwrap_list(self.client.request(AVAILABLE_INDEXES), AvailableIndex)

    def search_by_cik(
        self,
        query: str,
        *,
        limit: int | None = None,
    ) -> list[CIKResult]:
        """Search companies by CIK number.

        Args:
            query: The CIK number, e.g. ``"320193"`` or ``"0000320193"``.
                Despite the parameter name this is not a free-text search:
                the API matches a CIK only and rejects a company name with
                400 ``Invalid or missing query parameter - cik``. A numeric
                value is zero-padded to the canonical 10 digits before it is
                sent.

        Returns:
            List of matching CIK records.

        Additional keyword arguments (None preserves the existing request):
            limit: Maximum number of results requested from FMP.
        """
        optional_params = {
            "limit": limit,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        return self._unwrap_list(
            self.client.request(CIK_SEARCH, query=query, **optional_params), CIKResult
        )

    def get_cik_list(self, page: int = 0, limit: int = 1000) -> list[CIKListEntry]:
        """Get complete list of all CIK numbers"""
        return self._unwrap_list(
            self.client.request(CIK_LIST, page=page, limit=limit), CIKListEntry
        )

    def search_by_cusip(self, query: str) -> list[CUSIPResult]:
        """Search companies by CUSIP"""
        return self._unwrap_list(
            self.client.request(CUSIP_SEARCH, query=query), CUSIPResult
        )

    def search_by_isin(self, query: str) -> list[ISINResult]:
        """Search companies by ISIN"""
        return self._unwrap_list(
            self.client.request(ISIN_SEARCH, query=query), ISINResult
        )

    def get_company_screener(
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

        Additional keyword arguments (None preserves the existing request):
            avg_volume_more_than: Minimum average trading volume filter.
            avg_volume_less_than: Maximum average trading volume filter.
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
            self.client.request(COMPANY_SCREENER, **params, **optional_params),
            CompanySearchResult,
        )

    def get_market_hours(
        self,
        exchange: str = "NYSE",
        *,
        timestamp: int | None = None,
    ) -> MarketHours:
        """Get market trading hours information for a specific exchange

        Args:
            exchange: Exchange code (e.g., "NYSE", "NASDAQ"). Defaults to "NYSE".

        Returns:
            MarketHours: Exchange trading hours object

        Raises:
            ValueError: If the API returns an empty list

        Additional keyword arguments (None preserves the existing request):
            timestamp: Unix timestamp in seconds at which to evaluate market hours.
        """
        optional_params = {
            "timestamp": timestamp,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        result = self.client.request(MARKET_HOURS, exchange=exchange, **optional_params)
        return self._unwrap_single(result, MarketHours)

    def get_all_exchange_market_hours(
        self,
        *,
        timestamp: int | None = None,
    ) -> list[MarketHours]:
        """Get market trading hours information for all exchanges

        Additional keyword arguments (None preserves the existing request):
            timestamp: Unix timestamp in seconds at which to evaluate market hours.
        """
        optional_params = {
            "timestamp": timestamp,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        return self._unwrap_list(
            self.client.request(ALL_EXCHANGE_MARKET_HOURS, **optional_params),
            MarketHours,
        )

    def get_holidays_by_exchange(
        self,
        exchange: str = "NYSE",
        *,
        from_date: dt_date | None = None,
        to_date: dt_date | None = None,
    ) -> list[MarketHoliday]:
        """Get market holidays for a specific exchange

        Additional keyword arguments (None preserves the existing request):
            from_date: Start date passed to FMP; boundary semantics depend on the
                endpoint.
            to_date: End date passed to FMP; boundary semantics depend on the endpoint.
        """
        optional_params = {
            "from_date": from_date,
            "to_date": to_date,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        return self._unwrap_list(
            self.client.request(
                HOLIDAYS_BY_EXCHANGE, exchange=exchange, **optional_params
            ),
            MarketHoliday,
        )

    def get_gainers(self) -> list[MarketMover]:
        """Get market gainers"""
        return self._unwrap_list(self.client.request(GAINERS), MarketMover)

    def get_losers(self) -> list[MarketMover]:
        """Get market losers"""
        return self._unwrap_list(self.client.request(LOSERS), MarketMover)

    def get_most_active(self) -> list[MarketMover]:
        """Get most active stocks"""
        return self._unwrap_list(self.client.request(MOST_ACTIVE), MarketMover)

    def get_sector_performance(
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
            self.client.request(SECTOR_PERFORMANCE, **params), SectorPerformance
        )

    def get_industry_performance_snapshot(
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
            self.client.request(INDUSTRY_PERFORMANCE_SNAPSHOT, **params),
            IndustryPerformance,
        )

    def get_historical_sector_performance(
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
            self.client.request(HISTORICAL_SECTOR_PERFORMANCE, **params),
            SectorPerformance,
        )

    def get_historical_industry_performance(
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
            self.client.request(HISTORICAL_INDUSTRY_PERFORMANCE, **params),
            IndustryPerformance,
        )

    def get_sector_pe_snapshot(
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
            self.client.request(SECTOR_PE_SNAPSHOT, **params), SectorPESnapshot
        )

    def get_industry_pe_snapshot(
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
            self.client.request(INDUSTRY_PE_SNAPSHOT, **params), IndustryPESnapshot
        )

    def get_historical_sector_pe(
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
            self.client.request(HISTORICAL_SECTOR_PE, **params), SectorPESnapshot
        )

    def get_historical_industry_pe(
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
            self.client.request(HISTORICAL_INDUSTRY_PE, **params), IndustryPESnapshot
        )

    @deprecated(
        "pre-post-market is dead, and the market-wide shape no longer exists. "
        "Live extended-hours data is per symbol: "
        "FMPDataClient.company.get_aftermarket_quote(symbol), or the "
        "batch-aftermarket-quote endpoint, which requires a symbols parameter."
    )
    def get_pre_post_market(self) -> list[PrePostMarketQuote]:
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

    def get_all_shares_float(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
    ) -> list[ShareFloat]:
        """Get share float data for all companies

        Additional keyword arguments (None preserves the existing request):
            page: Zero-based page number; pagination is controlled by the caller.
            limit: Maximum number of results requested from FMP.
        """
        optional_params = {
            "page": page,
            "limit": limit,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        return self._unwrap_list(
            self.client.request(ALL_SHARES_FLOAT, **optional_params), ShareFloat
        )

    def get_available_exchanges(
        self,
        *,
        extended: bool | None = None,
    ) -> list[ExchangeSymbol]:
        """Get a complete list of supported stock exchanges

        Additional keyword arguments (None preserves the existing request):
            extended: Include extended exchange listings.
        """
        optional_params = {
            "extended": extended,
        }
        optional_params = {
            key: value for key, value in optional_params.items() if value is not None
        }
        return self._unwrap_list(
            self.client.request(AVAILABLE_EXCHANGES, **optional_params), ExchangeSymbol
        )

    def get_available_sectors(self) -> list[str]:
        """Get a complete list of industry sectors"""
        return self._unwrap_list(self.client.request(AVAILABLE_SECTORS), str)

    def get_available_industries(self) -> list[str]:
        """Get a comprehensive list of industries where stock symbols are available"""
        return self._unwrap_list(self.client.request(AVAILABLE_INDUSTRIES), str)

    def get_available_countries(self) -> list[str]:
        """Get a comprehensive list of countries where stock symbols are available"""
        return self._unwrap_list(self.client.request(AVAILABLE_COUNTRIES), str)

    def get_ipo_disclosure(
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
            self.client.request(IPO_DISCLOSURE, **params), IPODisclosure
        )

    def get_ipo_prospectus(
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
            self.client.request(IPO_PROSPECTUS, **params), IPOProspectus
        )
