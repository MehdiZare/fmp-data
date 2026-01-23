# fmp_data/async_client.py
"""Async client for FMP Data API.

This is the async counterpart to FMPDataClient. All endpoint methods are async
and have the same names as their sync equivalents (no _async suffix).

Example:
    async with AsyncFMPDataClient.from_env() as client:
        profile = await client.company.get_profile("AAPL")
        quote = await client.company.get_quote("AAPL")
"""

from __future__ import annotations

import logging
import types

from pydantic import ValidationError as PydanticValidationError

from fmp_data.alternative.async_client import AsyncAlternativeMarketsClient
from fmp_data.base import BaseClient
from fmp_data.batch.async_client import AsyncBatchClient
from fmp_data.company.async_client import AsyncCompanyClient
from fmp_data.config import ClientConfig, LoggingConfig, LogHandlerConfig
from fmp_data.economics.async_client import AsyncEconomicsClient
from fmp_data.exceptions import ConfigError
from fmp_data.fundamental.async_client import AsyncFundamentalClient
from fmp_data.index.async_client import AsyncIndexClient
from fmp_data.institutional.async_client import AsyncInstitutionalClient
from fmp_data.intelligence.async_client import AsyncMarketIntelligenceClient
from fmp_data.investment.async_client import AsyncInvestmentClient
from fmp_data.logger import FMPLogger
from fmp_data.market.async_client import AsyncMarketClient
from fmp_data.sec.async_client import AsyncSECClient
from fmp_data.technical.async_client import AsyncTechnicalClient
from fmp_data.transcripts.async_client import AsyncTranscriptsClient


