"""
Example demonstrating technical analysis indicators.
Shows how to calculate and use RSI, MACD, SMA, and EMA indicators.
"""

from fmp_data import FMPDataClient


def main():
    with FMPDataClient.from_env() as client:
        symbol = "AAPL"

        # Get RSI (Relative Strength Index)
        print(f"\n=== {symbol} RSI (14-period) ===\n")
        rsi = client.technical.get_rsi(symbol, period_length=14, timeframe="1day")
        if rsi:
            for indicator in rsi[:5]:  # Show first 5
                print(f"Date: {indicator.date} | RSI: {indicator.rsi:.2f}")

        # Get MACD (Moving Average Convergence Divergence)
        print(f"\n\n=== {symbol} MACD ===\n")
        macd = client.technical.get_macd(
            symbol, fast_period=12, slow_period=26, signal_period=9
        )
        if macd:
            for indicator in macd[:5]:  # Show first 5
                print(f"Date: {indicator.date}")
                print(f"  MACD: {indicator.macd:.4f}")
                print(f"  Signal: {indicator.signal:.4f}")
                print(f"  Histogram: {indicator.histogram:.4f}")

        # Get SMA (Simple Moving Average)
        print(f"\n\n=== {symbol} SMA (50-day) ===\n")
        sma = client.technical.get_sma(symbol, period_length=50, timeframe="1day")
        if sma:
            for indicator in sma[:5]:  # Show first 5
                print(f"Date: {indicator.date} | SMA: ${indicator.sma:.2f}")

        # Get EMA (Exponential Moving Average)
        print(f"\n\n=== {symbol} EMA (20-day) ===\n")
        ema = client.technical.get_ema(symbol, period_length=20, timeframe="1day")
        if ema:
            for indicator in ema[:5]:  # Show first 5
                print(f"Date: {indicator.date} | EMA: ${indicator.ema:.2f}")


if __name__ == "__main__":
    main()
