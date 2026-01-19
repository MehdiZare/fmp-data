# fmp_data/batch/client.py
from fmp_data.base import EndpointGroup
from fmp_data.batch.endpoints import (
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
)
from fmp_data.batch.models import (
    AftermarketQuote,
    AftermarketTrade,
    BatchMarketCap,
    BatchQuote,
    BatchQuoteShort,
)


class BatchClient(EndpointGroup):
    """Client for batch data endpoints

    Provides methods to retrieve data for multiple symbols or entire asset classes
    in a single API call.
    """

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

    def get_exchange_quotes(self, exchange: str) -> list[BatchQuote]:
        """Get quotes for all stocks on a specific exchange

        Args:
            exchange: Exchange code (e.g., NYSE, NASDAQ)

        Returns:
            List of quotes for all stocks on the exchange
        """
        return self.client.request(BATCH_EXCHANGE_QUOTE, exchange=exchange)

    def get_mutualfund_quotes(self) -> list[BatchQuote]:
        """Get batch quotes for all mutual funds

        Returns:
            List of quotes for all mutual funds
        """
        return self.client.request(BATCH_MUTUALFUND_QUOTES)

    def get_etf_quotes(self) -> list[BatchQuote]:
        """Get batch quotes for all ETFs

        Returns:
            List of quotes for all ETFs
        """
        return self.client.request(BATCH_ETF_QUOTES)

    def get_commodity_quotes(self) -> list[BatchQuote]:
        """Get batch quotes for all commodities

        Returns:
            List of quotes for all commodities
        """
        return self.client.request(BATCH_COMMODITY_QUOTES)

    def get_crypto_quotes(self) -> list[BatchQuote]:
        """Get batch quotes for all cryptocurrencies

        Returns:
            List of quotes for all cryptocurrencies
        """
        return self.client.request(BATCH_CRYPTO_QUOTES)

    def get_forex_quotes(self) -> list[BatchQuote]:
        """Get batch quotes for all forex pairs

        Returns:
            List of quotes for all forex pairs
        """
        return self.client.request(BATCH_FOREX_QUOTES)

    def get_index_quotes(self) -> list[BatchQuote]:
        """Get batch quotes for all market indexes

        Returns:
            List of quotes for all market indexes
        """
        return self.client.request(BATCH_INDEX_QUOTES)

    def get_market_caps(self, symbols: list[str]) -> list[BatchMarketCap]:
        """Get market capitalization for multiple symbols

        Args:
            symbols: List of stock symbols

        Returns:
            List of market cap data for each symbol
        """
        return self.client.request(BATCH_MARKET_CAP, symbols=",".join(symbols))
