# MCP Integration

FMP Data ships an MCP server for Claude Desktop and other MCP clients.
The MCP tool catalog covers endpoints with MCP tool semantics; for full endpoint
coverage, use the Python client.

Tool naming defaults to semantic keys (e.g., `profile`). For collision-free tool
names, set `FMP_MCP_TOOL_NAME_STYLE=spec` to expose fully qualified names like
`company.profile`.

## Tool argument names (MCP vs LangChain)

MCP tools advertise the **Python client method** parameter names — the same
names you pass to `client.company.get_profile(...)`,
`client.sec.search_filings_by_symbol(from_date=..., to_date=...)`, and so on.
That matches how the MCP loader resolves `client.<module>.<method>` and builds
the tool schema from `inspect.signature`.

LangChain tools built from `EndpointVectorStore` keep the **HTTP / wire** names
from the endpoint declaration (`from`, `to`, `periodLength`, …) and map them
onto method parameters at invoke time. The two integrations therefore may show
different argument names for the same endpoint; both are correct for their
dispatch path. See the LangChain section of the project README and #188.

## Guides

- Setup for Claude Desktop: [Claude Desktop Setup](claude_desktop.md)
- Configuration profiles and manifests: [Configuration Profiles](configurations.md)
- Troubleshooting: [Troubleshooting](troubleshooting.md)
- Tools reference: [Tools Reference](tools.md)
