"""
Smoke tests for example files.
Ensures examples run without errors (imports, syntax, basic runtime).
"""

import importlib.util
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

import pytest

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


def create_mock_client():
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
            MagicMock(date=MagicMock(strftime=lambda x: "2024-01-01"), close=150.0),
            MagicMock(date=MagicMock(strftime=lambda x: "2024-01-02"), close=151.0),
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

    # Mock fundamental client
    mock_client.fundamental.get_income_statement.return_value = [
        MagicMock(
            fiscal_year="2024",
            revenue=400000000000,
            net_income=100000000000,
            eps=6.0,
        ),
    ]
    mock_client.fundamental.get_balance_sheet.return_value = [
        MagicMock(
            fiscal_year="2024",
            total_assets=500000000000,
            total_liabilities=300000000000,
            total_stockholders_equity=200000000000,
            cash_and_cash_equivalents=50000000000,
        ),
    ]
    mock_client.fundamental.get_cash_flow.return_value = [
        MagicMock(
            fiscal_year="2024",
            operating_cash_flow=120000000000,
            net_cash_used_for_investing_activities=-10000000000,
            net_cash_used_provided_by_financing_activities=-90000000000,
            free_cash_flow=110000000000,
        ),
    ]

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


def load_module_from_path(file_path: Path):
    """Load a Python module from file path."""
    spec = importlib.util.spec_from_file_location("test_module", file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["test_module"] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("example_file", EXAMPLE_FILES)
def test_example_runs_without_error(example_file, capsys):
    """Test that each example can be imported and runs without errors."""
    example_path = EXAMPLES_DIR / example_file

    # Ensure file exists
    assert example_path.exists(), f"Example file not found: {example_file}"

    # Create mock client
    mock_client = create_mock_client()

    # Mock FMPDataClient.from_env() to return our mock
    with patch("fmp_data.FMPDataClient.from_env") as mock_from_env:
        mock_from_env.return_value.__enter__.return_value = mock_client
        mock_from_env.return_value.__exit__.return_value = None

        # Load and run the example
        try:
            module = load_module_from_path(example_path)

            # Run main function if it exists
            if hasattr(module, "main"):
                module.main()

            # Capture output to ensure something was printed
            captured = capsys.readouterr()
            assert len(captured.out) > 0, f"Example {example_file} produced no output"

        except Exception as e:
            pytest.fail(f"Example {example_file} failed with error: {e}")


def test_all_examples_have_main_function():
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


def test_all_examples_use_context_manager():
    """Ensure all examples use context manager pattern."""
    for example_file in EXAMPLE_FILES:
        example_path = EXAMPLES_DIR / example_file

        # Read file content
        content = example_path.read_text()

        # Check for context manager usage
        assert (
            "with FMPDataClient" in content
        ), f"Example {example_file} not using context manager pattern"


def test_no_hardcoded_api_keys():
    """Ensure no examples have hardcoded API keys."""
    dangerous_patterns = [
        "api_key=",
        "FMP_API_KEY =",
    ]

    for example_file in EXAMPLE_FILES:
        example_path = EXAMPLES_DIR / example_file
        content = example_path.read_text()

        # Check for dangerous patterns (excluding placeholder)
        for pattern in dangerous_patterns:
            if pattern in content:
                # Allow placeholder strings
                if "your_api_key_here" in content or "your_test_api_key" in content:
                    continue
                pytest.fail(f"Example {example_file} may contain hardcoded API key")
