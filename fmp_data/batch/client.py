# fmp_data/batch/client.py
import csv
from datetime import date
import io
import logging
from typing import Any, TypeVar, cast, get_args, get_origin

from pydantic import AnyHttpUrl, BaseModel, HttpUrl
from pydantic import ValidationError as PydanticValidationError

from fmp_data.base import EndpointGroup
from fmp_data.batch.endpoints import (
    BALANCE_SHEET_STATEMENT_BULK,
    BALANCE_SHEET_STATEMENT_GROWTH_BULK,
    BATCH_AFTERMARKET_QUOTE,
    BATCH_AFTERMARKET_TRADE,
    BATCH_COMMODITY_QUOTES,
    BATCH_CRYPTO_QUOTES,
    BATCH_ETF_QUOTES,
    BATCH_EXCHANGE_QUOTE,
    BATCH_FOREX_QUOTES,
    BATCH_INDEX_QUOTES,
    BATCH_MARKET_CAP,
    BATCH_MUTUALFUND_QUOTES,
    BATCH_QUOTE,
    BATCH_QUOTE_SHORT,
    CASH_FLOW_STATEMENT_BULK,
    CASH_FLOW_STATEMENT_GROWTH_BULK,
    DCF_BULK,
    EARNINGS_SURPRISES_BULK,
    EOD_BULK,
    ETF_HOLDER_BULK,
    INCOME_STATEMENT_BULK,
    INCOME_STATEMENT_GROWTH_BULK,
    KEY_METRICS_TTM_BULK,
    PEERS_BULK,
    PRICE_TARGET_SUMMARY_BULK,
    PROFILE_BULK,
    RATING_BULK,
    RATIOS_TTM_BULK,
    SCORES_BULK,
    UPGRADES_DOWNGRADES_CONSENSUS_BULK,
)
from fmp_data.batch.models import (
    AftermarketQuote,
    AftermarketTrade,
    BatchMarketCap,
    BatchQuote,
    BatchQuoteShort,
    EarningsSurpriseBulk,
    EODBulk,
    PeersBulk,
)
from fmp_data.company.models import (
    CompanyProfile,
    PriceTargetSummary,
    UpgradeDowngradeConsensus,
)
from fmp_data.fundamental.models import (
    DCF,
    BalanceSheet,
    CashFlowStatement,
    CompanyRating,
    FinancialGrowth,
    FinancialRatiosTTM,
    FinancialScore,
    IncomeStatement,
    KeyMetricsTTM,
)
from fmp_data.investment.models import ETFHolding

logger = logging.getLogger(__name__)
ModelT = TypeVar("ModelT", bound=BaseModel)


