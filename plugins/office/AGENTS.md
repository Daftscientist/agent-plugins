# Office implementation rules

1. Read `DESIGN.md` completely before changing Office architecture.
2. Inspect current domOXML, Agent Plugins, and official MCP Python SDK v2 APIs; never guess.
3. Use `mcp.server.MCPServer`; never use FastMCP v1.
4. Expose HTML with inline CSS, never OOXML or shape micro-tools.
5. Reject active content and caller-controlled `data-office-id` values.
6. Use opaque IDs and hidden request scope for every store and protocol operation.
7. Preserve domOXML warnings, preservation data, and coverage debt.
8. Keep MCP handlers thin and domain/storage/domOXML concerns independently testable.
9. Never require model filesystem access or enable local/network input by default.
10. Run `ruff check`, `ruff format --check`, `pyright`, and `pytest` before pushing.
