# fmp_data/client.py
import logging
import types
import warnings

from pydantic import ValidationError as PydanticValidationError

from fmp_data.alternative import AlternativeMarketsClient
from fmp_data.base import BaseClient
from fmp_data.company.client import CompanyClient
from fmp_data.config import ClientConfig, LoggingConfig, LogHandlerConfig
from fmp_data.economics import EconomicsClient
from fmp_data.exceptions import ConfigError
from fmp_data.fundamental import FundamentalClient
from fmp_data.institutional import InstitutionalClient
from fmp_data.intelligence import MarketIntelligenceClient
from fmp_data.investment import InvestmentClient
from fmp_data.logger import FMPLogger
from fmp_data.market import MarketClient
from fmp_data.technical import TechnicalClient


class FMPDataClient(BaseClient):
    """Main client for FMP Data API"""

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = 30,
        max_retries: int = 3,
        base_url: str = "https://financialmodelingprep.com/api",
        config: ClientConfig | None = None,
        debug: bool = False,
    ):
        self._initialized: bool = False
        self._logger: logging.Logger | None = None
        self._company: CompanyClient | None = None
        self._market: MarketClient | None = None
        self._fundamental: FundamentalClient | None = None
        self._technical: TechnicalClient | None = None
        self._intelligence: MarketIntelligenceClient | None = None
        self._institutional: InstitutionalClient | None = None
        self._investment: InvestmentClient | None = None
        self._alternative: AlternativeMarketsClient | None = None
        self._economics: EconomicsClient | None = None

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
                        api_key=api_key or "",  # Handle None case
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

        except Exception as e:
            if not hasattr(self, "_logger") or self._logger is None:
                self._logger = FMPLogger().get_logger(__name__)
            self._logger.error(f"Failed to initialize client: {e!s}")
            raise

    @classmethod
    def from_env(cls, debug: bool = False) -> "FMPDataClient":
        """
        Create client instance from environment variables

        Args:
            debug: Enable debug logging if True
        """
        config = ClientConfig.from_env()
        if debug:
            config.logging.level = "DEBUG"
            if "console" in config.logging.handlers:
                config.logging.handlers["console"].level = "DEBUG"

        return cls(config=config)

    def __enter__(self) -> "FMPDataClient":
        """Context manager enter"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """
        Context manager exit

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred
        """
        self.close()
        if exc_type is not None and exc_val is not None and self.logger:
            self.logger.error(
                "Error in context manager",
                extra={"error_type": exc_type.__name__, "error": str(exc_val)},
                exc_info=True,  # Use True instead of tuple to let logger handle it
            )

    def close(self) -> None:
        """Clean up resources"""
        try:
            if hasattr(self, "client") and self.client is not None:
                self.client.close()
            if hasattr(self, "_initialized") and self._initialized:
                logger = getattr(self, "_logger", None)
                if logger is not None:
                    logger.info("FMP Data client closed")
        except Exception as e:
            # Log if possible, but don't raise
            logger = getattr(self, "_logger", None)
            if logger is not None:
                logger.error(f"Error during cleanup: {e!s}")

    def __del__(self) -> None:
        """Destructor that ensures resources are cleaned up"""
        try:
            if hasattr(self, "_initialized") and self._initialized:
                self.close()
        except (Exception, BaseException) as e:
            # Suppress any errors during cleanup
            warnings.warn(
                f"Error during FMPDataClient cleanup: {e!s}",
                ResourceWarning,
                stacklevel=2,
            )

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
    def company(self) -> CompanyClient:
        """Get or create the company client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._company is None:
            if self.logger:
                self.logger.debug("Initializing company client")
            self._company = CompanyClient(self)
        return self._company

    @property
    def market(self) -> MarketClient:
        """Get or create the market data client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._market is None:
            if self.logger:
                self.logger.debug("Initializing market client")
            self._market = MarketClient(self)
        return self._market

    @property
    def fundamental(self) -> FundamentalClient:
        """Get or create the fundamental client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._fundamental is None:
            if self.logger:
                self.logger.debug("Initializing fundamental client")
            self._fundamental = FundamentalClient(self)
        return self._fundamental

    @property
    def technical(self) -> TechnicalClient:
        """Get or create the technical analysis client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._technical is None:
            if self.logger:
                self.logger.debug("Initializing technical analysis client")
            self._technical = TechnicalClient(self)
        return self._technical

    @property
    def intelligence(self) -> MarketIntelligenceClient:
        """Get or create the market intelligence client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._intelligence is None:
            if self.logger:
                self.logger.debug("Initializing market intelligence client")
            self._intelligence = MarketIntelligenceClient(self)
        return self._intelligence

    @property
    def institutional(self) -> InstitutionalClient:
        """Get or create the institutional activity client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._institutional is None:
            if self.logger:
                self.logger.debug("Initializing institutional activity client")
            self._institutional = InstitutionalClient(self)
        return self._institutional

    @property
    def investment(self) -> InvestmentClient:
        """Get or create the investment products client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._investment is None:
            if self.logger:
                self.logger.debug("Initializing investment products client")
            self._investment = InvestmentClient(self)
        return self._investment

    @property
    def alternative(self) -> AlternativeMarketsClient:
        """Get or create the alternative markets client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._alternative is None:
            if self.logger:
                self.logger.debug("Initializing alternative markets client")
            self._alternative = AlternativeMarketsClient(self)
        return self._alternative

    @property
    def economics(self) -> EconomicsClient:
        """Get or create the economics data client instance"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")

        if self._economics is None:
            if self.logger:
                self.logger.debug("Initializing economics data client")
            self._economics = EconomicsClient(self)
        return self._economics
