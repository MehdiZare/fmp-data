# MCP Integration

FMP Data ships an MCP server for Claude Desktop and other MCP clients.
The MCP tool catalog covers endpoints with MCP tool semantics; for full endpoint
coverage, use the Python client.

Tool naming defaults to semantic keys (e.g., `profile`). For collision-free tool
names, set `FMP_MCP_TOOL_NAME_STYLE=spec` to expose fully qualified names like
`company.profile`.

## Guides

- Setup for Claude Desktop: [Claude Desktop Setup](claude_desktop.md)
- Configuration profiles and manifests: [Configuration Profiles](configurations.md)
- Troubleshooting: [Troubleshooting](troubleshooting.md)
- Tools reference: [Tools Reference](tools.md)
