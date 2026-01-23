"""
Example demonstrating market index constituent tracking.
Shows how to track S&P 500, NASDAQ, and Dow Jones constituents.
"""

from fmp_data import FMPDataClient


def main():
    with FMPDataClient.from_env() as client:
        # Get S&P 500 constituents
        print("\n=== S&P 500 Constituents (Sample) ===\n")
        sp500 = client.index.get_sp500_constituents()
        print(f"Total S&P 500 constituents: {len(sp500)}")
        for company in sp500[:10]:  # Show first 10
            print(f"{company.symbol:6} - {company.name} ({company.sector})")

        # Get NASDAQ constituents
        print("\n\n=== NASDAQ Constituents (Sample) ===\n")
        nasdaq = client.index.get_nasdaq_constituents()
        print(f"Total NASDAQ constituents: {len(nasdaq)}")
        for company in nasdaq[:10]:  # Show first 10
            print(f"{company.symbol:6} - {company.name}")

        # Get Dow Jones constituents
        print("\n\n=== Dow Jones Industrial Average (All 30) ===\n")
        dowjones = client.index.get_dowjones_constituents()
        print(f"Total Dow Jones constituents: {len(dowjones)}")
        for company in dowjones:
            print(f"{company.symbol:6} - {company.name} ({company.sector})")

        # Get historical S&P 500 changes
        print("\n\n=== Recent S&P 500 Changes ===\n")
        changes = client.index.get_historical_sp500()
        for change in changes[:5]:  # Show first 5 recent changes
            print(
                f"{change.date}: {change.added_security} added, "
                f"{change.removed_security} removed"
            )


if __name__ == "__main__":
    main()
