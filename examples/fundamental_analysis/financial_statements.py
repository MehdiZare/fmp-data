"""
Example demonstrating financial statement analysis.
Shows how to fetch and analyze income statements, balance sheets, and cash flow.
"""

from fmp_data import FMPDataClient


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
            print(f"Revenue: ${stmt.revenue:,.0f}")
            print(f"Net Income: ${stmt.net_income:,.0f}")
            print(f"EPS: ${stmt.eps:.2f}")
            print()

        # Get balance sheets
        print(f"\n=== {symbol} Balance Sheet (Latest) ===\n")
        balance = client.fundamental.get_balance_sheet(symbol, period="annual", limit=1)
        if balance:
            stmt = balance[0]
            print(f"Year: {stmt.fiscal_year}")
            print(f"Total Assets: ${stmt.total_assets:,.0f}")
            print(f"Total Liabilities: ${stmt.total_liabilities:,.0f}")
            print(f"Total Equity: ${stmt.total_stockholders_equity:,.0f}")
            print(
                f"Cash & ST Investments: ${stmt.cash_and_short_term_investments:,.0f}"
            )

        # Get cash flow statements
        print(f"\n\n=== {symbol} Cash Flow (Latest) ===\n")
        cash_flow = client.fundamental.get_cash_flow(symbol, period="annual", limit=1)
        if cash_flow:
            stmt = cash_flow[0]
            print(f"Year: {stmt.fiscal_year}")
            op_cf = stmt.operating_cash_flow
            inv_cf = stmt.net_cash_used_for_investing_activities
            fin_cf = stmt.net_cash_used_provided_by_financing_activities
            print(f"Operating Cash Flow: ${op_cf:,.0f}")
            print(f"Investing Cash Flow: ${inv_cf:,.0f}")
            print(f"Financing Cash Flow: ${fin_cf:,.0f}")
            print(f"Free Cash Flow: ${stmt.free_cash_flow:,.0f}")


if __name__ == "__main__":
    main()
