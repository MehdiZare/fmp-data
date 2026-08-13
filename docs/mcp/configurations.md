# MCP Configuration Examples

Example MCP (Model Context Protocol) manifests live in `examples/mcp/configurations/`.
Use them to scope which tools are exposed to Claude or other MCP clients. If you
installed from PyPI, copy the manifests from the repo or create your own.

## Quick Setup

For guided setup, run:
```bash
pip install "fmp-data[mcp]"
fmp-mcp setup
```

See [Claude Desktop Setup](claude_desktop.md) for full setup instructions.

## Available Configurations

### Default (no manifest)
Uses the full tool set. Do not set `FMP_MCP_MANIFEST`.

### `minimal_manifest.py`
The smallest useful configuration with just essential tools:
- Company profiles and quotes
- Basic market data
- Cryptocurrency support

**Use case:** Testing, development, or lightweight deployments

### `trading_manifest.py`
Optimized for active trading and technical analysis:
- Real-time quotes and market movers
- Technical indicators (SMA, RSI, MACD, etc.)
- Pre-/post-market data
- Price targets and news

**Use case:** Day trading, swing trading, technical analysis

### `research_manifest.py`
Comprehensive tools for fundamental analysis:
- Complete financial statements
- Key metrics and ratios
- Analyst recommendations
- Institutional holdings
- Economic indicators

**Use case:** Investment research, due diligence, long-term investing

### `crypto_manifest.py`
Specialized for cryptocurrency markets:
- Crypto quotes and historical data
- Intraday crypto prices
- Crypto news
- Technical indicators for crypto

**Use case:** Cryptocurrency trading and analysis

## Usage

### Quick Setup with CLI (Recommended)
```bash
# Setup wizard for Claude Desktop
fmp-mcp setup

# Check server status
fmp-mcp status

# Test server connection
fmp-mcp test

# List available tools
fmp-mcp list

# List tools for specific client
fmp-mcp list --client market
```

### Manual Configuration

#### Using with Python module execution
```bash
export FMP_API_KEY=your_api_key_here  # pragma: allowlist secret
export FMP_MCP_MANIFEST=examples/mcp/configurations/trading_manifest.py
python -m fmp_data.mcp
```

#### Using with MCP CLI
```bash
FMP_API_KEY=your_api_key mcp dev python -c "
from fmp_data.mcp.server import create_app
app = create_app("examples/mcp/configurations/research_manifest.py")
app.run()
"
```

#### Using in your own code
```python
from fmp_data.mcp.server import create_app

# Load a specific configuration
app = create_app(tools="examples/mcp/configurations/minimal_manifest.py")
app.run()
```

## Creating Custom Configurations

Manifests are **data**. `fmp-mcp validate` and the server parse them; they
never import or execute the file. A Python file that is not exactly a
docstring plus `TOOLS = ["..."]` is rejected.

Preferred new format:

```json
{
  "tools": ["company.profile", "company.quote"]
}
```

YAML (`tools: [company.profile]`) and TOML (`tools = ["company.profile"]`)
are accepted the same way. TOML has no top-level array form; use a
`tools` table. On Python 3.10 the `mcp` extra pulls in `tomli` for that
parse; 3.11+ uses stdlib `tomllib`.

You can still create a legacy Python manifest by:

1. **Manual creation** - Copy one of these examples and modify:
```python
# my_custom_manifest.py
TOOLS = [
    "company.profile",
    "company.quote",
    # Add your desired tools here
]
```

2. **Using the CLI tool** - Generate a manifest with specific tools.
   The suffix chooses the format (``.json`` preferred; ``.yaml`` / ``.toml``
   / legacy ``.py`` still work):
```bash
# Generate a JSON manifest (preferred)
fmp-mcp generate my_manifest.json --tools company.profile company.quote

# Generate without default tools
fmp-mcp generate my_manifest.json --no-defaults --tools company.quote market.gainers

# Whole catalog
fmp-mcp generate everything.json

# Bare keys work too, and are written out in their fully qualified form
fmp-mcp generate my_manifest.json --no-defaults --tools profile quote gainers

# Legacy Python (still parsed as data, never executed)
fmp-mcp generate my_manifest.py --tools company.profile company.quote
```

`--tools` accepts the same two entry forms a manifest does — a bare key
(`profile`) or a fully qualified spec (`company.profile`) — resolved by the
rule the server uses. What is *written* is always the qualified form, since it
is unambiguous under either name style. A bare key claimed by two clients is
reported as an ambiguity naming both candidates, not as "unknown"; an entry
naming nothing at all is still reported as unknown and skipped.

> **Changed in this release.** If **nothing** in an explicit `--tools`
> selection resolves, `generate` now writes no file and exits non-zero, naming
> each failed entry and why. It previously wrote `TOOLS = []` and exited 0.
> A single bad entry among good ones is still just a warning.
>
> This holds **whether or not `--no-defaults` is passed**. The default tools
> are not an answer to an ask that named only tools which do not exist, so
> they no longer top up an otherwise-empty selection and turn the failure
> into a success.
>
> **Also changed:** if an explicit `--tools` selection contains both sides of
> a name collision, `generate` writes no file and exits non-zero under the
> default `FMP_MCP_TOOL_NAME_STYLE=key`, because that pair cannot register.
> Neither side is silently dropped — drop one yourself, or set
> `FMP_MCP_TOOL_NAME_STYLE=spec`, under which both are advertised at their
> full spec and the manifest is written. `generate` and `validate` reach the
> same verdict under either style, so `generate && validate` no longer fails
> on a file `generate` just reported as successfully written.

