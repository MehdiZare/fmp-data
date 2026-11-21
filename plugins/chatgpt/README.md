# FMP Data for ChatGPT

The plugin exposes three read-only tools through the Python client. Search by
company name to identify the ticker and exchange, then retrieve a quote or
company profile. Quote availability and delay depend on the FMP subscription.
Use the timestamp returned with the price.

## Connect your account

Choose **Connect** in ChatGPT. On the plugin's connection page, enter the API
key from your [FMP dashboard](https://site.financialmodelingprep.com/developer/docs/quickstart).
The plugin verifies quote access with one AAPL lookup. ChatGPT receives a scoped
OAuth token. Every subsequent lookup uses the FMP key linked to that connection
and consumes that account's quota. If FMP rejects a rotated key, reconnect with
the replacement on the connection page.

## Run the server

The server uses the MCP SDK's OAuth authorization-code flow with S256 PKCE.
Register the HTTPS callback shown by ChatGPT and configure these environment
variables in your service's secret or deployment settings.

| Variable | Value |
| --- | --- |
| `FMP_PLUGIN_ORIGIN` | External HTTPS origin. Local development also supports `http://127.0.0.1:8000`. |
| `FMP_PLUGIN_REDIRECT_URI` | The exact registered ChatGPT HTTPS callback URL. |
| `FMP_PLUGIN_CLIENT_SECRET` | A random secret of at least 32 characters for the provided OAuth client. Enter the same value in OpenAI's connection setup. |
| `FMP_PLUGIN_ENCRYPTION_KEY` | A Fernet key. Generate it once with `uv run --extra chatgpt python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'` and store it in your secret manager. |
| `FMP_PLUGIN_DATABASE` | Absolute SQLite file path in a private, persistent directory accessible to the server. |

From the repository root:

```sh
uv run --extra chatgpt uvicorn plugins.chatgpt.server:create_app --factory --host 127.0.0.1 --port 8000
```

Route the entire origin to the service so ChatGPT and the user's browser can
reach discovery, authorization, account linking, token exchange, revocation,
and `/mcp`. Deploy on a persistent host whose workers share a local SQLite
volume. Keep the database and encryption key across restarts. Replacing the
encryption key requires reconnecting users. Keep request bodies and OAuth
credentials out of proxy and tracing logs.

Each connection stores an encrypted FMP key. Codes and tokens are stored as
hashes. Access tokens last an hour. Refresh rotates both tokens and extends
the connection by 30 days. Revoking either current token deletes the grant
and encrypted key. An idle connection expires after 30 days and expired rows
are purged when a new connection is linked.

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
the listing artwork, verified domain challenge, reviewer material, and the
registered client secret in the developer dashboard. The package declares
the provided OAuth client `fmp-data-chatgpt` and scope `market:read`.
The builder follows OpenAI's per-server `extensions["com.openai"].auth`
format. The generic Agent Plugins 1.0.0 MCP schema currently rejects this
extension. Verify the saved OAuth settings in the OpenAI portal during submission.
See [OpenAI's registered-client manifest example](https://developers.openai.com/plugins/build/plugins#use-a-registered-oauth-client). FMP describes public display rights
in its [licensing information](https://site.financialmodelingprep.com/pricing-plans).

```sh
python plugins/chatgpt/package.py --endpoint "$MCP_ENDPOINT" --publisher "$PUBLISHER" \
  --website "$WEBSITE_URL" --support "$SUPPORT_URL" --privacy "$PRIVACY_URL" \
  --terms "$TERMS_URL" --output fmp-data-plugin.zip
```
