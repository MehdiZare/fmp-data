from datetime import date

from fmp_data import FMPDataClient

# Initialize client
client = FMPDataClient.from_env()

# Get real-time quote
quote = client.company.get_quote("AAPL")

# Get historical prices
historical_prices = client.company.get_historical_prices(
    symbol="AAPL", from_date=date(2024, 1, 1), to_date=date(2024, 3, 1)
)

# Get market gainers
gainers = client.market.get_gainers()

# Get sector performance
sector_perf = client.market.get_sector_performance()

# Check market hours
market_hours = client.market.get_market_hours()
