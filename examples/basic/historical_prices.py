"""
Simple example demonstrating core functionality of the FMP Data library.
Shows how to fetch market data, company information, and financial metrics.
"""

from datetime import datetime, timedelta

from fmp_data import FMPDataClient


def main():
    # Initialize client from environment variable (FMP_API_KEY)
    with FMPDataClient.from_env() as client:
        # Example stock symbol
        symbol = "AAPL"

        try:
            # Get basic stock quote
            quote = client.company.get_quote(symbol)
            print("\nCurrent Stock Quote:")
            print(f"Price: ${quote.price:.2f}")
            print(f"Change: {quote.change_percentage:.2f}%")
            print(f"Volume: {quote.volume:,}")

            # Get company profile
            profile = client.company.get_profile(symbol)
            print("\nCompany Profile:")
            print(f"Name: {profile.company_name}")
            print(f"Industry: {profile.industry}")
            print(f"Market Cap: ${profile.mkt_cap:,.2f}")

            # Get historical prices for the last 30 days
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)

            historical = client.company.get_historical_prices(
                symbol=symbol,
                from_date=start_date.strftime("%Y-%m-%d"),
                to_date=end_date.strftime("%Y-%m-%d"),
            )

            print("\nHistorical Prices (Last 30 Days):")
            for price in historical.historical[:5]:  # Show first 5 days
                date_str = price.date.strftime("%Y-%m-%d")
                print(f"Date: {date_str}, Close: ${price.close:.2f}")

            # Get latest earnings
            earnings = client.intelligence.get_historical_earnings(symbol)
            if earnings:
                print("\nLatest Earnings:")
                latest = earnings[-1]
                print(f"Date: {latest.event_date}")
                print(f"EPS: ${latest.eps if latest.eps else 'N/A'}")
                print(
                    f"Estimated EPS: "
                    f"${latest.eps_estimated if latest.eps_estimated else 'N/A'}"
                )

            # Get technical indicators
            rsi = client.technical.get_rsi(symbol, period_length=14)
            if rsi:
                print("\nTechnical Indicators:")
                print(f"Current RSI (14): {rsi[0].rsi:.2f}")

        except Exception as e:
            print(f"Error: {e!s}")

    # Client automatically closed after with block


if __name__ == "__main__":
    main()
