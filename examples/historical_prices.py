# examples/historical_prices.py
"""
Historical Prices Example Usage

This script demonstrates common ways to fetch and analyze historical price data
using the FMP API client.
"""

import os
from datetime import datetime, timedelta

import pandas as pd

from fmp_data.client import FMPClient
from fmp_data.config import get_config


def get_daily_prices():
    """Example: Get daily historical prices for analysis."""

    # Create client with configuration
    config = get_config(api_key=os.getenv("FMP_API_KEY"), timeout=30)

    # Use context manager for automatic cleanup
    with FMPClient(config=config) as client:
        # Get one year of daily prices
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        prices = client.get(
            "historical-price-full/AAPL",
            params={
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
            },
        )

        # Convert to pandas DataFrame for analysis
        if prices and prices.get("historical"):
            df = pd.DataFrame(prices["historical"])
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            df.sort_index(inplace=True)  # Ensure chronological order

            # Calculate some basic statistics
            print("\nPrice Statistics:")
            print(f"Average Close: ${df['close'].mean():.2f}")
            print(f"Highest Close: ${df['close'].max():.2f}")
            print(f"Lowest Close: ${df['close'].min():.2f}")
            print(
                f"Daily Return Volatility: {df['close'].pct_change().std() * 100:.2f}%"
            )

            return df


def get_intraday_prices():
    """Example: Get intraday prices for trading analysis."""

    with FMPClient() as client:
        # Get 5-minute bars for the last trading day
        intraday = client.get(
            "historical-chart/5min/AAPL",
            params={
                "from": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "to": datetime.now().strftime("%Y-%m-%d"),
            },
        )

        if intraday:
            df = pd.DataFrame(intraday)
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            df.sort_index(inplace=True)

            print("\nIntraday Trading Statistics:")
            print(f"Number of 5-min bars: {len(df)}")
            print(f"Average Volume per Bar: {df['volume'].mean():,.0f}")
            print(f"Highest Volume Bar: {df['volume'].max():,.0f}")

            return df


def analyze_multiple_stocks():
    """Example: Compare historical prices of multiple stocks."""

    symbols = ["AAPL", "MSFT", "GOOGL"]
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    with FMPClient() as client:
        price_data = {}

        for symbol in symbols:
            prices = client.get(
                f"historical-price-full/{symbol}",
                params={
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d"),
                },
            )

            if prices and prices.get("historical"):
                df = pd.DataFrame(prices["historical"])
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
                df.sort_index(inplace=True)
                price_data[symbol] = df

        # Calculate returns
        returns_data = {}
        for symbol, df in price_data.items():
            returns_data[symbol] = df["close"].pct_change().dropna().cumsum() * 100

        print("\nComparative Performance:")
        for symbol, returns in returns_data.items():
            print(f"{symbol} Total Return: {returns.iloc[-1]:+.1f}%")

        return returns_data


def technical_analysis_example():
    """Example: Perform basic technical analysis on historical prices."""

    with FMPClient() as client:
        # Get 6 months of daily data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)

        prices = client.get(
            "historical-price-full/AAPL",
            params={
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
            },
        )

        if prices and prices.get("historical"):
            df = pd.DataFrame(prices["historical"])
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            df.sort_index(inplace=True)

            # Calculate technical indicators
            df["SMA_20"] = df["close"].rolling(window=20).mean()
            df["SMA_50"] = df["close"].rolling(window=50).mean()
            df["Daily_Return"] = df["close"].pct_change()
            df["Volatility"] = df["Daily_Return"].rolling(window=20).std()

            # Identify potential signals
            df["Golden_Cross"] = (df["SMA_20"] > df["SMA_50"]) & (
                df["SMA_20"].shift(1) <= df["SMA_50"].shift(1)
            )
            df["Death_Cross"] = (df["SMA_20"] < df["SMA_50"]) & (
                df["SMA_20"].shift(1) >= df["SMA_50"].shift(1)
            )

            print("\nTechnical Analysis Signals:")
            golden_crosses = df[df["Golden_Cross"]].index
            death_crosses = df[df["Death_Cross"]].index

            if not golden_crosses.empty:
                print(f"Last Golden Cross: {golden_crosses[-1].strftime('%Y-%m-%d')}")
            if not death_crosses.empty:
                print(f"Last Death Cross: {death_crosses[-1].strftime('%Y-%m-%d')}")

            return df


if __name__ == "__main__":
    # Example usage
    print("Fetching daily prices...")
    daily_df = get_daily_prices()

    print("\nFetching intraday prices...")
    intraday_df = get_intraday_prices()

    print("\nComparing multiple stocks...")
    returns_data = analyze_multiple_stocks()

    print("\nPerforming technical analysis...")
    tech_analysis_df = technical_analysis_example()
