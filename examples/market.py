from fmp_data import FMPDataClient

# Initialize client
client = FMPDataClient.from_env()

# Get real-time quote
quote = client.market.get_quote("AAPL")

# Get historical prices
historical_prices = client.market.get_historical_prices(
    symbol="AAPL", from_date="2024-01-01", to_date="2024-03-01"
)

# Get market gainers
gainers = client.market.get_gainers()

# Get sector performance
sector_perf = client.market.get_sector_performance()

# Check market hours
market_hours = client.market.get_market_hours()