With no `--tools` filter the generated manifest covers the catalog except for
what would stop it starting a *useful* server: tool keys FMP no longer serves
(they return no data on every call), deprecated tool keys (removed in 3.0),
and one side of each tool-name collision. Under the default
`FMP_MCP_TOOL_NAME_STYLE=key` a tool is advertised under its bare key, so
`alternative.crypto_quotes` and `batch.crypto_quotes` both want to be called
`crypto_quotes` and registration refuses the pair. Every exclusion is named in
the generated file's header and printed on generation, grouped by reason: a
deprecated key is listed beside the replacement that ships in its place, and a
collision loser beside the `FMP_MCP_TOOL_NAME_STYLE=spec` setting (names become
`<client>.<key>`) that lets you add both sides back.

3. **Discovering available tools** - List all available tools:
```bash
# List all tools in table format
fmp-mcp list

# List as tree structure
fmp-mcp list --format tree

# Filter by client module
fmp-mcp list --client technical

# Export as JSON
fmp-mcp list --format json > tools.json
```

Tip: set `FMP_MCP_TOOL_NAME_STYLE=spec` to expose fully qualified tool names
(`client.key`) and avoid naming collisions when multiple tools share a key.

> **Changed in this release — `list` output shape.** Every format now emits
> the **fully qualified spec** (`company.profile`), not the bare key, so what
> you read can be pasted straight into a manifest or `--tools` without
> guessing which client owns it. Previously the table and tree showed bare
> keys, which are ambiguous for `crypto_quotes` and `forex_quotes` — the two
> keys claimed by two clients each — and so could not be copied safely.
> The table also gained a **`Retirement`** column.
>
> This changes output any script parsing `fmp-mcp list` will see. `--format
> json` remains the stable interface for programmatic use.
>
> One rough edge: at an 80-column terminal the table wraps a long spec across
> two lines rather than truncating it. Nothing is lost and the specs remain
> distinguishable, but a spec that wraps is not directly copy-pasteable — use
> `--format json`, or a wider terminal, if you are copying.

> **Reading the `Retirement` column.** Three different things can be true of
> a tool key, and they are labelled apart because each asks something
> different of you:
>
> | Label | Meaning | What to do |
> |---|---|---|
> | *(blank)* | Live tool. | Nothing. |
> | `DEPRECATED -> other.spec` | A second **name** for a method that still serves real data. Stops resolving in 3.0. | Swap the name; the replacement is a drop-in. |
> | `WITHDRAWN, nearest live tool other.spec` | FMP no longer serves this endpoint. It resolves and registers, but can only ever answer `[]`. | Move to the named tool — and check its fields, the payload differs. |
> | `WITHDRAWN, no replacement` | Same, and FMP publishes nothing equivalent. | Drop the tool. |
>
> In `--format json` these are three fields: `deprecated` (the replacement
> spec, or `null`), `withdrawn` (boolean) and `successor` (the nearest live
> spec for a withdrawal, or `null`). `deprecated` keeps the meaning it has
> always had — withdrawals are **not** folded into it.

### Bare keys vs. fully qualified specs

A manifest entry may be the bare tool key (`profile`) or the fully qualified
spec (`company.profile`). A bare key resolves **only when exactly one client
claims it**. Two keys are claimed by two clients each — `crypto_quotes` and
`forex_quotes`, by `alternative` and `batch` — and must be written in full:

```python
TOOLS = [
    "alternative.crypto_quotes",  # not "crypto_quotes"
    "batch.forex_quotes",  # not "forex_quotes"
]
```

Using the bare form for either raises at registration with an error naming
every candidate.

Naming **both** halves of a colliding pair is a separate failure. Under the
default `FMP_MCP_TOOL_NAME_STYLE=key`, the advertised tool name is just the
key, so `alternative.crypto_quotes` and `batch.crypto_quotes` in one manifest
both want to be called `crypto_quotes` and registration is refused. To expose
both at once, set `FMP_MCP_TOOL_NAME_STYLE=spec` (see the tip above) so each
tool is advertised under its fully qualified name.

## Validation

Validate your manifest file before using:
```bash
fmp-mcp validate my_manifest.py
```

**The exit code is the verdict, and it means "this manifest can start a
server".** `validate` exits non-zero for exactly the four things
`register_from_manifest` refuses:

| Finding | Exit code | Why |
|---|---|---|
| unknown entry (`company.profil`) | non-zero | resolves to nothing |
| ambiguous bare key (`crypto_quotes`) | non-zero | claimed by two clients |
| the same tool listed twice (`profile` **and** `company.profile`) | non-zero | one tool, two entries; no name style separates them |
| two tools claiming one advertised name | non-zero | only under the default `FMP_MCP_TOOL_NAME_STYLE=key`; set `spec` and this stops being a clash |
| deprecated entry | **0** | still resolves; the migration table prints |
| withdrawn entry | **0** | still registers, answers with no data; reported |
| `TOOLS = []` | **0** | an empty manifest starts a server with no tools — useless, but not broken, and `validate`'s verdict is "can this start a server". `generate` nonetheless *refuses to write* one, because there the emptiness is a failed ask with named reasons |

Clashes are judged under the `FMP_MCP_TOOL_NAME_STYLE` in effect, so validating
with the variable your server runs with is what you want.

> **Changed in this release.** `validate` previously printed its warnings and
> then exited 0 regardless, so a manifest with a typo passed CI and failed at
> server start. If you have `fmp-mcp validate` in a pipeline, a manifest with
> any of the fatal findings above will now fail that build — which is the point,
> but it may fail on first upgrade.

## Tips

- Start with `minimal_manifest.py` and add tools as needed
- Group related tools together with comments
- Test your configuration with a simple query before deployment
- Consider API rate limits when selecting tools
- Use `research_manifest.py` for comprehensive analysis
- Use `trading_manifest.py` for real-time market monitoring
