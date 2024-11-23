"""
Example demonstrating how to fetch various types of market data
using the FMP Data library.
Shows real-time quotes, historical data, market movers, and sector analysis.
"""

from datetime import datetime, timedelta

from fmp_data import FMPDataClient


def analyze_stock(client, symbol):
    """Get detailed stock information"""
    print(f"\n=== Stock Analysis: {symbol} ===")

    # Get real-time quote
    quote = client.market.get_quote(symbol)
    print(f"\nCurrent Price: ${quote.price:.2f}")
    print(f"Change: {quote.change_percentage:+.2f}%")
    print(f"Volume: {quote.volume:,}")
    print(f"52-Week Range: ${quote.year_low:.2f} - ${quote.year_high:.2f}")
    print(f"50-Day Avg: ${quote.price_avg_50:.2f}")
    print(f"200-Day Avg: ${quote.price_avg_200:.2f}")


def analyze_historical_data(client, symbol):
    """Analyze historical price data"""
    print(f"\n=== Historical Data Analysis: {symbol} ===")

    # Get 3 months of historical data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)

    prices = client.market.get_historical_prices(
        symbol=symbol,
        from_date=start_date.strftime("%Y-%m-%d"),
        to_date=end_date.strftime("%Y-%m-%d"),
    )

    # Calculate basic statistics
    closes = [p.close for p in prices]
    if closes:
        print("\nLast 90 Days Statistics:")
        print(f"Average Price: ${sum(closes) / len(closes):.2f}")
        print(f"Highest Price: ${max(closes):.2f}")
        print(f"Lowest Price: ${min(closes):.2f}")


def get_market_movers(client):
    """Get market gainers, losers, and most active stocks"""
    print("\n=== Market Movers ===")

    # Get top gainers
    gainers = client.market.get_gainers()
    print("\nTop Gainers:")
    for gainer in gainers[:3]:  # Show top 3
        print(
            f"{gainer.symbol}: {gainer.change_percentage:+.2f}% (${gainer.price:.2f})"
        )

    # Get top losers
    losers = client.market.get_losers()
    print("\nTop Losers:")
    for loser in losers[:3]:  # Show top 3
        print(f"{loser.symbol}: {loser.change_percentage:+.2f}% (${loser.price:.2f})")

    # Get most active
    active = client.market.get_most_active()
    print("\nMost Active:")
    for stock in active[:3]:  # Show top 3
        print(f"{stock.symbol}: Volume {stock.volume:,} (${stock.price:.2f})")


def analyze_sectors(client):
    """Analyze sector performance"""
    print("\n=== Sector Performance ===")

    sectors = client.market.get_sector_performance()
    for sector in sectors:
        print(f"{sector.sector}: {sector.change_percentage:+.2f}%")


def check_market_status(client):
    """Check market hours and status"""
    print("\n=== Market Status ===")

    status = client.market.get_market_hours()
    print(f"Stock Market Open: {status.isTheStockMarketOpen}")
    print(f"Forex Market Open: {status.isTheForexMarketOpen}")
    print(f"Crypto Market Open: {status.isTheCryptoMarketOpen}")

    # Get pre/post market data if available
    try:
        pre_post = client.market.get_pre_post_market()
        if pre_post:
            print("\nPre/Post Market Activity:")
            for quote in pre_post[:3]:  # Show first 3 entries
                print(f"{quote.symbol}: ${quote.price:.2f} ({quote.session})")
    except Exception as e:
        print(f"Pre/post market data not available: {e}")


def main():
    # Initialize client using environment variables
    client = FMPDataClient.from_env()

    try:
        # Analyze specific stock
        analyze_stock(client, "AAPL")

        # Get historical data
        analyze_historical_data(client, "AAPL")

        # Get market movers
        get_market_movers(client)

        # Analyze sectors
        analyze_sectors(client)

        # Check market status
        check_market_status(client)

    except Exception as e:
        print(f"Error during market analysis: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
