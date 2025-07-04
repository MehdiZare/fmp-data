# fmp_data/market/models.py
from datetime import datetime
from typing import Any
import warnings

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.alias_generators import to_camel

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


class ExchangeSymbol(BaseModel):
    """Exchange symbol information matching actual API response"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Stock symbol")
    name: str | None = Field(None, description="Company name")
    price: float | None = Field(None, description="Current price")
    change_percentage: float | None = Field(
        None, alias="changesPercentage", description="Price change percentage"
    )
    change: float | None = Field(None, description="Price change")
    day_low: float | None = Field(None, alias="dayLow", description="Day low price")
    day_high: float | None = Field(None, alias="dayHigh", description="Day high price")
    year_high: float | None = Field(None, alias="yearHigh", description="52-week high")
    year_low: float | None = Field(None, alias="yearLow", description="52-week low")
    market_cap: float | None = Field(
        None, alias="marketCap", description="Market capitalization"
    )
    price_avg_50: float | None = Field(None, description="50-day moving average")
    price_avg_200: float | None = Field(None, description="200-day moving average")
    exchange: str | None = Field(None, description="Stock exchange")
    volume: float | None = Field(None, description="Trading volume")
    avg_volume: float | None = Field(None, description="Average volume")
    open: float | None = Field(None, description="Opening price")
    previous_close: float | None = Field(None, description="Previous closing price")
    eps: float | None = Field(None, description="Earnings per share")
    pe: float | None = Field(None, description="Price to earnings ratio")
    earnings_announcement: datetime | None = Field(None, alias="earningsAnnouncement")
    shares_outstanding: float | None = Field(None, description="Shares outstanding")
    timestamp: int | None = Field(None, description="Quote timestamp")

    @classmethod
    @model_validator(mode="before")
    def validate_data(cls, data: Any) -> dict[str, Any]:
        """
        Validate data and convert invalid values to None with warnings.

        Args:
            data: Raw data to validate

        Returns:
            Dict[str, Any]: Cleaned data with invalid values converted to None
        """
        if not isinstance(data, dict):
            # Convert non-dict data to an empty dict or raise an error
            warnings.warn(
                f"Expected dict data but got {type(data)}. Converting to empty dict.",
                stacklevel=2,
            )
            return {}

        cleaned_data: dict[str, Any] = {}
        for field_name, field_value in data.items():
            try:
                # Check if field exists and is a float type
                field_info = cls.model_fields.get(field_name)
                if field_info and field_info.annotation in (float, float | None):
                    try:
                        if field_value is not None:
                            cleaned_data[field_name] = float(field_value)
                        else:
                            cleaned_data[field_name] = None
                    except (ValueError, TypeError):
                        warnings.warn(
                            f"Invalid value for {field_name}: "
                            f"{field_value}. Setting to None",
                            stacklevel=2,
                        )
                        cleaned_data[field_name] = None
                else:
                    cleaned_data[field_name] = field_value
            except Exception as e:
                warnings.warn(
                    f"Error processing field {field_name}: {e!s}. Setting to None",
                    stacklevel=2,
                )
                cleaned_data[field_name] = None

        return cleaned_data


class StockMarketHours(BaseModel):
    """Opening and closing hours of the stock market"""

    model_config = default_model_config
    openingHour: str = Field(description="Opening hour of the market")
    closingHour: str = Field(description="Closing hour of the market")


class StockMarketHoliday(BaseModel):
    """Stock market holiday for a specific year"""

    model_config = default_model_config

    year: int = Field(description="Year of the holiday schedule")
    holidays: dict[str, str] = Field(description="Mapping of holiday names to dates")

    @classmethod
    def from_api_data(cls, data: dict[str, Any]) -> "StockMarketHoliday":
        """
        Create a StockMarketHoliday instance from API response data.

        Args:
            data: Dictionary containing year and holidays data from the API

        Returns:
            StockMarketHoliday: Initialized instance with parsed holiday data

        Raises:
            ValueError: If data is malformed or missing required fields
        """
        if not isinstance(data, dict):
            raise ValueError(
                f"Expected a dictionary but got {type(data).__name__}: {data}"
            )

        # Extract the year
        year = data.get("year")
        if year is None:
            raise ValueError("Missing 'year' field in data")

        # Aggregate holidays into a dictionary
        holidays: dict[str, str] = {}
        for holiday in data.get("holidays", []):
            if not isinstance(holiday, dict):
                raise ValueError(
                    f"Expected a dictionary for "
                    f"holiday but got {type(holiday).__name__}: {holiday}"
                )

            name = holiday.get("name")
            date = holiday.get("date")
            if not name or not date:
                raise ValueError(
                    f"Holiday entry must have 'name' and 'date': {holiday}"
                )

            holidays[name] = date

        return cls(year=year, holidays=holidays)


class MarketHours(BaseModel):
    """Market trading hours information"""

    model_config = default_model_config

    stockExchangeName: str = Field(description="Stock exchange name")
    stockMarketHours: StockMarketHours = Field(description="Market hours")
    stockMarketHolidays: list[StockMarketHoliday] = Field(
        description="List of market holidays"
    )
    isTheStockMarketOpen: bool = Field(
        description="Whether the stock market is currently open"
    )
    isTheEuronextMarketOpen: bool = Field(description="Whether Euronext market is open")
    isTheForexMarketOpen: bool = Field(description="Whether Forex market is open")
    isTheCryptoMarketOpen: bool = Field(description="Whether Crypto market is open")

    def __init__(self, **data: Any) -> None:
        """
        Override the default initialization to preprocess API data.

        Args:
            **data: Keyword arguments containing model data
        """
        # Process stockMarketHolidays
        holidays = data.get("stockMarketHolidays", [])
        if holidays:
            data["stockMarketHolidays"] = [
                StockMarketHoliday.from_api_data(h) for h in holidays
            ]

        # Initialize the base model with processed data
        super().__init__(**data)


class MarketMover(BaseModel):
    """Market mover (gainer/loser) data"""

    model_config = ConfigDict(
        populate_by_name=True, validate_assignment=True, extra="ignore"
    )

    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")
    change: float = Field(description="Price change")
    price: float = Field(description="Current price")
    change_percentage: float | None = Field(
        None, alias="changesPercentage", description="Price change percentage"
    )


class SectorPerformance(BaseModel):
    """Sector performance data"""

    model_config = default_model_config

    sector: str = Field(description="Sector name")
    change_percentage: float | None = Field(
        None, alias="changesPercentage", description="Change percentage as a float"
    )

    @field_validator("change_percentage", mode="before")
    def parse_percentage(cls, value: Any) -> float:
        """
        Convert percentage string to a float.

        Args:
            value: Value to parse, expected to be a string ending with '%'

        Returns:
            float: Parsed percentage value as decimal

        Raises:
            ValueError: If value cannot be parsed as a percentage
        """
        if isinstance(value, str) and value.endswith("%"):
            try:
                return float(value.strip("%")) / 100
            except ValueError as e:
                raise ValueError(f"Invalid percentage format: {value}") from e
        raise ValueError(f"Expected a percentage string, got: {value}")


class PrePostMarketQuote(BaseModel):
    """Pre/Post market quote data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    timestamp: datetime = Field(description="Quote timestamp")
    price: float = Field(description="Current price")
    volume: int = Field(description="Trading volume")
    session: str = Field(description="Trading session (pre/post)")


class CIKResult(BaseModel):
    """CIK search result"""

    model_config = default_model_config

    cik: str = Field(description="CIK number")
    name: str = Field(description="Company name")
    symbol: str = Field(description="Stock symbol")


class CUSIPResult(BaseModel):
    """CUSIP search result"""

    model_config = default_model_config

    cusip: str = Field(description="CUSIP number")
    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")


class ISINResult(BaseModel):
    """ISIN search result"""

    model_config = default_model_config

    isin: str = Field(description="ISIN number")
    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")


class AvailableIndex(BaseModel):
    """Market index information"""

    model_config = default_model_config

    symbol: str = Field(description="Index symbol")
    name: str = Field(description="Index name")
    currency: str = Field(description="Trading currency")
    stock_exchange: str = Field(alias="stockExchange", description="Stock exchange")
    exchange_short_name: str = Field(
        alias="exchangeShortName", description="Exchange short name"
    )


class CompanySearchResult(BaseModel):
    """Company search result"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol (ticker)")
    name: str = Field(description="Company name")
    currency: str | None = Field(None, description="Trading currency")
    stock_exchange: str | None = Field(None, description="Stock exchange")
    exchange_short_name: str | None = Field(None, description="Exchange short name")