class BatchClient(EndpointGroup):
    """Client for batch data endpoints

    Provides methods to retrieve data for multiple symbols or entire asset classes
    in a single API call.
    """

    @staticmethod
    def _parse_csv_rows(raw: bytes) -> list[dict[str, Any]]:
        text = raw.decode("utf-8").strip()
        if not text:
            return []
        reader = csv.DictReader(io.StringIO(text))
        rows: list[dict[str, Any]] = []
        for row in reader:
            if not row or all(value in (None, "", " ") for value in row.values()):
                continue
            normalized: dict[str, str | None] = {}
            for key, value in row.items():
                if value is None:
                    normalized[key] = None
                    continue
                stripped = value.strip()
                normalized[key] = stripped if stripped else None
            rows.append(normalized)
        return rows

    @staticmethod
    def _parse_csv_models(raw: bytes, model: type[ModelT]) -> list[ModelT]:
        results: list[ModelT] = []
        url_fields = BatchClient._get_url_fields(model)
        for row in BatchClient._parse_csv_rows(raw):
            try:
                results.append(model.model_validate(row))
            except PydanticValidationError as exc:
                if url_fields:
                    retry_row = dict(row)
                    for error in exc.errors():
                        if not error.get("loc"):
                            continue
                        field = error["loc"][0]
                        if isinstance(field, str) and field in url_fields:
                            retry_row[field] = None
                    try:
                        results.append(model.model_validate(retry_row))
                        continue
                    except PydanticValidationError:
                        pass
                logger.warning(
                    "Skipping invalid %s row: %s",
                    model.__name__,
                    exc,
                )
        return results

    @staticmethod
    def _get_url_fields(model: type[BaseModel]) -> set[str]:
        url_fields: set[str] = set()
        model_fields = getattr(model, "model_fields", None)
        if not model_fields:
            return url_fields
        for name, field in model_fields.items():
            if BatchClient._is_url_annotation(field.annotation):
                url_fields.add(name)
        return url_fields

    @staticmethod
    def _is_url_annotation(annotation: Any) -> bool:
        origin = get_origin(annotation)
        if origin is None:
            return annotation in {AnyHttpUrl, HttpUrl}
        if origin is list:
            return any(
                BatchClient._is_url_annotation(arg) for arg in get_args(annotation)
            )
        return any(BatchClient._is_url_annotation(arg) for arg in get_args(annotation))

    def get_quotes(self, symbols: list[str]) -> list[BatchQuote]:
        """Get real-time quotes for multiple symbols

        Args:
            symbols: List of stock symbols

        Returns:
            List of quote data for each symbol
        """
        return self.client.request(BATCH_QUOTE, symbols=",".join(symbols))

    def get_quotes_short(self, symbols: list[str]) -> list[BatchQuoteShort]:
        """Get quick price snapshots for multiple symbols

        Args:
            symbols: List of stock symbols

        Returns:
            List of short quote data for each symbol
        """
        return self.client.request(BATCH_QUOTE_SHORT, symbols=",".join(symbols))

    def get_aftermarket_trades(self, symbols: list[str]) -> list[AftermarketTrade]:
        """Get aftermarket (post-market) trade data for multiple symbols

        Args:
            symbols: List of stock symbols

        Returns:
            List of aftermarket trade data
        """
        return self.client.request(BATCH_AFTERMARKET_TRADE, symbols=",".join(symbols))

    def get_aftermarket_quotes(self, symbols: list[str]) -> list[AftermarketQuote]:
        """Get aftermarket quote data for multiple symbols

        Args:
            symbols: List of stock symbols

        Returns:
            List of aftermarket quote data
        """
        return self.client.request(BATCH_AFTERMARKET_QUOTE, symbols=",".join(symbols))

    def get_exchange_quotes(
        self, exchange: str, short: bool | None = None
    ) -> list[BatchQuote]:
        """Get quotes for all stocks on a specific exchange

        Args:
            exchange: Exchange code (e.g., NYSE, NASDAQ)
            short: Whether to return short quote data

        Returns:
            List of quotes for all stocks on the exchange
        """
        params: dict[str, object] = {"exchange": exchange}
        if short is not None:
            params["short"] = short
        return self.client.request(BATCH_EXCHANGE_QUOTE, **params)

    def get_mutualfund_quotes(self, short: bool | None = None) -> list[BatchQuote]:
        """Get batch quotes for all mutual funds

        Args:
            short: Whether to return short quote data

        Returns:
            List of quotes for all mutual funds
        """
        params: dict[str, object] = {}
        if short is not None:
            params["short"] = short
        return self.client.request(BATCH_MUTUALFUND_QUOTES, **params)

    def get_etf_quotes(self, short: bool | None = None) -> list[BatchQuote]:
        """Get batch quotes for all ETFs

        Args:
            short: Whether to return short quote data

        Returns:
            List of quotes for all ETFs
        """
        params: dict[str, object] = {}
        if short is not None:
            params["short"] = short
        return self.client.request(BATCH_ETF_QUOTES, **params)

    def get_commodity_quotes(self, short: bool | None = None) -> list[BatchQuote]:
        """Get batch quotes for all commodities

        Args:
            short: Whether to return short quote data

        Returns:
            List of quotes for all commodities
        """
        params: dict[str, object] = {}
        if short is not None:
            params["short"] = short
        return self.client.request(BATCH_COMMODITY_QUOTES, **params)

    def get_crypto_quotes(self, short: bool | None = None) -> list[BatchQuote]:
        """Get batch quotes for all cryptocurrencies

        Args:
            short: Whether to return short quote data

        Returns:
            List of quotes for all cryptocurrencies
        """
        params: dict[str, object] = {}
        if short is not None:
            params["short"] = short
        return self.client.request(BATCH_CRYPTO_QUOTES, **params)

    def get_forex_quotes(self, short: bool | None = None) -> list[BatchQuote]:
        """Get batch quotes for all forex pairs

        Args:
            short: Whether to return short quote data

        Returns:
            List of quotes for all forex pairs
        """
        params: dict[str, object] = {}
        if short is not None:
            params["short"] = short
        return self.client.request(BATCH_FOREX_QUOTES, **params)

    def get_index_quotes(self, short: bool | None = None) -> list[BatchQuote]:
        """Get batch quotes for all market indexes

        Args:
            short: Whether to return short quote data

        Returns:
            List of quotes for all market indexes
        """
        params: dict[str, object] = {}
        if short is not None:
            params["short"] = short
        return self.client.request(BATCH_INDEX_QUOTES, **params)

    def get_market_caps(self, symbols: list[str]) -> list[BatchMarketCap]:
        """Get market capitalization for multiple symbols

        Args:
            symbols: List of stock symbols

        Returns:
            List of market cap data for each symbol
        """
        return self.client.request(BATCH_MARKET_CAP, symbols=",".join(symbols))

    def get_profile_bulk(self, part: str) -> list[CompanyProfile]:
        """Get company profile data in bulk"""
        raw = cast(bytes, self.client.request(PROFILE_BULK, part=part))
        return self._parse_csv_models(raw, CompanyProfile)

    def get_dcf_bulk(self) -> list[DCF]:
        """Get discounted cash flow valuations in bulk"""
        raw = cast(bytes, self.client.request(DCF_BULK))
        rows = self._parse_csv_rows(raw)
        for row in rows:
            if "Stock Price" in row and "stockPrice" not in row:
                row["stockPrice"] = row.pop("Stock Price")
        return [DCF.model_validate(row) for row in rows]

    def get_rating_bulk(self) -> list[CompanyRating]:
        """Get stock ratings in bulk"""
        raw = cast(bytes, self.client.request(RATING_BULK))
        return self._parse_csv_models(raw, CompanyRating)

    def get_scores_bulk(self) -> list[FinancialScore]:
        """Get financial scores in bulk"""
        raw = cast(bytes, self.client.request(SCORES_BULK))
        return self._parse_csv_models(raw, FinancialScore)

    def get_ratios_ttm_bulk(self) -> list[FinancialRatiosTTM]:
        """Get trailing twelve month financial ratios in bulk"""
        raw = cast(bytes, self.client.request(RATIOS_TTM_BULK))
        return self._parse_csv_models(raw, FinancialRatiosTTM)

    def get_price_target_summary_bulk(self) -> list[PriceTargetSummary]:
        """Get bulk price target summaries"""
        raw = cast(bytes, self.client.request(PRICE_TARGET_SUMMARY_BULK))
        return self._parse_csv_models(raw, PriceTargetSummary)

    def get_etf_holder_bulk(self, part: str) -> list[ETFHolding]:
        """Get bulk ETF holdings"""
        raw = cast(bytes, self.client.request(ETF_HOLDER_BULK, part=part))
        return self._parse_csv_models(raw, ETFHolding)

    def get_upgrades_downgrades_consensus_bulk(
        self,
    ) -> list[UpgradeDowngradeConsensus]:
        """Get bulk upgrades/downgrades consensus data"""
        raw = cast(bytes, self.client.request(UPGRADES_DOWNGRADES_CONSENSUS_BULK))
        rows = [row for row in self._parse_csv_rows(raw) if row.get("symbol")]
        return [UpgradeDowngradeConsensus.model_validate(row) for row in rows]

    def get_key_metrics_ttm_bulk(self) -> list[KeyMetricsTTM]:
        """Get bulk trailing twelve month key metrics"""
        raw = cast(bytes, self.client.request(KEY_METRICS_TTM_BULK))
        return self._parse_csv_models(raw, KeyMetricsTTM)

    def get_peers_bulk(self) -> list[PeersBulk]:
        """Get bulk peer lists"""
        raw = cast(bytes, self.client.request(PEERS_BULK))
        return self._parse_csv_models(raw, PeersBulk)

    def get_earnings_surprises_bulk(self, year: int) -> list[EarningsSurpriseBulk]:
        """Get bulk earnings surprises for a given year"""
        raw = cast(bytes, self.client.request(EARNINGS_SURPRISES_BULK, year=year))
        return self._parse_csv_models(raw, EarningsSurpriseBulk)

    def get_income_statement_bulk(
        self, year: int, period: str
    ) -> list[IncomeStatement]:
        """Get bulk income statements"""
        raw = cast(
            bytes,
            self.client.request(INCOME_STATEMENT_BULK, year=year, period=period),
        )
        return self._parse_csv_models(raw, IncomeStatement)

    def get_income_statement_growth_bulk(
        self, year: int, period: str
    ) -> list[FinancialGrowth]:
        """Get bulk income statement growth data"""
        raw = cast(
            bytes,
            self.client.request(INCOME_STATEMENT_GROWTH_BULK, year=year, period=period),
        )
        return self._parse_csv_models(raw, FinancialGrowth)

    def get_balance_sheet_bulk(self, year: int, period: str) -> list[BalanceSheet]:
        """Get bulk balance sheet statements"""
        raw = cast(
            bytes,
            self.client.request(BALANCE_SHEET_STATEMENT_BULK, year=year, period=period),
        )
        return self._parse_csv_models(raw, BalanceSheet)

    def get_balance_sheet_growth_bulk(
        self, year: int, period: str
    ) -> list[FinancialGrowth]:
        """Get bulk balance sheet growth data"""
        raw = cast(
            bytes,
            self.client.request(
                BALANCE_SHEET_STATEMENT_GROWTH_BULK, year=year, period=period
            ),
        )
        return self._parse_csv_models(raw, FinancialGrowth)

    def get_cash_flow_bulk(self, year: int, period: str) -> list[CashFlowStatement]:
        """Get bulk cash flow statements"""
        raw = cast(
            bytes,
            self.client.request(CASH_FLOW_STATEMENT_BULK, year=year, period=period),
        )
        return self._parse_csv_models(raw, CashFlowStatement)

    def get_cash_flow_growth_bulk(
        self, year: int, period: str
    ) -> list[FinancialGrowth]:
        """Get bulk cash flow growth data"""
        raw = cast(
            bytes,
            self.client.request(
                CASH_FLOW_STATEMENT_GROWTH_BULK, year=year, period=period
            ),
        )
        return self._parse_csv_models(raw, FinancialGrowth)

    def get_eod_bulk(self, target_date: date | str) -> list[EODBulk]:
        """Get bulk end-of-day prices"""
        date_param = (
            target_date.strftime("%Y-%m-%d")
            if isinstance(target_date, date)
            else target_date
        )
        raw = cast(bytes, self.client.request(EOD_BULK, date=date_param))
        return self._parse_csv_models(raw, EODBulk)
