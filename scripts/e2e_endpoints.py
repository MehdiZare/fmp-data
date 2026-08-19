#!/usr/bin/env python3
"""Record or replay a full client-method sweep against the FMP API.

This is a maintainer tool. It spends quota in ``record`` mode. Replay uses
VCR cassettes under ``tests/e2e/vcr_cassettes/`` and never hits the network.

Examples::

    uv run python scripts/e2e_endpoints.py list
    uv run python scripts/e2e_endpoints.py record --group company
    uv run python scripts/e2e_endpoints.py record --method get_profile --refresh
    uv run python scripts/e2e_endpoints.py replay
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

from fmp_data import ClientConfig, FMPDataClient  # noqa: E402
from fmp_data.config import (  # noqa: E402
    LoggingConfig,
    LogHandlerConfig,
    RateLimitConfig,
)
from tests.e2e.harness import (  # noqa: E402
    CLIENT_GROUPS,
    REPORT_PATH,
    discover_cases,
    format_report,
    run_cases,
    select_cases,
    write_report,
)


def _load_env() -> None:
    env_path = ROOT / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)
    if not os.getenv("FMP_TEST_API_KEY") and os.getenv("FMP_API_KEY"):
        os.environ["FMP_TEST_API_KEY"] = os.environ["FMP_API_KEY"]
    if not os.getenv("FMP_API_KEY") and os.getenv("FMP_TEST_API_KEY"):
        os.environ["FMP_API_KEY"] = os.environ["FMP_TEST_API_KEY"]


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sweep every public sync FMPDataClient method under VCR."
    )
    parser.add_argument(
        "command",
        choices=("list", "record", "replay"),
        help="list cases, record live traffic, or replay cassettes",
    )
    parser.add_argument(
        "--group",
        choices=CLIENT_GROUPS,
        help="restrict to one client group",
    )
    parser.add_argument(
        "--method",
        help="restrict to one method name (can combine with --group)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="with record: overwrite existing cassettes (VCR mode 'all')",
    )
    parser.add_argument(
        "--skip-bulk",
        action="store_true",
        help="skip batch *_bulk CSV downloads",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="set validation_mode=strict so extra/missing fields fail",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPORT_PATH,
        help=f"JSON report path (default: {REPORT_PATH})",
    )
    parser.add_argument(
        "--throttle",
        type=float,
        default=0.2,
        help="seconds to wait between live calls (record only)",
    )
    return parser.parse_args(argv)


def _make_client(*, strict: bool, replay: bool) -> FMPDataClient:
    api_key = os.getenv("FMP_TEST_API_KEY") or os.getenv("FMP_API_KEY")
    if not api_key:
        if replay:
            api_key = "DUMMY_API_KEY"  # pragma: allowlist secret
        else:
            raise SystemExit("FMP_TEST_API_KEY (or FMP_API_KEY) is required to record.")
    if not replay and len(api_key.strip()) < 10:
        raise SystemExit("FMP_TEST_API_KEY appears to be invalid.")

    config = ClientConfig(
        api_key=api_key,
        base_url=os.getenv("FMP_TEST_BASE_URL", "https://financialmodelingprep.com"),
        timeout=int(float(os.getenv("FMP_TEST_TIMEOUT", "30"))),
        max_retries=2,
        validation_mode="strict" if strict else "warn",
        logging=LoggingConfig(
            level="ERROR",
            handlers={
                "console": LogHandlerConfig(
                    class_name="StreamHandler",
                    level="ERROR",
                    format="%(levelname)s %(name)s: %(message)s",
                )
            },
        ),
        rate_limit=RateLimitConfig(
            daily_limit=5000, requests_per_second=5, requests_per_minute=250
        ),
    )
    return FMPDataClient(config=config)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    _load_env()
    cases = select_cases(
        discover_cases(),
        group=args.group,
        method=args.method,
        skip_bulk=args.skip_bulk,
    )
    if not cases:
        print("No cases matched.", file=sys.stderr)
        return 2

    if args.command == "list":
        for case in cases:
            flags = []
            if case.deprecated:
                flags.append("deprecated")
            if case.bulk:
                flags.append("bulk")
            suffix = f"  [{', '.join(flags)}]" if flags else ""
            path = f"  {case.endpoint_path}" if case.endpoint_path else ""
            print(f"{case.group}.{case.method}{path}{suffix}")
        print(f"\n{len(cases)} case(s)", file=sys.stderr)
        return 0

    if args.command == "record":
        record_mode = "all" if args.refresh else "new_episodes"
        os.environ["FMP_VCR_RECORD"] = record_mode
    else:
        record_mode = "none"
        os.environ["FMP_VCR_RECORD"] = "none"

    client = _make_client(strict=args.strict, replay=args.command == "replay")
    try:
        rows = run_cases(
            cases,
            client=client,
            record_mode=record_mode,
            throttle=args.throttle,
        )
    finally:
        client.close()

    payload = [row.as_dict() for row in rows]
    write_report(args.report, payload)
    print(format_report(payload))
    print(f"\nreport: {args.report}", file=sys.stderr)

    failed = any(row.status in {"error", "empty"} for row in rows)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
