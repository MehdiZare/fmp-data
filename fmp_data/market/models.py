# fmp_data/market/models.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Quote(BaseModel):
    """Real-time stock quote data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")
    price: float = Field(description="Current price")
    change_percentage: float = Field(
        alias="changesPercentage", description="Price change percentage"
    )
    change: float = Field(description="Price change")
    day_low: float = Field(alias="dayLow", description="Day low price")
    day_high: float = Field(alias="dayHigh", description="Day high price")
    year_high: float = Field(alias="yearHigh", description="52-week high")
    year_low: float = Field(alias="yearLow", description="52-week low")
    market_cap: float = Field(alias="marketCap", description="Market capitalization")
    price_avg_50: float = Field(alias="priceAvg50", description="50-day average price")
    price_avg_200: float = Field(
        alias="priceAvg200", description="200-day average price"
    )
    volume: int = Field(description="Trading volume")
    avg_volume: int = Field(alias="avgVolume", description="Average volume")
    open: float = Field(description="Opening price")
    previous_close: float = Field(
        alias="previousClose", description="Previous close price"
    )
    eps: float = Field(description="Earnings per share")
    pe: float = Field(description="Price to earnings ratio")
    timestamp: datetime = Field(description="Quote timestamp")


class SimpleQuote(BaseModel):
    """Simple stock quote data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    price: float = Field(description="Current price")
    volume: int = Field(description="Trading volume")


class HistoricalPrice(BaseModel):
    """Historical price data point"""

    model_config = ConfigDict(populate_by_name=True)

    date: datetime = Field(description="Date of the price data")
    open: float = Field(description="Opening price")
    high: float = Field(description="High price")
    low: float = Field(description="Low price")
    close: float = Field(description="Closing price")
    adj_close: float = Field(alias="adjClose", description="Adjusted closing price")
    volume: int = Field(description="Trading volume")
    unadjusted_volume: int = Field(
        alias="unadjustedVolume", description="Unadjusted volume"
    )
    change: float = Field(description="Price change")
    change_percent: float = Field(
        alias="changePercent", description="Price change percentage"
    )
    vwap: float = Field(description="Volume weighted average price")
    label: str = Field(description="Date label")
    change_over_time: float = Field(
        alias="changeOverTime", description="Change over time"
    )


class HistoricalData(BaseModel):
    """Model to parse the full historical data response"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    historical: list[HistoricalPrice] = Field(
        description="List of historical price data"
    )

    @classmethod
    def parse_api_response(cls, data: dict):
        """Parse raw API response into validated HistoricalData model."""
        # Ensure historical data is validated
        historical_prices = [
            HistoricalPrice(**item) for item in data.get("historical", [])
        ]
        return cls(symbol=data["symbol"], historical=historical_prices)


class IntradayPrice(BaseModel):
    """Intraday price data point"""

    model_config = ConfigDict(populate_by_name=True)

    date: datetime = Field(description="Date and time")
    open: float = Field(description="Opening price")
    low: float = Field(description="Low price")
    high: float = Field(description="High price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")


class StockMarketHours(BaseModel):
    """Opening and closing hours of the stock market"""

    openingHour: str = Field(description="Opening hour of the market")
    closingHour: str = Field(description="Closing hour of the market")


class StockMarketHoliday(BaseModel):
    """Stock market holiday for a specific year"""

    year: int = Field(description="Year of the holiday schedule")
    holidays: dict[str, str] = Field(description="Mapping of holiday names to dates")

    @classmethod
    def from_api_data(cls, data):
        if not isinstance(data, dict):
            raise ValueError(
                f"Expected a dictionary but got {type(data).__name__}: {data}"
            )

        # Extract the year
        year = data.get("year")
        if year is None:
            raise ValueError("Missing 'year' field in data")

        # Aggregate holidays into a dictionary
        holidays = {}
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

    model_config = ConfigDict(populate_by_name=True)

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

    def __init__(self, **data):
        """Override the default initialization to preprocess API data."""
        # Process stockMarketHolidays
        holidays = data.get("stockMarketHolidays", [])
        if holidays:
            data["stockMarketHolidays"] = [
                StockMarketHoliday.from_api_data(h) for h in holidays
            ]

        # Initialize the base model with processed data
        super().__init__(**data)


class MarketCapitalization(BaseModel):
    """Market capitalization data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    date: datetime = Field(description="Date")
    market_cap: float = Field(alias="marketCap", description="Market capitalization")


class MarketMover(BaseModel):
    """Market mover (gainer/loser) data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")
    change: float = Field(description="Price change")
    price: float = Field(description="Current price")
    change_percentage: float = Field(
        alias="changesPercentage", description="Price change percentage"
    )


class SectorPerformance(BaseModel):
    """Sector performance data"""

    model_config = ConfigDict(populate_by_name=True)

    sector: str = Field(description="Sector name")
    change_percentage: float = Field(
        alias="changesPercentage", description="Change percentage as a float"
    )

    @field_validator("change_percentage", mode="before")
    def parse_percentage(cls, value):
        """Convert percentage string to a float."""
        if isinstance(value, str) and value.endswith("%"):
            try:
                return float(value.strip("%")) / 100
            except ValueError as e:
                raise ValueError(f"Invalid percentage format: {value}") from e
        raise ValueError(f"Expected a percentage string, got: {value}")


class PrePostMarketQuote(BaseModel):
    """Pre/Post market quote data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    timestamp: datetime = Field(description="Quote timestamp")
    price: float = Field(description="Current price")
    volume: int = Field(description="Trading volume")
    session: str = Field(description="Trading session (pre/post)")