class AsyncFMPDataClient(BaseClient):
    """Async client for FMP Data API.

    All sub-clients expose async methods without the _async suffix.

    Example:
        async with AsyncFMPDataClient.from_env() as client:
            profile = await client.company.get_profile("AAPL")
    """

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = 30,
        max_retries: int = 3,
        base_url: str = "https://financialmodelingprep.com",
        config: ClientConfig | None = None,
        debug: bool = False,
    ):
        self._initialized: bool = False
        self._logger: logging.Logger | None = None
        self._company: AsyncCompanyClient | None = None
        self._market: AsyncMarketClient | None = None
        self._fundamental: AsyncFundamentalClient | None = None
        self._technical: AsyncTechnicalClient | None = None
        self._intelligence: AsyncMarketIntelligenceClient | None = None
        self._institutional: AsyncInstitutionalClient | None = None
        self._investment: AsyncInvestmentClient | None = None
        self._alternative: AsyncAlternativeMarketsClient | None = None
        self._economics: AsyncEconomicsClient | None = None
        self._batch: AsyncBatchClient | None = None
        self._transcripts: AsyncTranscriptsClient | None = None
        self._sec: AsyncSECClient | None = None
        self._index: AsyncIndexClient | None = None

        if not api_key and (config is None or not config.api_key):
            raise ConfigError("Invalid client configuration: API key is required")

        try:
            if config is not None:
                self._config = config
            else:
                logging_config = LoggingConfig(
                    level="DEBUG" if debug else "INFO",
                    handlers={
                        "console": LogHandlerConfig(
                            class_name="StreamHandler",
                            level="DEBUG" if debug else "INFO",
                            format=(
                                "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
                            ),
                        )
                    },
                )

                try:
                    self._config = ClientConfig(
                        api_key=api_key or "",
                        timeout=timeout,
                        max_retries=max_retries,
                        base_url=base_url,
                        logging=logging_config,
                    )
                except PydanticValidationError as e:
                    raise ConfigError("Invalid client configuration") from e

            FMPLogger().configure(self._config.logging)
            self._logger = FMPLogger().get_logger(__name__)

            super().__init__(self._config)
            self._initialized = True

        except Exception:
            logger = getattr(self, "_logger", None)
            if logger is None:
                self._logger = FMPLogger().get_logger(__name__)
                logger = self._logger
            logger.exception("Failed to initialize async client")
            raise

    @classmethod
    def from_env(cls, debug: bool = False) -> AsyncFMPDataClient:
        """
        Create async client instance from environment variables

        Args:
            debug: Enable debug logging if True
        """
        config = ClientConfig.from_env()
        if debug:
            config.logging.level = "DEBUG"
            if "console" in config.logging.handlers:
                config.logging.handlers["console"].level = "DEBUG"

        return cls(config=config)

    async def __aenter__(self) -> AsyncFMPDataClient:
        """Async context manager enter"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Async context manager exit - closes all client resources"""
        await self.aclose()
        if exc_type is not None and exc_val is not None and self.logger:
            self.logger.error(
                "Error in async context manager",
                extra={"error_type": exc_type.__name__, "error": str(exc_val)},
                exc_info=True,
            )

    async def aclose(self) -> None:
        """Clean up all resources (both async and sync clients)."""
        try:
            # Close async client
            async_client = getattr(self, "_async_client", None)
            if async_client is not None and not async_client.is_closed:
                await async_client.aclose()
                self._async_client = None
            # Close sync client (might be used internally)
            client = getattr(self, "client", None)
            if client is not None:
                client.close()
            if getattr(self, "_initialized", False):
                logger = getattr(self, "_logger", None)
                if logger is not None:
                    logger.info("Async FMP Data client closed")
        except Exception:
            logger = getattr(self, "_logger", None)
            if logger is not None:
                logger.exception("Error during async cleanup")

    @property
    def logger(self) -> logging.Logger:
        """Get the logger instance, creating one if needed"""
        if self._logger is None:
            self._logger = FMPLogger().get_logger(self.__class__.__module__)
        return self._logger

    @logger.setter
    def logger(self, value: logging.Logger) -> None:
        """Set the logger instance"""
        self._logger = value

    @logger.deleter
    def logger(self) -> None:
        """Delete the logger instance"""
        self._logger = None

    @property
    def company(self) -> AsyncCompanyClient:
        """Get or create the async company client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._company is None:
            if self.logger:
                self.logger.debug("Initializing async company client")
            self._company = AsyncCompanyClient(self)
        return self._company

    @property
    def market(self) -> AsyncMarketClient:
        """Get or create the async market data client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._market is None:
            if self.logger:
                self.logger.debug("Initializing async market client")
            self._market = AsyncMarketClient(self)
        return self._market

    @property
    def fundamental(self) -> AsyncFundamentalClient:
        """Get or create the async fundamental client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._fundamental is None:
            if self.logger:
                self.logger.debug("Initializing async fundamental client")
            self._fundamental = AsyncFundamentalClient(self)
        return self._fundamental

    @property
    def technical(self) -> AsyncTechnicalClient:
        """Get or create the async technical analysis client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._technical is None:
            if self.logger:
                self.logger.debug("Initializing async technical analysis client")
            self._technical = AsyncTechnicalClient(self)
        return self._technical

    @property
    def intelligence(self) -> AsyncMarketIntelligenceClient:
        """Get or create the async market intelligence client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._intelligence is None:
            if self.logger:
                self.logger.debug("Initializing async market intelligence client")
            self._intelligence = AsyncMarketIntelligenceClient(self)
        return self._intelligence

    @property
    def institutional(self) -> AsyncInstitutionalClient:
        """Get or create the async institutional activity client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._institutional is None:
            if self.logger:
                self.logger.debug("Initializing async institutional activity client")
            self._institutional = AsyncInstitutionalClient(self)
        return self._institutional

    @property
    def investment(self) -> AsyncInvestmentClient:
        """Get or create the async investment products client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._investment is None:
            if self.logger:
                self.logger.debug("Initializing async investment products client")
            self._investment = AsyncInvestmentClient(self)
        return self._investment

    @property
    def alternative(self) -> AsyncAlternativeMarketsClient:
        """Get or create the async alternative markets client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._alternative is None:
            if self.logger:
                self.logger.debug("Initializing async alternative markets client")
            self._alternative = AsyncAlternativeMarketsClient(self)
        return self._alternative

    @property
    def economics(self) -> AsyncEconomicsClient:
        """Get or create the async economics data client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._economics is None:
            if self.logger:
                self.logger.debug("Initializing async economics data client")
            self._economics = AsyncEconomicsClient(self)
        return self._economics

    @property
    def batch(self) -> AsyncBatchClient:
        """Get or create the async batch data client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._batch is None:
            if self.logger:
                self.logger.debug("Initializing async batch data client")
            self._batch = AsyncBatchClient(self)
        return self._batch

    @property
    def transcripts(self) -> AsyncTranscriptsClient:
        """Get or create the async transcripts client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._transcripts is None:
            if self.logger:
                self.logger.debug("Initializing async transcripts client")
            self._transcripts = AsyncTranscriptsClient(self)
        return self._transcripts

    @property
    def sec(self) -> AsyncSECClient:
        """Get or create the async SEC filings client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._sec is None:
            if self.logger:
                self.logger.debug("Initializing async SEC client")
            self._sec = AsyncSECClient(self)
        return self._sec

    @property
    def index(self) -> AsyncIndexClient:
        """Get or create the async index constituents client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._index is None:
            if self.logger:
                self.logger.debug("Initializing async index client")
            self._index = AsyncIndexClient(self)
        return self._index
