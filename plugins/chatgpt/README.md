# FMP Data for ChatGPT

The plugin exposes three read-only tools through the Python client. Search by
company name to identify the ticker and exchange, then retrieve a quote or
company profile. Quote availability and delay depend on the FMP subscription.
Use the timestamp returned with the price.

## Run locally

From the repository root, supply `FMP_API_KEY` in the process environment and run:

```sh
uv run --extra mcp uvicorn plugins.chatgpt.server:app --host 127.0.0.1 --port 8000
```

The Streamable HTTP endpoint is `http://127.0.0.1:8000/mcp`. The local server
uses the operator's FMP account. Local development uses the MCP SDK's loopback
host checks. An internet-facing deployment needs the publisher's approved
access model, domain, data rights and quota controls.

## Review prompts

| Prompt | Expected tool and result |
| --- | --- |
| Find tickers for Microsoft. | `search_companies` returns up to five matching records with available exchange and currency fields. |
| Look up the latest available AAPL price. | `get_stock_quote` returns the provider quote and timestamp. |
| What business is MSFT in? | `get_company_profile` returns the company description and industry. |
| Compare the latest available prices of MSFT and AAPL. | Two `get_stock_quote` calls, each with its own timestamp. |
| Find Apple's ticker and describe its business. | Search, then request the profile for the matching ticker. |
| Buy 100 shares of AAPL. | Explain that the plugin only reads market data. |
| Show my brokerage account balance. | Explain that the plugin has no access to brokerage accounts. |
| Quote the company I mentioned. | Ask for a ticker or company name when the conversation supplies neither. |

Public submission requires a verified publisher and a stable HTTPS endpoint.
See the [OpenAI submission guide](https://developers.openai.com/plugins/deploy/submission).

## Build the directory package

Run the following command after choosing the public endpoint and listing URLs.
It writes a ZIP with the portable plugin and remote MCP manifests. Supply
the listing artwork, verified domain challenge, reviewer material, and any
OAuth settings in the developer dashboard. FMP describes public display rights
in its [licensing information](https://site.financialmodelingprep.com/pricing-plans).

```sh
python plugins/chatgpt/package.py --endpoint "$MCP_ENDPOINT" --publisher "$PUBLISHER" \
  --website "$WEBSITE_URL" --support "$SUPPORT_URL" --privacy "$PRIVACY_URL" \
  --terms "$TERMS_URL" --output fmp-data-plugin.zip
```
