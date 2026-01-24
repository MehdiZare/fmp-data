"""
Smoke tests for example files.
Ensures examples run without errors (imports, syntax, basic runtime).
"""

import importlib.util
from pathlib import Path
import re
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest
from pytest import CaptureFixture

# Path to examples directory
EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"

# Example files to test (relative to examples/)
EXAMPLE_FILES = [
    "basic/company_info.py",
    "basic/historical_prices.py",
    "basic/market.py",
    "batch_operations/multi_symbol_quotes.py",
    "transcripts/earnings_calls.py",
    "sec_filings/filings_search.py",
    "index_tracking/index_constituents.py",
    "fundamental_analysis/financial_statements.py",
    "technical_analysis/indicators.py",
    "workflows/portfolio_analysis.py",
]


class ModuleLoadError(Exception):
    """Raised when a test module cannot be loaded from file path."""

    def __init__(self, file_path: Path) -> None:
        super().__init__(f"Could not load spec from {file_path}")
        self.file_path = file_path


def create_mock_client() -> MagicMock:
    """Create a mock FMPDataClient with all necessary methods."""
    mock_client = MagicMock()

    # Mock company client
    mock_client.company.get_profile.return_value = MagicMock(
        company_name="Apple Inc.",
        symbol="AAPL",
        industry="Technology",
        sector="Technology",
        ceo="Tim Cook",
        website="https://www.apple.com",
        description="Apple Inc. designs, manufactures, and markets smartphones...",
        mkt_cap=2500000000000.0,
    )
    mock_client.company.get_quote.return_value = MagicMock(
        price=150.0,
        changes_percentage=1.5,
        volume=50000000,
        year_low=120.0,
        year_high=180.0,
        price_avg_50=145.0,
        price_avg_200=140.0,
        change=2.25,
    )
    mock_client.company.get_historical_prices.return_value = MagicMock(
        historical=[
            MagicMock(date=MagicMock(strftime=lambda _: "2024-01-01"), close=150.0),
            MagicMock(date=MagicMock(strftime=lambda _: "2024-01-02"), close=151.0),
        ]
    )
    mock_client.company.get_executives.return_value = [
        MagicMock(title="CEO", name="Tim Cook"),
        MagicMock(title="CFO", name="Luca Maestri"),
    ]
    mock_client.company.get_company_peers.return_value = [
        MagicMock(symbol="MSFT"),
        MagicMock(symbol="GOOGL"),
    ]
    mock_client.company.get_employee_count.return_value = [
        MagicMock(period_of_report="2023-09-30", employee_count=164000),
        MagicMock(period_of_report="2022-09-30", employee_count=154000),
    ]

    # Mock market client
    mock_client.market.get_gainers.return_value = [
        MagicMock(symbol="XYZ", changes_percentage=5.0, price=100.0),
    ]
    mock_client.market.get_losers.return_value = [
        MagicMock(symbol="ABC", changes_percentage=-5.0, price=50.0),
    ]
    mock_client.market.get_most_active.return_value = [
        MagicMock(symbol="AAPL", volume=100000000, price=150.0),
    ]
    mock_client.market.get_sector_performance.return_value = [
        MagicMock(sector="Technology", change_percentage=2.5),
    ]
    mock_client.market.get_market_hours.return_value = MagicMock(
        is_market_open=True,
    )

    # Mock batch client
    mock_client.batch.get_quotes.return_value = [
        MagicMock(
            symbol="AAPL",
            price=150.0,
            changes_percentage=1.5,
            volume=50000000,
            market_cap=2500000000000,
        ),
        MagicMock(
            symbol="MSFT",
            price=380.0,
            changes_percentage=0.8,
            volume=30000000,
            market_cap=2800000000000,
        ),
        MagicMock(
            symbol="GOOGL",
            price=140.0,
            changes_percentage=-0.5,
            volume=25000000,
            market_cap=1800000000000,
        ),
    ]
    mock_client.batch.get_etf_quotes.return_value = [
        MagicMock(symbol="SPY", price=450.0, changes_percentage=0.5),
    ]
    mock_client.batch.get_market_caps.return_value = [
        MagicMock(symbol="AAPL", market_cap=2500000000000),
    ]

    # Mock transcripts client
    mock_client.transcripts.get_latest.return_value = [
        MagicMock(
            symbol="AAPL",
            quarter=4,
            year=2024,
            date="2024-10-31",
            content="Earnings call transcript...",
        ),
    ]
    mock_client.transcripts.get_transcript.return_value = [
        MagicMock(
            symbol="AAPL",
            quarter=4,
            year=2024,
            date="2024-10-31",
            content="Full earnings call transcript content here...",
        ),
    ]
    mock_client.transcripts.get_available_dates.return_value = [
        MagicMock(quarter=4, year=2024, date="2024-10-31"),
    ]

    # Mock SEC client
    mock_client.sec.get_latest_8k.return_value = [
        MagicMock(
            symbol="AAPL",
            form_type="8-K",
            filed_date="2024-01-15",
            final_link="https://sec.gov/...",
        ),
    ]
    mock_client.sec.search_by_symbol.return_value = [
        MagicMock(
            form_type="10-K",
            filed_date="2024-01-01",
            link="https://sec.gov/...",
        ),
    ]
    mock_client.sec.get_profile.return_value = MagicMock(
        cik="0000320193",
        company_name="Apple Inc.",
        sic_code="3571",
        sic_description="Electronic Computers",
    )
    mock_client.sec.get_sic_codes.return_value = [
        MagicMock(sic_code="3571", office="Electronic Computers"),
    ]

    # Mock index client
    mock_client.index.get_sp500_constituents.return_value = [
        MagicMock(symbol="AAPL", name="Apple Inc.", sector="Technology"),
    ]
    mock_client.index.get_nasdaq_constituents.return_value = [
        MagicMock(symbol="AAPL", name="Apple Inc."),
    ]
    mock_client.index.get_dowjones_constituents.return_value = [
        MagicMock(symbol="AAPL", name="Apple Inc.", sector="Technology"),
    ]
    mock_client.index.get_historical_sp500.return_value = [
        MagicMock(
            date="2024-01-01",
            added_security="NEW",
            removed_security="OLD",
        ),
    ]

    # Mock fundamental client with actual numeric values
    income_stmt = MagicMock()
    income_stmt.fiscal_year = "2024"
    income_stmt.revenue = 400000000000.0
    income_stmt.net_income = 100000000000.0
    income_stmt.eps = 6.0
    mock_client.fundamental.get_income_statement.return_value = [income_stmt]

    balance_sheet = MagicMock()
    balance_sheet.fiscal_year = "2024"
    balance_sheet.total_assets = 500000000000.0
    balance_sheet.total_liabilities = 300000000000.0
    balance_sheet.total_stockholders_equity = 200000000000.0
    balance_sheet.cash_and_short_term_investments = 50000000000.0
    mock_client.fundamental.get_balance_sheet.return_value = [balance_sheet]

    cash_flow = MagicMock()
    cash_flow.fiscal_year = "2024"
    cash_flow.operating_cash_flow = 120000000000.0
    cash_flow.net_cash_used_for_investing_activities = -10000000000.0
    cash_flow.net_cash_used_provided_by_financing_activities = -90000000000.0
    cash_flow.free_cash_flow = 110000000000.0
    mock_client.fundamental.get_cash_flow.return_value = [cash_flow]

    # Mock technical client
    mock_client.technical.get_rsi.return_value = [
        MagicMock(date="2024-01-01", rsi=65.0),
    ]
    mock_client.technical.get_sma.return_value = [
        MagicMock(date="2024-01-01", sma=150.0),
    ]
    mock_client.technical.get_ema.return_value = [
        MagicMock(date="2024-01-01", ema=151.0),
    ]

    # Mock intelligence client
    mock_client.intelligence.get_historical_earnings.return_value = [
        MagicMock(
            event_date="2024-01-31",
            eps=1.5,
            eps_estimated=1.4,
        ),
    ]

    return mock_client


