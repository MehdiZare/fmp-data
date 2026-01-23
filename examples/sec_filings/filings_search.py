"""
Example demonstrating SEC filings search and retrieval.
Shows how to search and analyze SEC filings (8-K, 10-K, 10-Q).
"""

from fmp_data import FMPDataClient


def main():
    with FMPDataClient.from_env() as client:
        # Get latest 8-K filings (material events)
        print("\n=== Latest 8-K Filings ===\n")
        filings_8k = client.sec.get_latest_8k(limit=5)
        for filing in filings_8k:
            print(f"{filing.symbol} - {filing.form_type}")
            print(f"Date: {filing.filed_date}")
            print(f"URL: {filing.final_link}")
            print()

        # Get SEC filings for specific company
        print("\n=== Apple SEC Filings ===\n")
        filings = client.sec.search_by_symbol("AAPL", limit=10)
        for filing in filings[:5]:  # Show first 5
            print(f"{filing.form_type} - {filing.filed_date}")
            print(f"Link: {filing.link}")
            print()

        # Get SEC company profile
        print("\n=== Apple SEC Profile ===\n")
        profile = client.sec.get_profile("AAPL")
        if profile:
            print(f"CIK: {profile.cik}")
            print(f"Company: {profile.company_name}")
            print(f"SIC Code: {profile.sic_code}")
            print(f"SIC Description: {profile.sic_description}")

        # Get SIC codes list
        print("\n=== Sample SIC Codes ===\n")
        sic_codes = client.sec.get_sic_codes()
        for sic in sic_codes[:5]:  # Show first 5
            print(f"{sic.sic_code} - {sic.office}")


if __name__ == "__main__":
    main()
