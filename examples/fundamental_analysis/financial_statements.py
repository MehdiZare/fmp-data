"""
Example demonstrating financial statement analysis.
Shows how to fetch and analyze income statements, balance sheets, and cash flow.
"""

from fmp_data import FMPDataClient


def format_amount(value: float | None) -> str:
    """Format financial amount, returning 'N/A' for None values."""
    if value is None:
        return "N/A"
    return f"${value:,.0f}"


def main() -> None:
    with FMPDataClient.from_env() as client:
        symbol = "AAPL"

        # Get income statements
        print(f"\n=== {symbol} Income Statement (Annual) ===\n")
        income = client.fundamental.get_income_statement(
            symbol, period="annual", limit=3
        )
        for stmt in income:
            print(f"Year: {stmt.fiscal_year}")
            print(f"Revenue: {format_amount(stmt.revenue)}")
            print(f"Net Income: {format_amount(stmt.net_income)}")
            eps = f"${stmt.eps:.2f}" if stmt.eps is not None else "N/A"
            print(f"EPS: {eps}")
            print()

        # Get balance sheets
        print(f"\n=== {symbol} Balance Sheet (Latest) ===\n")
        balance = client.fundamental.get_balance_sheet(symbol, period="annual", limit=1)
        if balance:
            stmt = balance[0]
            print(f"Year: {stmt.fiscal_year}")
            print(f"Total Assets: {format_amount(stmt.total_assets)}")
            print(f"Total Liabilities: {format_amount(stmt.total_liabilities)}")
            print(f"Total Equity: {format_amount(stmt.total_stockholders_equity)}")
            cash_investments = format_amount(stmt.cash_and_short_term_investments)
            print(f"Cash & ST Investments: {cash_investments}")

        # Get cash flow statements
        print(f"\n\n=== {symbol} Cash Flow (Latest) ===\n")
        cash_flow = client.fundamental.get_cash_flow(symbol, period="annual", limit=1)
        if cash_flow:
            stmt = cash_flow[0]
            print(f"Year: {stmt.fiscal_year}")
            print(f"Operating Cash Flow: {format_amount(stmt.operating_cash_flow)}")
            investing_cf = format_amount(stmt.net_cash_used_for_investing_activities)
            print(f"Investing Cash Flow: {investing_cf}")
            financing_cf = format_amount(
                stmt.net_cash_used_provided_by_financing_activities
            )
            print(f"Financing Cash Flow: {financing_cf}")
            print(f"Free Cash Flow: {format_amount(stmt.free_cash_flow)}")


if __name__ == "__main__":
    main()