def load_module_from_path(file_path: Path) -> ModuleType:
    """Load a Python module from file path."""
    # Use unique module name to avoid collisions
    module_name = f"test_example_{file_path.stem}_{id(file_path)}"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ModuleLoadError(file_path)

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("example_file", EXAMPLE_FILES)
def test_example_runs_without_error(
    example_file: str, capsys: CaptureFixture[str]
) -> None:
    """Test that each example can be imported and runs without errors."""
    example_path = EXAMPLES_DIR / example_file

    # Ensure file exists
    assert example_path.exists(), f"Example file not found: {example_file}"

    # Create mock client
    mock_client = create_mock_client()

    # Load the module first
    module = load_module_from_path(example_path)

    # Mock both FMPDataClient() and FMPDataClient.from_env() in the loaded module
    with (patch.object(module, "FMPDataClient") as mock_client_class,):
        # Mock the context manager
        mock_client_class.from_env.return_value.__enter__.return_value = mock_client
        mock_client_class.from_env.return_value.__exit__.return_value = None
        mock_client_class.return_value.__enter__.return_value = mock_client
        mock_client_class.return_value.__exit__.return_value = None

        # Run the example
        # Run main function if it exists
        main_func = getattr(module, "main", None)
        if main_func and callable(main_func):
            main_func()

        # Capture output to ensure something was printed
        captured = capsys.readouterr()
        assert captured.out, f"Example {example_file} produced no output"


def test_all_examples_have_main_function() -> None:
    """Ensure all example files have a main() function."""
    for example_file in EXAMPLE_FILES:
        example_path = EXAMPLES_DIR / example_file

        # Read file content
        content = example_path.read_text()

        # Check for main function
        assert "def main(" in content, f"Example {example_file} missing main() function"

        # Check for if __name__ == "__main__"
        assert (
            'if __name__ == "__main__"' in content
        ), f"Example {example_file} missing if __name__ == '__main__' guard"


def test_all_examples_use_context_manager() -> None:
    """Ensure all examples use context manager pattern."""
    for example_file in EXAMPLE_FILES:
        example_path = EXAMPLES_DIR / example_file

        # Read file content
        content = example_path.read_text()

        # Check for context manager usage
        assert (
            "with FMPDataClient" in content
        ), f"Example {example_file} not using context manager pattern"


def test_no_hardcoded_api_keys() -> None:
    """Ensure no examples have hardcoded API keys."""
    # Match api_key= or FMP_API_KEY= followed by a quoted string
    # that's not a placeholder
    key_patterns = [
        re.compile(
            r'api_key\s*=\s*["\'](?!your_api_key_here|your_test_api_key)[^"\']+["\']'
        ),
        re.compile(
            r'FMP_API_KEY\s*=\s*["\'](?!your_api_key_here|your_test_api_key)[^"\']+["\']'
        ),
    ]

    for example_file in EXAMPLE_FILES:
        example_path = EXAMPLES_DIR / example_file
        content = example_path.read_text()

        for pattern in key_patterns:
            if pattern.search(content):
                pytest.fail(f"Example {example_file} may contain hardcoded API key")
