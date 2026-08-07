# Office MCP server

This directory contains the typed Python MCP 2.0 server used by the Office Agent Plugin. It is an implementation detail of the self-contained plugin in the parent directory; clients should launch it through `mcp.json`.

## Development

Python 3.12 and [uv](https://docs.astral.sh/uv/) are required.

```bash
uv sync --frozen --extra dev
uv run playwright install chromium
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv build
```

Run the local stdio server with `uv run python -m office_mcp`. The bundled streamable-HTTP launcher is restricted to loopback; remote deployment must inject authenticated request scope, tenant-safe storage/output adapters, transport authorization, and a shared subscription bus through `create_server`.

The server keeps MCP protocol handlers, presentation-domain logic, scoped storage, input/output boundaries, and the domOXML adapter separately testable. domOXML is pinned to an exact commit in `uv.lock` and `pyproject.toml`.
