"""Run Office over stdio or Streamable HTTP."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Office MCP server")
    parser.add_argument("--transport", choices=("stdio", "streamable-http"), default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    from office_mcp.app import mcp

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        if args.host not in {"127.0.0.1", "::1", "localhost"}:
            parser.error(
                "the bundled HTTP launcher is loopback-only; remote deployment requires "
                "authenticated request-scope, store, and subscription adapters"
            )
        mcp.run(transport="streamable-http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
