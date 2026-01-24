"""
Example demonstrating earnings call transcript access.
Shows how to fetch and analyze earnings call transcripts.
"""

from fmp_data import FMPDataClient
from fmp_data.exceptions import FMPError


def main() -> None:
    with FMPDataClient.from_env() as client:
        # Get latest earnings call transcripts
        print("\n=== Latest Earnings Call Transcripts ===\n")
        latest = client.transcripts.get_latest(limit=5)
        for transcript in latest:
            print(f"{transcript.symbol} - Q{transcript.quarter} {transcript.year}")
            print(f"Date: {transcript.date}")
            if transcript.content:
                print(f"Content: {transcript.content[:200]}...")
            else:
                print("Content: [Not available]")
            print()

        # Get transcript for specific company and quarter
        print("\n=== Apple Q4 2024 Transcript ===\n")
        try:
            transcripts = client.transcripts.get_transcript(
                "AAPL", year=2024, quarter=4
            )
            if transcripts:
                transcript = transcripts[0]  # Get first result
                print(f"Symbol: {transcript.symbol}")
                print(f"Quarter: Q{transcript.quarter} {transcript.year}")
                print(f"Date: {transcript.date}")
                if transcript.content:
                    print(f"Content length: {len(transcript.content)} characters")
                    print(f"Preview: {transcript.content[:300]}...")
                else:
                    print("Content: [Not available]")
        except FMPError as e:
            print(f"Transcript not available: {e}")

        # Get available transcript dates for a company
        print("\n=== Available Transcript Dates for AAPL ===\n")
        dates = client.transcripts.get_available_dates("AAPL")
        for date_info in dates[:5]:  # Show first 5
            print(f"Q{date_info.quarter} {date_info.year} - {date_info.date}")


if __name__ == "__main__":
    main()
