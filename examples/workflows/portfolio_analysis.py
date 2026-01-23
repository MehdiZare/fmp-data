"""
Real-world workflow example: Portfolio analysis.
Demonstrates how to analyze a portfolio of stocks using various endpoints.
"""

from fmp_data import FMPDataClient


def analyze_portfolio(client, portfolio):
    """Analyze a portfolio of stocks."""
    print("\n" + "=" * 80)
    print("PORTFOLIO ANALYSIS REPORT")
    print("=" * 80)

    # Get quotes for all symbols
    quotes = client.batch.get_quotes(portfolio)

    portfolio_data = []

    print("\n--- Current Holdings ---\n")
    for quote in quotes:
        # Get company profile for additional context
        try:
            profile = client.company.get_profile(quote.symbol)
            sector = profile.sector if profile else "N/A"
        except Exception:
            sector = "N/A"

        holding_info = {
            "symbol": quote.symbol,
            "price": quote.price,
            "change": quote.changes_percentage,
            "market_cap": quote.market_cap,
            "sector": sector,
        }
        portfolio_data.append(holding_info)

        print(
            f"{quote.symbol:6} | ${quote.price:8.2f} | "
            f"{quote.changes_percentage:+6.2f}% | {sector}"
        )

    # Sector allocation
    print("\n--- Sector Allocation ---\n")
    sectors = {}
    for holding in portfolio_data:
        sector = holding["sector"]
        if sector in sectors:
            sectors[sector] += 1
        else:
            sectors[sector] = 1

    for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(portfolio_data)) * 100
        print(f"{sector}: {count} stocks ({percentage:.1f}%)")

    # Technical indicators for key holdings
    print("\n--- Technical Analysis (First 3 Holdings) ---\n")
    for symbol in portfolio[:3]:
        try:
            rsi = client.technical.get_rsi(symbol, period_length=14)
            if rsi:
                current_rsi = rsi[0].rsi
                signal = (
                    "Overbought"
                    if current_rsi > 70
                    else "Oversold" if current_rsi < 30 else "Neutral"
                )
                print(f"{symbol}: RSI = {current_rsi:.2f} ({signal})")
        except Exception as e:
            print(f"{symbol}: Technical data unavailable - {e}")


def main():
    # Example portfolio
    portfolio = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"]

    with FMPDataClient.from_env() as client:
        analyze_portfolio(client, portfolio)


if __name__ == "__main__":
    main()
