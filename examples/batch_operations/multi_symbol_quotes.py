"""
Example demonstrating batch operations for multiple symbols.
Shows how to efficiently fetch quotes for multiple stocks at once.
"""

from fmp_data import FMPDataClient


def main() -> None:
    with FMPDataClient.from_env() as client:
        # Get quotes for multiple symbols at once
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        quotes = client.batch.get_quotes(symbols)

        print("\n=== Multi-Symbol Quotes ===\n")
        for quote in quotes:
            price = quote.price if quote.price is not None else 0.0
            change_pct = (
                quote.changes_percentage
                if quote.changes_percentage is not None
                else 0.0
            )
            volume = quote.volume if quote.volume is not None else 0
            print(
                f"{quote.symbol:6} | ${price:8.2f} | "
                f"{change_pct:+6.2f}% | Vol: {volume:,}"
            )

        # Get all ETF quotes
        print("\n=== Sample ETF Quotes ===\n")
        etf_quotes = client.batch.get_etf_quotes()
        for etf in etf_quotes[:10]:  # Show first 10
            price = etf.price if etf.price is not None else 0.0
            change_pct = (
                etf.changes_percentage if etf.changes_percentage is not None else 0.0
            )
            print(f"{etf.symbol:6} | ${price:8.2f} | {change_pct:+6.2f}%")

        # Get market caps for portfolio
        print("\n=== Portfolio Market Caps ===\n")
        portfolio = ["AAPL", "MSFT", "GOOGL"]
        market_caps = client.batch.get_market_caps(portfolio)
        for cap in market_caps:
            market_cap = cap.market_cap if cap.market_cap is not None else 0.0
            print(f"{cap.symbol:6} | Market Cap: ${market_cap:,.0f}")


if __name__ == "__main__":
    main()
