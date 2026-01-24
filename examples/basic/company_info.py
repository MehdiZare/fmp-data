"""
Basic example demonstrating how to fetch company information.
Shows company profile, executives, peers, and key metrics.
"""

from fmp_data import FMPDataClient


def main() -> None:
    with FMPDataClient.from_env() as client:
        symbol = "AAPL"

        # Get company profile
        print(f"\n=== {symbol} Company Profile ===\n")
        profile = client.company.get_profile(symbol)
        print(f"Company: {profile.company_name}")
        print(f"Symbol: {profile.symbol}")
        print(f"Industry: {profile.industry}")
        print(f"Sector: {profile.sector}")
        print(f"CEO: {profile.ceo}")
        print(f"Website: {profile.website}")
        description = profile.description or ""
        print(
            f"Description: {description[:200]}{'...' if len(description) > 200 else ''}"
        )

        # Get company executives
        print(f"\n\n=== {symbol} Executive Team ===\n")
        executives = client.company.get_executives(symbol)
        for exec in executives[:5]:  # Show first 5
            print(f"{exec.title}: {exec.name}")

        # Get company peers
        print(f"\n\n=== {symbol} Company Peers ===\n")
        peers = client.company.get_company_peers(symbol)
        if peers:
            peer_symbols = [peer.symbol for peer in peers[:10]]
            print(f"Peers: {', '.join(peer_symbols)}")

        # Get employee count history
        print(f"\n\n=== {symbol} Employee Count History ===\n")
        employees = client.company.get_employee_count(symbol)
        for record in employees[:5]:  # Show first 5 records
            print(f"{record.period_of_report}: {record.employee_count:,} employees")


if __name__ == "__main__":
    main()
