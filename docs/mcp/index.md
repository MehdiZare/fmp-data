# MCP Integration

FMP Data ships **`fmp-mcp`**, a local MCP server for Claude Desktop and other
MCP clients. The MCP tool catalog covers endpoints with MCP tool semantics;
for full endpoint coverage, use the Python client.

FMP also hosts their own remote MCP server. That is a different product.
See [FMP hosted MCP vs `fmp-mcp`](hosted.md) for when to use which
(decision recorded in [#230](https://github.com/MehdiZare/fmp-data/issues/230)).

Tool naming defaults to semantic keys (e.g., `profile`). For collision-free tool
names, set `FMP_MCP_TOOL_NAME_STYLE=spec` to expose fully qualified names like
`company.profile`.

## Tool argument names (MCP vs LangChain)

MCP tools advertise the **Python client method** parameter names — the same
names you pass to `client.company.get_profile(...)`,
`client.sec.search_by_symbol(symbol=..., from_date=..., to_date=...)`, and so
on. The MCP loader resolves `client.<module>.<method>` and registers that
callable; the MCP framework advertises its Python signature as the tool schema.

LangChain tools built from `EndpointVectorStore` keep the **HTTP / wire** names
from the endpoint declaration (`from`, `to`, `periodLength`, …) and, when the
method shape is compatible, map them onto method parameters at invoke time.
The two integrations therefore may show different argument names for the same
endpoint (e.g. `from`/`to` on LangChain vs `from_date`/`to_date` or
`start_date`/`end_date` on MCP) — both are intentional.

If a required method parameter had no wire source, LangChain would keep the
wire schema and fall back to `client.request` instead of the method. No tool in
the catalog does that today: the institutional Form 13F and
symbol-positions-summary tools were the last exception, and since #188 they
dispatch through `get_form_13f_by_quarter` /
`get_institutional_holdings_by_quarter`, whose `year`/`quarter` arguments are
what the API itself requires. Both MCP and LangChain therefore advertise
`cik`/`symbol` + `year` + `quarter` for those tools; the date-shaped
`get_form_13f(cik, report_date)` remains available to Python callers.
`tests/unit/lc/test_endpoint_method_coverage.py` fails CI if a new mismatch
appears. See the LangChain section of the project README and #188.

Both integrations resolve and bind through `fmp_data.tool_binding`, a core
module with no LangChain or MCP dependency: attribute-chain resolution, the
wire→method name aliases, the required-parameter coverage gate and the
invoke-time kwargs mapping all live there, so the two cannot drift apart. What
still differs between them is only what each *advertises* — method parameter
names on MCP, wire names on LangChain.

## Guides

- Setup for Claude Desktop: [Claude Desktop Setup](claude_desktop.md)
- Configuration profiles and manifests: [Configuration Profiles](configurations.md)
- Troubleshooting: [Troubleshooting](troubleshooting.md)
- Tools reference: [Tools Reference](tools.md)
- FMP hosted MCP vs this package: [Hosted MCP](hosted.md)
