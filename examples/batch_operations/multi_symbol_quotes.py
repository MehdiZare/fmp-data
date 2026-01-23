"""
Example demonstrating batch operations for multiple symbols.
Shows how to efficiently fetch quotes for multiple stocks at once.
"""

from fmp_data import FMPDataClient


def main():
    with FMPDataClient.from_env() as client:
        # Get quotes for multiple symbols at once
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        quotes = client.batch.get_quotes(symbols)

        print("\n=== Multi-Symbol Quotes ===\n")
        for quote in quotes:
            print(
                f"{quote.symbol:6} | ${quote.price:8.2f} | "
                f"{quote.changes_percentage:+6.2f}% | Vol: {quote.volume:,}"
            )

        # Get all ETF quotes
        print("\n=== Sample ETF Quotes ===\n")
        etf_quotes = client.batch.get_etf_quotes()
        for etf in etf_quotes[:10]:  # Show first 10
            print(
                f"{etf.symbol:6} | ${etf.price:8.2f} | {etf.changes_percentage:+6.2f}%"
            )

        # Get market caps for portfolio
        print("\n=== Portfolio Market Caps ===\n")
        portfolio = ["AAPL", "MSFT", "GOOGL"]
        market_caps = client.batch.get_market_caps(portfolio)
        for cap in market_caps:
            print(f"{cap.symbol:6} | Market Cap: ${cap.market_cap:,.0f}")


if __name__ == "__main__":
    main()
