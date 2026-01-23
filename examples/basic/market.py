"""
Basic market data example.
Shows real-time quotes, historical prices, market movers, and market status.
"""

from datetime import date

from fmp_data import FMPDataClient


def main():
    # Initialize client with context manager
    with FMPDataClient.from_env() as client:
        # Get real-time quote
        quote = client.company.get_quote("AAPL")
        print(f"Current price: ${quote.price}")

        # Get historical prices
        historical_prices = client.company.get_historical_prices(
            symbol="AAPL", from_date=date(2024, 1, 1), to_date=date(2024, 3, 1)
        )
        print(f"Historical data points: {len(historical_prices.historical)}")

        # Get market gainers
        gainers = client.market.get_gainers()
        print(f"Top gainer: {gainers[0].symbol if gainers else 'N/A'}")

        # Get sector performance
        sector_perf = client.market.get_sector_performance()
        print(f"Sectors: {len(sector_perf)}")

        # Check market hours
        market_hours = client.market.get_market_hours()
        print(f"Market is open: {market_hours.is_market_open}")

    # Client automatically closed after with block


if __name__ == "__main__":
    main()
