# client.py
import warnings

from pydantic import ValidationError as PydanticValidationError

from .base import BaseClient
from .company.client import CompanyClient
from .config import ClientConfig, LoggingConfig, LogHandlerConfig
from .exceptions import ConfigError
from .logger import FMPLogger


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
        # pylint: disable=line-too-long
        """
        Initialize FMP Data client

        Args:
            api_key: Optional API key.
            If not provided, will look for FMP_API_KEY env variable
            timeout: Request timeout in seconds
            max_retries: Maximum number of request retries
            base_url: FMP API base URL
            config: Optional pre-configured ClientConfig instance
            debug: Enable debug logging if True

        Raises:
            ConfigError: If api_key is not provided and not found in environment
        """
        self._initialized = False
        self._company = None
        self._logger = None
        # pylint: disable=line-too-long

        try:
            if config is not None:
                self._config = config
            else:
                # Create default logging config based on debug parameter
                logging_config = LoggingConfig(
                    level="DEBUG" if debug else "INFO",
                    handlers={
                        "console": LogHandlerConfig(
                            class_name="StreamHandler",
                            level="DEBUG" if debug else "INFO",
                            format=(
                                "%(asctime)s - %(levelname)s - "
                                "%(name)s - %(message)s"
                            ),
                        )
                    },
                )

                try:
                    self._config = ClientConfig(
                        api_key=api_key,
                        timeout=timeout,
                        max_retries=max_retries,
                        base_url=base_url,
                        logging=logging_config,
                    )
                except PydanticValidationError as e:
                    raise ConfigError("Invalid client configuration") from e

            # Initialize the FMPLogger with our configuration
            FMPLogger().configure(self._config.logging)
            self._logger = FMPLogger().get_logger(__name__)

            # Initialize base client
            super().__init__(self._config)
            self._initialized = True

        except Exception as e:
            # Ensure we have a logger for error reporting
            if not hasattr(self, "_logger") or self._logger is None:
                self._logger = FMPLogger().get_logger(__name__)
            self._logger.error(f"Failed to initialize client: {str(e)}")
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

    def __enter__(self):
        """Context manager enter"""
        if not self._initialized:
            self._setup_http_client()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        if exc_type is not None and self.logger:
            self.logger.error(
                "Error in context manager",
                extra={"error_type": exc_type.__name__, "error": str(exc_val)},
                exc_info=(exc_type, exc_val, exc_tb),
            )

    def close(self):
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
                logger.error(f"Error during cleanup: {str(e)}")

    def __del__(self):
        """Destructor that ensures resources are cleaned up"""
        try:
            if hasattr(self, "_initialized") and self._initialized:
                self.close()
        except (Exception, BaseException) as e:
            # Suppress any errors during cleanup
            warnings.warn(
                f"Error during FMPDataClient cleanup: {str(e)}",
                ResourceWarning,
                stacklevel=2,
            )
