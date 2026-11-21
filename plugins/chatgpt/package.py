"""Build the OpenAI Agent Plugins ZIP for a deployed FMP Data server."""

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import ZIP_DEFLATED, ZipFile


def public_url(value: str) -> str:
    url = urlsplit(value)
    if (
        url.scheme != "https"
        or not url.hostname
        or url.username is not None
        or url.password is not None
        or url.query
        or url.fragment
    ):
        raise argparse.ArgumentTypeError("Supply a credential-free HTTPS URL.")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", type=public_url, required=True)
    parser.add_argument("--publisher", required=True)
    for field in ("website", "support", "privacy", "terms"):
        parser.add_argument(f"--{field}", type=public_url, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    schema = "https://agent-plugins.org/schemas/1.0.0"
    manifest = {
        "$schema": f"{schema}/plugin.schema.json",
        "name": "fmp-data",
        "version": "0.1.0",
        "description": "Find company tickers, quotes, and profiles with fmp-data.",
        "author": {"name": args.publisher},
        "repository": "https://github.com/MehdiZare/fmp-data",
        "license": "MIT",
        "extensions": {
            "com.openai": {
                "interface": {
                    "displayName": "FMP Data",
                    "shortDescription": "Look up company tickers, profiles, and quotes",
                    "developerName": args.publisher,
                    "websiteURL": args.website,
                    "supportURL": args.support,
                    "privacyPolicyURL": args.privacy,
                    "termsOfServiceURL": args.terms,
                    "defaultPrompt": ["Find Microsoft's ticker and latest quote."],
                },
            },
        },
    }
    mcp = {
        "$schema": f"{schema}/mcp.schema.json",
        "mcpServers": {"fmp-data": {"type": "streamable-http", "url": args.endpoint}},
    }
    with ZipFile(args.output, "x", compression=ZIP_DEFLATED) as archive:
        for name, obj in (("plugin.json", manifest), ("mcp.json", mcp)):
            archive.writestr(name, json.dumps(obj, indent=2) + "\n")


if __name__ == "__main__":
    main()
